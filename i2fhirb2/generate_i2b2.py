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
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import Optional, List

from rdflib import Graph, URIRef

from i2fhirb2.fhir.fhirontology import FHIRConceptDimension
from i2fhirb2.fhir.fhirontology import FHIROntology, FHIRModifierDimension, FHIROntologyTable
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimensionRoot
from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry, OntologyRoot
from i2fhirb2.i2b2model.i2b2tableaccess import TableAccess


def esc_output(txt: str) -> str:
    return txt.replace('\r\n', '').replace('\r', '').replace('\n', '')


def generate_output(g: Graph, o: FHIROntology, opts: Namespace, resource: Optional[URIRef], file: str) -> bool:
    o += g
    v = o.dimension_list(resource)
    return write_tsv(opts, file, o.tsv_header(), v)


def write_tsv(opts: Namespace, file: str, hdr: str, values: List[object]) -> bool:
    with open(opts.outdir + file + ('.tsv' if '.' not in file else ''), 'w') as outf:
        outf.write(hdr + '\n')
        for e in sorted(values):
            outf.write(esc_output(repr(e)) + '\n')
    return True


Default_Sourcesystem_Code = 'FHIR STU3'
Default_Path_Base = '\\FHIR\\'


def generate_i2b2_files(g: Graph, opts: Namespace) -> bool:
    return generate_table_access(opts) and \
           generate_concept_dimension(g, opts) and \
           generate_modifier_dimension(g, opts) and \
           generate_ontology(g, opts)


def generate_table_access(opts: Namespace) -> bool:
    table_access = TableAccess()
    return write_tsv(opts, 'table_access', table_access._header(), [table_access])


def generate_concept_dimension(g: Graph, opts: Namespace) -> bool:
    resource = URIRef(opts.resource) if opts.resource else None

    ConceptDimension._clear()
    ConceptDimension.sourcesystem_cd = opts.sourcesystem
    ConceptDimension.update_date = opts.updatedate

    ConceptDimensionRoot._clear()
    ConceptDimensionRoot.sourcesystem_cd = opts.sourcesystem
    ConceptDimensionRoot.update_date = opts.updatedate

    return generate_output(g, FHIRConceptDimension(name_base=opts.base), opts, resource, "concept_dimension")


def generate_modifier_dimension(g: Graph, opts: Namespace) -> bool:
    resource = URIRef(opts.resource) if opts.resource else None

    ModifierDimension._clear()
    ModifierDimension.sourcesystem_cd = opts.sourcesystem
    ModifierDimension.update_date = opts.updatedate

    return generate_output(g, FHIRModifierDimension(name_base=opts.base), opts, resource, "modifier_dimension")


def generate_ontology(g: Graph, opts: Namespace) -> bool:
    resource = URIRef(opts.resource) if opts.resource else None

    OntologyEntry._clear()
    OntologyEntry.sourcesystem_cd = opts.sourcesystem
    OntologyEntry.update_date = opts.updatedate

    OntologyRoot._clear()
    OntologyRoot.sourcesystem_cd = opts.sourcesystem
    OntologyRoot.update_date = opts.updatedate

    return generate_output(g, FHIROntologyTable(name_base=opts.base), opts, resource, "ontology")


def load_fhir_ontology(opts: Namespace) -> Optional[Graph]:
    g = Graph()
    print("Loading fhir.ttl")
    g.load(opts.indir + "fhir.ttl", format="turtle")
    print("loading w5.ttl")
    g.load(opts.indir + "w5.ttl", format="turtle")
    return g


def genargs() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgumentParser(description="FHIR in i2b2 generator")
    parser.add_argument("indir", help="Input directory or URI of w5.ttl and fhir.ttl files")
    parser.add_argument("outdir", help="Output directory to store .tsv files")
    parser.add_argument("-r", "--resource",
                        help="Name of specific resource to emit (e.g. Observation) - default is all")
    parser.add_argument("-s", "--sourcesystem",
                        default=Default_Sourcesystem_Code,
                        help="sourcesystem code. Default: 'F{}'".format(Default_Sourcesystem_Code))
    parser.add_argument("-b", "--base",
                        default=Default_Path_Base,
                        help="Concept dimension and ontology base path. Default:{}".format(Default_Path_Base))
    return parser


def generate_i2b2(argv) -> bool:
    opts = genargs().parse_args(argv)
    opts.updatedate = datetime.now()
    if not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    g = load_fhir_ontology(opts)
    return g is not None and generate_i2b2_files(g, opts)
