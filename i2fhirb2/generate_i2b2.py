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
from argparse import ArgumentParser, Namespace, Action
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from rdflib import Graph, URIRef
from sqlalchemy import delete, Table, Column, table, update
from sqlalchemy.engine import Engine

from i2fhirb2 import __version__
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
from i2fhirb2.i2b2model.tablenames import i2b2table
from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables

Default_Sourcesystem_Code = 'FHIR STU3'
Default_Base = 'FHIR'
Default_Path_Base = '\\{}\\'.format(Default_Base)
Default_Ontology_TableName = "custom_meta"


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


def generate_output(o: FHIRMetadata, opts: Namespace, resource: Optional[URIRef], file: str) -> bool:
    v = o.dimension_list(resource)
    return write_tsv(opts, file, o.tsv_header(), v)


def write_tsv(opts: Namespace, file: str, hdr: str, values: List[object]) -> bool:
    ofn = opts.outdir + file + ('.tsv' if '.' not in file else '')
    print("writing {}".format(ofn))
    with open(ofn, 'w') as outf:
        outf.write(hdr + '\n')
        for e in sorted(values):
            outf.write(esc_output(repr(e)) + '\n')
    return True


def generate_i2b2_files(g: Graph, opts: Namespace) -> bool:
    return ((opts.table and opts.table != i2b2table.table_access) or generate_table_access(opts)) and \
           ((opts.table and opts.table != i2b2table.concept_dimension) or generate_concept_dimension(g, opts)) and \
           ((opts.table and opts.table != i2b2table.modifier_dimension) or generate_modifier_dimension(g, opts)) and \
           ((opts.table and opts.table != i2b2table.ontology_table) or generate_ontology(g, opts))


def generate_table_access(opts: Namespace) -> bool:
    table_access = TableAccess()
    if opts.outdir:
        return write_tsv(opts, 'table_access', table_access._header(), [table_access])
    else:
        return update_table_access_table(opts, opts.tables.table_access, [table_access._freeze()])


def update_table_access_table(opts: Namespace, table: Table, records: List[Dict[str, Any]]) -> bool:
    ndel = opts.tables.ont_connection.execute(delete(table).where(table.c.c_table_cd == Default_Base)).rowcount
    if ndel > 0:
        print("{} {} {} deleted".format(ndel, table, pluralize(ndel, "record")))
    nins = opts.tables.ont_connection.execute(table.insert(), records).rowcount
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
        return generate_output(FHIRConceptDimension(g, name_base=opts.base), opts, resource,
                               i2b2table.concept_dimension)
    else:
        table = opts.tables.concept_dimension
        change_column_length(table, table.c.concept_cd, 200, opts.tables.crc_engine)
        return update_dimension_table(FHIRConceptDimension(g, name_base=opts.base), opts, table,
                                      'concept_path', [opts.base], resource)


def update_dimension_table(fo: FHIRMetadata, opts: Namespace, table: Table, table_key: str,
                           key_match: List[str], resource: Optional[URIRef]) -> bool:
    for km in key_match:
        q = delete(table).where(table.c[table_key].startswith(km.replace('\\', '\\\\')))
        ndel = opts.tables.crc_connection.execute(q).rowcount
        if ndel > 0:
            print("{} {} {} deleted".format(ndel, table, pluralize(ndel, "record")))
    nins = opts.tables.crc_connection.execute(table.insert(), [e._freeze()
                                                               for e in fo.dimension_list(resource)]).rowcount
    print("{} {} {} inserted".format(nins, table, pluralize(nins, "record")))
    return True


def change_column_length(table: Table, column: Column, length: int, engine: Engine) -> None:
    if column.type.length < length:
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
        return generate_output(FHIRModifierDimension(g, name_base=opts.base), opts, resource,
                               i2b2table.modifier_dimension)
    else:
        table = opts.tables.modifier_dimension
        change_column_length(table, table.c.modifier_cd, 200, opts.tables.crc_engine)
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
        return generate_output(FHIROntologyTable(g, name_base=opts.base), opts, resource, "ontology")
    else:
        table = opts.tables.custom_meta
        change_column_length(table, table.c.c_basecode, 200, opts.tables.ont_engine)
        change_column_length(table, table.c.c_tooltip, 1600, opts.tables.ont_engine)    # MedicationStatement is 1547 long
        return update_dimension_table(FHIROntologyTable(g, name_base=opts.base), opts, table, 'c_basecode',
                                      [opts.base.replace('\\', '') + ':', 'W5'], resource)


def load_fhir_ontology(opts: Namespace) -> Optional[Graph]:
    g = Graph()
    print("Loading fhir.ttl")
    g.load(opts.indir + "fhir.ttl", format="turtle")
    print("loading w5.ttl")
    g.load(opts.indir + "w5.ttl", format="turtle")
    return g


class LoadFromFile (Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, value: str, option_string=None):
        with open(value) as f:
            parser.parse_args(f.read().split(), namespace)


def test_configuration(opts: Namespace) -> bool:
    """ Test the configuration, making sure that the tsv files exist, the database can be opened and that we have
    write access to at least some of the tables
    """
    def test_ttl_file(name: str) -> bool:
        f = Path(opts.indir + name)
        if f.is_file():
            print("\tFile: {}{} exists".format(opts.indir, name))
            return True
        else:
            return error("'{}' file not found in {}".format(name, opts.indir))

    def test_tn(name: str, tables: I2B2Tables) -> bool:
        if name in [k for k, _ in tables._tables()]:
            print("\tTable {} exists".format(tn))
            return True
        else:
            return error("unable to locate table '{}'".format(tn))

    def error(msg: str) -> bool:
        print("  Error: -> {}".format(msg))
        return False

    print("Validating input files")
    success = test_ttl_file('fhir.ttl')
    if not test_ttl_file('w5.ttl'):
        success = False

    print("Validating sql connection")
    tables = None
    try:
        tables = I2B2Tables(opts)
    except Exception as e:
        print(str(e))

    if not tables:
        success = error("Unable to open SQL database")
        ont_url, crc_url = I2B2Tables._db_urls(opts)
        if ont_url == crc_url:
            print("\tURL: {}".format(ont_url))
        else:
            print("\tOntoogy URL: {}".format(ont_url))
            print("\tCRC URL: {}".format(crc_url))
    else:
        print("\tConnection validated")
        print("Validating target tables")
        for tn in i2b2table.all_tables():
            if not test_tn(i2b2table.phys_name(tn), tables):
                success = False

    if success:
        print("Testing write access")
        row_count = 0
        try:
            row_count = tables.ont_connection.execute(update(tables.table_access)
                                                      .where(tables.table_access.c.c_hlevel == 0)
                                                      .values(c_hlevel=0)).rowcount
        except Exception as e:
            if "permission" not in str(e) or "denied" not in str(e):
                print(str(e))
        if row_count > 0:
            print("\t{} rows updated in table_access table ".format(row_count))
        else:
            success = error("Write permission denied for table_access table")

    return success


def create_parser() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    metadata_tables = [i2b2table.concept_dimension, i2b2table.modifier_dimension, i2b2table.ontology_table,
                       i2b2table.table_access]
    parser = ArgumentParser(description="FHIR in i2b2 metadata generator", fromfile_prefix_chars='@')
    # For reasons we don't completely understand, the default parser doesn't split the lines...
    parser.convert_arg_line_to_args = lambda arg_line: arg_line.split()
    parser.add_argument("indir", help="Input directory or URI of w5.ttl and fhir.ttl files")
    parser.add_argument("-o", "--outdir", help="Output directory to store .tsv files."
                                               " If absent, .tsv files are not generated.")
    parser.add_argument("-t", "--table", metavar="TABLE",
                        help="Table to update ({}) (default: All tables)".format(', '.join(metadata_tables)),
                        choices=metadata_tables)
    parser.add_argument("-r", "--resource",
                        help="Name of specific resource to emit (e.g. Observation). (default: all)")
    parser.add_argument("--sourcesystem", metavar="SOURCESYSTEM_CD",
                        default=Default_Sourcesystem_Code,
                        help="sourcesystem code (default: \"{}\")".format(Default_Sourcesystem_Code))
    parser.add_argument("--base",
                        default=Default_Path_Base,
                        help="Concept dimension base path. (default: \"{}\")".format(Default_Path_Base))
    parser.add_argument("-l", "--load", help="Load i2b2 SQL tables", action="store_true")
    parser.add_argument("-g", "--gentsv", help="Generate TSV output", action="store_true")
    parser.add_argument("-v", "--version", action='version', version='Version: {}'.format(__version__))
    parser.add_argument("--list", help="List table names", action="store_true")
    parser.add_argument("-db", "--dburl", help="Default database URL")
    parser.add_argument("-u", "--user", help="Default user name")
    parser.add_argument("-p", "--password", help="Default password")
    parser.add_argument("--test", help="Test the confguration", action="store_true")
    parser.add_argument("--crcdb", help="CRC database URL.  (default: DBURL)")
    parser.add_argument("--crcuser", help="User name for CRC database. (default: USER)")
    parser.add_argument("--crcpassword", help="Password for CRC database. (default: PASSWORD")
    parser.add_argument("--ontdb", help="Ontology database URL.  (default: DBURL)")
    parser.add_argument("--ontuser", help="User name for ontology database. (default: USER)")
    parser.add_argument("--ontpassword", help="Password for ontology database. (default: PASSWORD")
    parser.add_argument("--onttable", help="Ontology table name (default: {})".format(Default_Ontology_TableName))
    return parser


def genargs(argv: List[str]) -> Namespace:

    def setdefault(self: Namespace, vn: str, default: object) -> None:
        assert vn in self, "Unknown option"
        if not getattr(self, vn):
            setattr(self, vn, default)

    opts = create_parser().parse_args(argv)
    opts.setdefault = lambda *a: setdefault(opts, *a)
    opts.updatedate = datetime.now()
    if not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if opts.outdir and not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    if opts.load or opts.gentsv or opts.list or opts.test:
        opts.setdefault('crcdb', opts.dburl)
        opts.setdefault('crcuser', opts.user)
        opts.setdefault('crcpassword', opts.password)
        opts.setdefault('ontdb', opts.dburl)
        opts.setdefault('ontuser', opts.user)
        opts.setdefault('ontpassword', opts.password)
    return opts


def generate_i2b2(argv: List[str]) -> bool:
    opts = genargs(argv)

    if opts.test:
        if not test_configuration(opts):
            return False
    opts.tables = I2B2Tables(opts) if (opts.load or opts.list) and not opts.test else None
    if opts.load or opts.gentsv:
        g = load_fhir_ontology(opts)
    if opts.list:
        print('\n'.join(["{} : {}".format(tn, tp) for tn, tp in opts.tables._tables()]))
    if opts.load or opts.gentsv:
        return g is not None and generate_i2b2_files(g, opts)
    else:
        return True
