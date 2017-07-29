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
from argparse import Namespace, ArgumentParser
from typing import List, Union

import sys

import dirlistproc
from rdflib import Graph

from i2fhirb2.loaders.fhircollectionloader import FHIRCollection
from i2fhirb2.loaders.fhirresourceloader import FHIRResource

dirname, _ = os.path.split(os.path.abspath(__file__))

DEFAULT_FHIR_URI = "http://hl7.org/fhir/"
DEFAULT_RDF_DIR = "rdf"
DEFAULT_FHIR_MV = os.path.join(dirname, '..', 'tests', 'data', 'fhir_metadata_vocabulary', 'fhir.ttl')


def load_fhir_ontology(opts: Namespace) -> Graph:
    g = Graph()
    print("Loading FHIR metadata vocabulary")
    g.load(opts.metadatavoc, format="turtle")
    return g


class ArgParser(ArgumentParser):
    def add_argument(self, *args, **kwargs):
        defhelp = kwargs.pop("help", None)
        default = kwargs.pop("default", None)
        if not defhelp or default is None:
            return super().add_argument(*args, help=defhelp, default=default, **kwargs)
        else:
            return super().add_argument(*args, help=defhelp + " (default: {})".format(default),
                                        default=default, **kwargs)


def proc_file(infile: str, outfile: str, opts: Namespace) -> bool:
    json_obj = FHIRResource.load_file_or_uri(infile)

    if 'resourceType' not in json_obj:
        if 'entry' in json_obj:
            coll = FHIRCollection(opts.fhir_metavoc,
                                  None,
                                  opts.uribase,
                                  data=json_obj,
                                  add_ontology_header=not opts.noontology,
                                  replace_narrative_text=opts.nonarrative)
    else:
        res = FHIRResource(opts.fhir_metavoc,
                           opts.jsonuri,
                           opts.uribase,
                           add_ontology_header=not opts.noontology,
                           replace_narrative_text=opts.nonarrative)
        res.

    return None

skip_dir_names = ['/v2/', '/v3/']
skip_file_names = ['.cs.', '.vs.', '.profile.', '.canonical.', '.schema.', '.diff.']


def file_filter(ifn: str, indir: str, opts: Namespace) -> bool:
    """
    Determine whether to process ifn.  We con't process:
        1) Anything in a directory having a path element that begins with "_"
        2) Really, really big files
        3) Temporary lists of know errors
    :param ifn: input file name
    :param indir: input directory
    :param opts: argparse options
    :return: True if to be processed, false if to be skipped
    """
    if indir.startswith("_") or "/_" in indir or any(dn in indir for dn in skip_dir_names):
        return False

    if any(sfn in ifn for sfn in skip_file_names):
        return False

    infile = os.path.join(indir, ifn)
    if os.path.getsize(infile) > (opts.maxsize * 1000):
        return False

    return True


def addargs(parser: ArgumentParser) -> None:
    parser.add_argument("-u", "--uribase", help="Base URI for RDF identifiers", default=DEFAULT_FHIR_URI)
    parser.add_argument("-mv", "--metadatavoc", help="FHIR metadata vocabulary", default=DEFAULT_FHIR_MV)
    parser.add_argument("-no", "--noontology", help="Omit owl ontology header", action="store_true")
    parser.add_argument("-nn", "--nonarrative", help="Omit narrative text on output", action="store_true")
    parser.add_argument("--maxsize", help="Maximum sensible file size in KB", type=int, default=800)
    parser.fromfile_prefix_chars = "@"


def postparse(opts: Namespace) -> None:
    opts.graph = Graph()
    opts.fhir_metavoc = load_fhir_ontology(opts)


def printjsontordf(argv: List[str]) -> bool:
    """ Entry point for command line utility """
    dlp = dirlistproc.DirectoryListProcessor(argv, description="Convert FHIR JSON into RDF", infile_suffix=".json",
                                             outfile_suffix=".ttl", addargs=addargs, postparse=postparse)
    dlp.run(file_filter=file_filter)

    # rdf = jsontordf(argv)
    # if rdf is not None:
    #     print(str(rdf))
    # return rdf is not None


if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), '..'))
    printjsontordf(sys.argv[1:])