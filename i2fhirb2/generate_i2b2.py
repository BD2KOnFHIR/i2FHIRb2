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
from typing import Optional, List, Dict, Any

from rdflib import Graph, URIRef
from sqlalchemy import delete, Table, Column
from sqlalchemy.engine import Engine

from i2fhirb2.fhir.fhirconceptdimension import FHIRConceptDimension
from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimension
from i2fhirb2.i2b2model.i2b2conceptdimension import ConceptDimensionRoot
from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension
from i2fhirb2.i2b2model.i2b2ontology import OntologyEntry, OntologyRoot
from i2fhirb2.i2b2model.i2b2tableaccess import TableAccess
from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables


def pluralize(cnt: int, base: Any) -> str:
    """
    Pluralize base based on the number in cnt
    :param cnt: number of elements
    :param base: base word
    :return: plural
    """
    return str(base) + ('s' if cnt != 1 else '')


def esc_output(txt: str) -> str:
    """
    Escape carriage returns for tsv output
    :param txt:
    :return:
    """
    return txt.replace('\r\n', '').replace('\r', '').replace('\n', '')


def generate_output(g: Graph, o: FHIRMetadata, opts: Namespace, resource: Optional[URIRef], file: str) -> bool:
    v = o.dimension_list(resource)
    return write_tsv(opts, file, o.tsv_header(), v)


def write_tsv(opts: Namespace, file: str, hdr: str, values: List[object]) -> bool:
    with open(opts.outdir + file + ('.tsv' if '.' not in file else ''), 'w') as outf:
        outf.write(hdr + '\n')
        for e in sorted(values):
            outf.write(esc_output(repr(e)) + '\n')
    return True


Default_Sourcesystem_Code = 'FHIR STU3'
Default_Base = 'FHIR'
Default_Path_Base = '\\{}\\'.format(Default_Base)


def generate_i2b2_files(g: Graph, opts: Namespace) -> bool:
    return ((opts.table and opts.table != 'table_access') or generate_table_access(opts)) and \
           ((opts.table and opts.table != 'concept_dimension') or generate_concept_dimension(g, opts)) and \
           ((opts.table and opts.table != 'modifier_dimension') or generate_modifier_dimension(g, opts)) and \
           ((opts.table and opts.table != 'ontology') or generate_ontology(g, opts))


def generate_table_access(opts: Namespace) -> bool:
    table_access = TableAccess()
    if opts.outdir:
        return write_tsv(opts, 'table_access', table_access._header(), [table_access])
    else:
        return update_table_access_table(opts, opts.tables.table_access, [table_access._freeze()])


def update_table_access_table(opts: Namespace, table: Table, records: List[Dict[str, Any]]) -> bool:
    ndel = opts.tables.connection.execute(delete(table).where(table.c.c_table_cd == Default_Base)).rowcount
    if ndel > 0:
        print("{} {} {} deleted".format(ndel, table, pluralize(ndel, "record")))
    nins = opts.tables.connection.execute(table.insert(), records).rowcount
    print("{} {} {} inserted".format(nins, table, pluralize(nins, "record")))
    return True


def generate_concept_dimension(g: Graph, opts: Namespace) -> bool:
    resource = FHIR[opts.resource] if opts.resource else None

    ConceptDimension._clear()
    ConceptDimension.sourcesystem_cd = opts.sourcesystem
    ConceptDimension.update_date = opts.updatedate

    ConceptDimensionRoot._clear()
    ConceptDimensionRoot.sourcesystem_cd = opts.sourcesystem
    ConceptDimensionRoot.update_date = opts.updatedate

    if opts.outdir:
        return generate_output(g, FHIRConceptDimension(g, name_base=opts.base), opts, resource, "concept_dimension")
    else:
        table = opts.tables.concept_dimension
        change_column_length(table, table.c.concept_cd, 200, opts.tables.engine)
        return update_dimension_table(FHIRConceptDimension(g, name_base=opts.base), opts, table,
                                      'concept_path', [opts.base], resource)


def update_dimension_table(fo: FHIRMetadata, opts: Namespace, table: Table, table_key: str,
                           key_match: List[str], resource: Optional[URIRef]) -> bool:
    for km in key_match:
        q = delete(table).where(table.c[table_key].startswith(km.replace('\\', '\\\\')))
        ndel = opts.tables.connection.execute(q).rowcount
        if ndel > 0:
            print("{} {} {} deleted".format(ndel, table, pluralize(ndel, "record")))
    nins = opts.tables.connection.execute(table.insert(), [e._freeze() for e in fo.dimension_list(resource)]).rowcount
    print("{} {} {} inserted".format(nins, table, pluralize(nins, "record")))
    return True


def change_column_length(table: Table, column: Column, length: int, engine: Engine) -> None:
    if column.type.length < length or True:
        print("Changing length of {} from {} to {}".format(column, column.type.length, length))
        column.type.length = length
        column_name = column.name
        column_type = column.type.compile(engine.dialect)
        engine.execute('ALTER TABLE {table} ALTER COLUMN {column_name} TYPE {column_type}'.format(**locals()))


def generate_modifier_dimension(g: Graph, opts: Namespace) -> bool:
    resource = URIRef(opts.resource) if opts.resource else None

    ModifierDimension._clear()
    ModifierDimension.sourcesystem_cd = opts.sourcesystem
    ModifierDimension.update_date = opts.updatedate

    if opts.outdir:
        return generate_output(g, FHIRModifierDimension(g, name_base=opts.base), opts, resource, "modifier_dimension")
    else:
        table = opts.tables.modifier_dimension
        change_column_length(table, table.c.modifier_cd, 200, opts.tables.engine)
        return update_dimension_table(FHIRModifierDimension(g, name_base=opts.base), opts, table,
                                      'modifier_path', [opts.base], resource)


def generate_ontology(g: Graph, opts: Namespace) -> bool:
    resource = URIRef(opts.resource) if opts.resource else None

    OntologyEntry._clear()
    OntologyEntry.sourcesystem_cd = opts.sourcesystem
    OntologyEntry.update_date = opts.updatedate

    OntologyRoot._clear()
    OntologyRoot.sourcesystem_cd = opts.sourcesystem
    OntologyRoot.update_date = opts.updatedate

    if opts.outdir:
        return generate_output(g, FHIROntologyTable(g, name_base=opts.base), opts, resource, "ontology")
    else:
        table = opts.tables.custom_meta
        change_column_length(table, table.c.c_basecode, 200, opts.tables.engine)
        change_column_length(table, table.c.c_tooltip, 1600, opts.tables.engine)    # MedicationStatement is 1547 long
        return update_dimension_table(FHIROntologyTable(g, name_base=opts.base), opts, table, 'c_basecode',
                                      [opts.base.replace('\\', '') + ':', 'W5'], resource)


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
    parser.add_argument("-o", "--outdir", help="Output directory to store .tsv files")
    parser.add_argument("-t", "--table", help="Table to update (e.g. concept_dimension) - default is all tables")
    parser.add_argument("-r", "--resource",
                        help="Name of specific resource to emit (e.g. Observation) - default is all")
    parser.add_argument("-s", "--sourcesystem",
                        default=Default_Sourcesystem_Code,
                        help="sourcesystem code. Default: 'F{}'".format(Default_Sourcesystem_Code))
    parser.add_argument("-b", "--base",
                        default=Default_Path_Base,
                        help="Concept dimension and ontology base path. Default:{}".format(Default_Path_Base))
    parser.add_argument("-l", "--load", help="Load i2b2 SQL tables", action="store_true")
    return parser


def generate_i2b2(argv) -> bool:
    opts = genargs().parse_args(argv)
    opts.updatedate = datetime.now()
    if not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if opts.outdir and not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    opts.tables = I2B2Tables() if opts.load else None
    g = load_fhir_ontology(opts)
    return g is not None and generate_i2b2_files(g, opts)
