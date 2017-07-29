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
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import List, Optional

from rdflib import Graph

from i2fhirb2.fhir.fhirspecific import DEFAULT_FMV, FHIR, DEFAULT_PROVIDER_ID
from i2fhirb2.generate_i2b2 import Default_Sourcesystem_Code, Default_Path_Base
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact

from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension
from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping
from i2fhirb2.i2b2model.shared.i2b2core import I2B2_Core_With_Upload_Id
from i2fhirb2.loaders.fhirjsonloader import fhir_json_to_rdf


from i2fhirb2.loaders.i2b2graphmap import I2B2GraphMap
from i2fhirb2.sqlsupport.db_connection import add_connection_args, process_parsed_args
from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables


def load_rdf_graph(opts: Namespace) -> Optional[Graph]:
    """
    Load the file(s) specified by opts into an RDF graph
    :param opts: User supplied option
    :return: Loaded graph or None if errors were encountered
    """
    g = Graph()

    def load_file(dirname, fname):
        filepath = os.path.join(dirname, fname)
        print("--> loading {}".format(filepath))
        if opts.filetype == 'rdf':
            g.load(filepath, format="turtle")
        else:
            fmv = Graph()
            fmv.load(opts.metavoc, format="turtle")
            fhir_json_to_rdf(fmv, filepath, opts.uribase, g)

    if opts.file:
        load_file(opts.indir if opts.indir else "", opts.file)
    else:
        for dirpath, _, filenames in os.walk(opts.indir):
            for filename in filenames:
                if filename.endswith(opts.file_suffix):
                    load_file(dirpath, filename)

    return g


def create_parser() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    # TODO: figure out how to split out the db connection arguments so we can reuse them
    parser = ArgumentParser(description="Load FHIR Resource Data into i2b2 CRC tables", fromfile_prefix_chars='@')
    parser.add_argument("-f", "--file", metavar="Input file", help="URL or name of input file")
    parser.add_argument("-d", "--indir", metavar="Input directory", help="URI of server or directory of input files")
    parser.add_argument("-o", "--outdir", metavar="Output directory", help="Output directory to store .tsv files. "
                                                  "If not specified, no .tsv files are generated.")
    parser.add_argument("-t", "--filetype", help="Type of files to load. Default: json", choices=['rdf', 'json'])
    parser.add_argument("-mv", "--metavoc", help="Name of FHIR Metavocabulary file (default: {}".format(DEFAULT_FMV),
                        default=DEFAULT_FMV)
    parser.add_argument("--sourcesystem", metavar="Source system code",
                        default=Default_Sourcesystem_Code,
                        help="Sourcesystem code.  (default: \"{}\")".format(Default_Sourcesystem_Code))
    parser.add_argument("-u", "--uploadid", metavar="Upload identifier",
                        help="Upload identifer -- uniquely identifies this batch", type=int,
                        required=True)
    parser.add_argument("--base", metavar="concept identifier base (default: {})".format(Default_Path_Base),
                        default=Default_Path_Base,
                        help="Concept dimension and ontology base path. (default:\"{}\")".format(Default_Path_Base))
    parser.add_argument("-ub", "--uribase", help="Resource URI base. Default: {}".format(FHIR), default=str(FHIR))
    parser.add_argument("-l", "--load", help="Load i2b2 SQL tables", action="store_true")
    parser.add_argument("-rm", "--remove", help="Remove existing entries for the upload identifier and/or"
                                                " clear target tsv files", action="store_true")
    parser.add_argument("-p", "--providerid", metavar="Default provider id",
                        help="Default provider id (default: {})".format(DEFAULT_PROVIDER_ID),
                        default=DEFAULT_PROVIDER_ID)
    return parser


def genargs(argv: List[str]) -> Optional[Namespace]:
    """
    Parse the input arguments and create the options list
    :param argv: input arguments
    :return: options if success or None of parameters aren't valid
    """
    opts = add_connection_args(create_parser()).parse_args(argv)
    if not (opts.file or opts.indir):
        print("Either an input file or input directory must be supplied", file=sys.stderr)
        return None
    if opts.remove and not opts.load:
        print("Remove existing option not yet implemented for tsv files")
        return None
    if opts.file and not opts.filetype:
        if opts.file.endswith(".json"):
            opts.filetype = "json"
        elif opts.file.endswith(".ttl"):
            opts.filetype = "ttl"
        else:
            print("Unable to determine file type from input file name")
            return None
    if (opts.file and opts.file.endswith('.ttl') and opts.filetype == "json") or \
            (opts.file and opts.file.endswith('.json') and opts.filetype == "rdf"):
        print("Supplied file type ({}) doesnt match file suffix ({})"
              .format(opts.filetype, opts.file.rsplit('.', 1)[1]))
        return None
    if opts.indir and not opts.filetype:
        opts.filetype = "json"

    opts.file_suffix = ".json" if opts.filetype == "json" else '.ttl' if opts.filetype == "rdf" else "."

    opts.updatedate = datetime.now()
    if opts.indir and not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if opts.outdir and not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    opts.updatedate = datetime.now()
    if opts.load:
        process_parsed_args(opts)

    if opts.sourcesystem:
        I2B2_Core_With_Upload_Id.sourcesystem_cd = opts.sourcesystem
        # TODO: make sure this works
        # PatientDimension.sourcesystem_cd = opts.sourcesystem
        # PatientMapping.sourcesystem_cd = opts.sourcesystem
        # ObservationFact.sourcesystem_cd = opts.sourcesystem
        # VisitDimension.sourcesystem_cd = opts.sourcesystem
        # EncounterMapping.sourcesystem_cd = opts.sourcesystem
    I2B2_Core_With_Upload_Id.upload_id = opts.uploadid
    # PatientMapping.upload_id = opts.uploadid
    # PatientDimension.upload_id = opts.uploadid
    # ObservationFact.upload_id = opts.uploadid
    # VisitDimension.upload_id = opts.uploadid
    # EncounterMapping.upload_id = opts.uploadid

    return opts


def print_rdf_summary(g: Graph()) -> None:
    # num_resources = len(list(g.subject_objects(FHIR.resourceType)))
    num_triples = len(g)
    print("Loaded ??? resources creating {} triples (Unable to determine how many...)".format(num_triples))


def load_graph_map(opts: Namespace) -> Optional[I2B2GraphMap]:
    opts.tables = I2B2Tables(opts) if opts.load else None
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


def populate_fact_table(argv: List[str]) -> bool:
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
                i2b2_map.load_i2b2_tables()
            return True


if __name__ == "__main__":
    populate_fact_table(sys.argv[1:])
