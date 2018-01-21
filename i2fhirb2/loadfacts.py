# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import sys
from argparse import Namespace
from datetime import datetime
from random import randint
from typing import List, Optional
from urllib.request import Request, urlopen
from i2fhirb2 import __version__

from fhirtordf.fhir.fhirmetavoc import FHIRMetaVoc
from fhirtordf.loaders.fhirjsonloader import fhir_json_to_rdf
from rdflib import Graph

from i2fhirb2.common_cli_parameters import add_common_parameters
from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact

from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension
from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping
from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId


from i2fhirb2.loaders.i2b2graphmap import I2B2GraphMap
from i2fhirb2.sqlsupport.dbconnection import add_connection_args, process_parsed_args, I2B2Tables
from i2fhirb2.file_aware_parser import FileAwareParser


# TODO: Add support for non-turtle RDF files
# TODO: Add continuation headers for RDF


def load_rdf_graph(opts: Namespace) -> Optional[Graph]:
    """
    Load the file(s) specified by opts into an RDF graph
    :param opts: User supplied option
    :return: Loaded graph or None if errors were encountered
    """
    g = Graph()
    fmv = FHIRMetaVoc(opts.metadatavoc + '/fhir.ttl')

    def read_rdf_uri(uri: str) -> str:
        req = Request(uri)
        req.add_header("Accept", "application/turtle, text/turtle;q=0.9")
        with urlopen(req) as response:
            return response.read().decode()

    def load_file(dirname: str, fname: str) -> None:
        filepath = fname if '://' in fname else os.path.join(dirname, fname)
        print("--> loading {}".format(filepath))
        if '://' in fname:
            if opts.filetype == 'rdf':
                rdf_str = read_rdf_uri(fname)
                if not rdf_str:
                    print("   Read Failed")
                g.parse(data=rdf_str, format="turtle")
            else:
                fhir_json_to_rdf(fname, opts.uribase, g, metavoc=fmv)
        else:
            if filepath.endswith('.json'):
                fhir_json_to_rdf(filepath, opts.uribase, g, metavoc=fmv)
            else:
                g.load(filepath, format="turtle")

    if opts.infile:
        [load_file(opts.indir if opts.indir else "", fn) for fn in opts.infile]
    else:
        for dirpath, _, filenames in os.walk(opts.indir):
            for filename in filenames:
                if (opts.filetype == 'json' and filename.endswith('.json')) or filename.endswith('.ttl'):
                    load_file(dirpath, filename)
    return g


def create_parser() -> FileAwareParser:
    """
    Create a command line argument parser
    :return: parser
    """
    parser = FileAwareParser(description="Load FHIR Resource Data into i2b2 CRC tables", prog="loadfacts")
    parser.add_argument("-l", "--load", help="Load SQL Tables", action="store_true")
    parser.add_file_argument("-i", "--infile",
                             metavar="Input files", help="URLs and/or name(s) of input file(s)", nargs='*')
    parser.add_file_argument("-id", "--indir", metavar="Input directory",
                             help="URI of server or directory of input files")
    parser.add_file_argument("-od", "--outdir", metavar="Output directory",
                             help="Output directory to store .tsv files.")
    parser.add_argument("-t", "--filetype",
                        help="Type of file to ask for / load - only applies for URL's and directories.",
                        choices=['json', 'rdf'], default='rdf')
    parser.add_argument("-rm", "--remove", help="Remove existing entries for the upload identifier and/or"
                        " clear target tsv files", action="store_true")
    parser.add_argument("--dupcheck", help="Check for duplicate records before add.", action="store_true")
    return add_common_parameters(parser)


def genargs(argv: List[str]) -> Optional[Namespace]:
    """
    Parse the input arguments and create the options list
    :param argv: input arguments
    :return: options if success or None of parameters aren't valid
    """
    parser = add_connection_args(create_parser())
    opts = parser.parse_args(parser.decode_file_args(argv))
    if opts.version:
        print("FHIR i2b2 CRC loader -- Version {}".format(__version__))
    elif not (opts.load or opts.outdir):
        parser.error("Either load option (-l) or output directory must be specified")
    if not (opts.infile or opts.indir or opts.version):
        parser.error("Either a list of input files or input directory must be supplied")
    if opts.remove and not opts.load:
        parser.error("Remove existing upload id only implemented for LOAD option")
    if opts.infile:
        for fn in opts.infile:
            if '://' not in fn and not (fn.endswith('.ttl') or fn.endswith(".json")):
                parser.error("Unrecognized file type: {}".format(fn))
    if opts.load or opts.outdir:
        if not opts.uploadid:
            # TODO: find a more rational way to do this
            # TODO: uploadid to description map
            opts.uploadid = randint(200000, 500000)
        opts.updatedate = datetime.now()
        if opts.indir and not opts.indir.endswith(os.sep):
            opts.indir = os.path.join(opts.indir, '')
        if opts.outdir and not opts.outdir.endswith(os.sep):
            opts.outdir = os.path.join(opts.outdir, '')
        if opts.load:
            process_parsed_args(opts, parser.error)
        I2B2CoreWithUploadId.sourcesystem_cd = opts.sourcesystem
        I2B2CoreWithUploadId.upload_id = opts.uploadid
        return opts
    return None


def print_rdf_summary(g: Graph()) -> None:
    """
    Summarize the number of resources and other information that was actually loaded
    :param g: Graph of loaded RDF
    """
    # TODO: Figure out how to count the number of resources
    # num_resources = len(list(g.subject_objects(FHIR.resourceType)))
    num_triples = len(g)
    # print("Loaded ??? resources creating {} triples (Unable to determine how many...)".format(num_triples))
    print("{} triples".format(num_triples))


def load_graph_map(opts: Namespace) -> Optional[I2B2GraphMap]:
    """
    Transform the input URI(s) and/or file(s) into an I2B2GraphMap
    :param opts: input options
    :return: I2B2GraphMap if success otherwise None
    """
    opts.tables = I2B2Tables(opts) if opts.load else None
    print("upload_id: {}".format(opts.uploadid))
    if opts.tables:
        print("  Starting encounter number: {}"
              .format(FHIREncounterMapping.refresh_encounter_number_generator(opts.tables,
                                                                              opts.uploadid if opts.remove else None)))
        print("  Starting patient number: {}"
              .format(FHIRPatientMapping.refresh_patient_number_generator(opts.tables,
                                                                          opts.uploadid if opts.remove else None)))
    g = load_rdf_graph(opts)
    if g:
        update_dt = datetime.now()
        update_dt_coarse = datetime(update_dt.year, update_dt.month, update_dt.day, update_dt.hour, update_dt.minute)
        ObservationFact.update_date = update_dt_coarse
        PatientDimension.update_date = update_dt_coarse
        PatientMapping.update_date = update_dt_coarse
        print_rdf_summary(g)
        return I2B2GraphMap(g, opts)
    return None


def load_facts(argv: List[str]) -> bool:
    """
    Convert a set of FHIR resources into their corresponding i2b2 counterparts.
    :param argv: Command line arguments.  See: create_parser for details
    :return:
    """
    opts = genargs(argv)
    if not opts:
        return False
    else:
        i2b2_map = load_graph_map(opts)
        if not i2b2_map:
            return False
        else:
            print(i2b2_map.summary())
            if opts.outdir:
                i2b2_map.generate_tsv_files()
            if opts.load:
                i2b2_map.load_i2b2_tables(opts.dupcheck)
            return True


if __name__ == "__main__":
    load_facts(sys.argv[1:])
