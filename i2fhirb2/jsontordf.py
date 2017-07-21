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
from typing import List

import sys
from rdflib import Graph

from i2fhirb2.loaders.fhircollectionloader import FHIRCollection
from i2fhirb2.loaders.fhirresourceloader import FHIRResource

dirname, _ = os.path.split(os.path.abspath(__file__))

DEFAULT_FHIR_URI = "http://hl7.org/fhir/"
DEFAULT_RDF_DIR = "rdf"
DEFAULT_FHIR_MV = os.path.join(dirname, '..', 'tests', 'data', 'fhir.ttl')


def load_fhir_ontology(opts: Namespace) -> Graph:
    g = Graph()
    if opts.outdir:
        print("Loading FHIR metadata vocabulary")
    g.load(opts.metadatavoc, format="turtle")
    return g


class ArgParser(ArgumentParser):
    def add_argument(self, *args, **kwargs):
        help = kwargs.pop("help", None)
        default = kwargs.pop("default", None)
        if not help or default is None:
            return super().add_argument(*args, help=help, default=default, **kwargs)
        else:
            return super().add_argument(*args, help=help + " (default: {})".format(default), default=default, **kwargs)


def create_parser() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgParser(description="Convert FHIR JSON into RDF", fromfile_prefix_chars='@')
    parser.add_argument("jsonuri", help="URI or name of JSON source file")
    parser.add_argument("-u", "--uribase", help="Base URI for RDF identifiers", default=DEFAULT_FHIR_URI)
    parser.add_argument("-od", "--outdir", help="RDF output directory.  If omitted, use sys.stdout")
    parser.add_argument("-mv", "--metadatavoc", help="FHIR metadata vocabulary", default=DEFAULT_FHIR_MV)
    parser.add_argument("-no", "--noontology", help="Omit owl ontology header", action="store_true")
    parser.add_argument("-nn", "--nonarrative", help="Omit narrative text on output", action="store_true")
    return parser


def jsontordf(argv: List[str]) -> bool:
    parser = create_parser()
    opts = parser.parse_args(argv)
    mvg = load_fhir_ontology(opts)
    json_obj = FHIRResource.load_file_or_uri(opts.jsonuri)
    # Try to guess how the JSON is assembled
    if 'resourceType' not in json_obj:
        if 'entry' in json_obj:
            rdf = FHIRCollection(mvg, None, opts.uribase, data=json_obj, add_ontology_header=not opts.noontology,
                  replace_narrative_text=opts.nonarrative )
    else:
        rdf = FHIRResource(mvg, opts.jsonuri, opts.uribase, add_ontology_header=not opts.noontology,
                           replace_narrative_text=opts.nonarrative)
    print(str(rdf))
    return True
