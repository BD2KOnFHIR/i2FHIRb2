import os
import sys
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union
from urllib import request
from urllib.error import HTTPError

from fhirtordf.fhir.fhirmetavoc import FHIRMetaVoc
from i2b2model.shared.i2b2core import I2B2Core

from i2fhirb2.common_cli_parameters import add_common_parameters
from i2b2model.metadata.commondimension import CommonDimension
from rdflib import Graph
from sqlalchemy import delete, Table, update
from dynprops import heading, as_dict

from i2fhirb2.fhir.fhirconceptdimension import FHIRConceptDimension
from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
from i2fhirb2.fhir.fhirspecific import FHIR, DEFAULT_BASE
from i2b2model.metadata.i2b2ontology import OntologyEntry
from i2b2model.metadata.i2b2tableaccess import TableAccess
from i2b2model.shared.tablenames import i2b2tablenames
from i2b2model.sqlsupport.dbconnection import add_connection_args, process_parsed_args
from i2b2model.sqlsupport.file_aware_parser import FileAwareParser
from i2b2model.sqlsupport.i2b2tables import I2B2Tables, change_column_length
from i2fhirb2.tsv_support.tsvwriter import write_tsv

DIMENSION_LIST = Union[List[FHIRConceptDimension], List[FHIRModifierDimension], List[OntologyEntry]]


def pluralize(cnt: int, base: Any) -> str:
    """
    Pluralize base based on the number in cnt
    :param cnt: number of elements
    :param base: base word
    :return: plural
    """
    return str(base) + ('s' if cnt != 1 else '')


def initialize_table_defaults(g: Graph, opts: Namespace) -> None:
    """
    Initialize all of the table defaults
    :param g: Graph containing fhir.ttl
    :param opts: input options
    """
    # TODO: This is kind of messy -- we've refactored so we should be able to consolidate this
    CommonDimension.graph = g

    I2B2Core.sourcesystem_cd = opts.sourcesystem
    I2B2Core.update_date = opts.updatedate


def generate_i2b2_files(g: Graph, opts: Namespace) -> bool:
    """
    Generate the requested i2b2 files as listed in opts
    :param g: Graph of the data to be generated
    :param opts: supplied options
    :return: success indicator
    """
    if not opts.table or opts.table in (i2b2tablenames.concept_dimension,
                                        i2b2tablenames.concept_dimension,
                                        i2b2tablenames.ontology_table):
        resource = FHIR[opts.resource] if opts.resource else None
        initialize_table_defaults(g, opts)
        dimset = FHIROntologyTable(g, name_base=opts.base).dimension_list(resource)

        return \
            output_table_access(opts) and \
            output_concept_dimension(opts, dimset.concept_dimension) and \
            output_modifier_dimension(opts, dimset.modifier_dimension) and \
            output_ontology(opts, dimset.ontology_dimension)


def output_table_access(opts: Namespace) -> bool:
    """
    Generate the table access entries if requested
    :param opts: user options
    :return: True if success or generation is not needed
    """
    if not opts.table or opts.table == i2b2tablenames.table_access:
        table_access = TableAccess('FHIR')
        if opts.outdir:
            return write_tsv(opts.outdir, 'table_access', heading(table_access), [table_access])
        else:
            return update_table_access_table(opts, opts.tables.table_access, [as_dict(table_access)])
    else:
        return True


def update_table_access_table(opts: Namespace, table: Table, records: List[Dict[str, Any]]) -> bool:
    ndel = opts.tables.ont_connection.execute(delete(table).where(table.c.c_table_cd == DEFAULT_BASE)).rowcount
    if ndel > 0:
        print("{} {} {} deleted".format(ndel, table, pluralize(ndel, "record")))
    nins = opts.tables.ont_connection.execute(table.insert(), records).rowcount
    print("{} {} {} inserted".format(nins, table, pluralize(nins, "record")))
    return True


def output_concept_dimension(opts: Namespace, output: List[FHIRConceptDimension]) -> bool:
    """
    Generate the concept dimension output if required
    :param opts: input options
    :param output: output list
    :return: success indicator
    """
    table_name = i2b2tablenames.concept_dimension
    if not opts.table or opts.table == table_name:
        if opts.outdir:
            return write_tsv(opts.outdir, table_name, heading(FHIRConceptDimension), output)
        else:
            table = opts.tables.concept_dimension
            change_column_length(table, table.c.concept_cd, 200, opts.tables.crc_engine)
            return update_dimension_table(output, opts, table)
    else:
        return True


def output_modifier_dimension(opts: Namespace, output: List[FHIRModifierDimension]) -> bool:
    """
    Generate the modifier dimension output if required
    :param opts: input options
    :param output: output list
    :return: success indicator
    """
    table_name = i2b2tablenames.modifier_dimension
    if not opts.table or opts.table == table_name:
        if opts.outdir:
            return write_tsv(opts.outdir, table_name, heading(FHIRModifierDimension), output)
        else:
            table = opts.tables.modifier_dimension
            change_column_length(table, table.c.modifier_cd, 200, opts.tables.crc_engine)
            return update_dimension_table(output, opts, table)
    else:
        return True


def output_ontology(opts: Namespace, output: List[OntologyEntry]) -> bool:
    """
    Generate the i2b2 ontology output if required
    :param opts: input options
    :param output: set of ontology entries
    :return: success indicator
    """
    table_name = i2b2tablenames.ontology_table
    if not opts.table or opts.table == table_name:
        if opts.outdir:
            return write_tsv(opts.outdir, table_name, heading(OntologyEntry), output)
        else:
            table = opts.tables.ontology_table
            change_column_length(table, table.c.c_basecode, 200, opts.tables.ont_engine)
            # MedicationStatement is 1547 long
            change_column_length(table, table.c.c_tooltip, 1600, opts.tables.ont_engine)
            return update_dimension_table(output, opts, table)
    else:
        return True


def update_dimension_table(output: DIMENSION_LIST, opts: Namespace, table: Table) \
        -> bool:
    """
    Update the supplied dimension table, removing all existing records

    :param output: list of dimension entries
    :param opts: input options
    :param table: table to be updated
    :return: Success indicator
    """
    q = delete(table).where(table.c.sourcesystem_cd == opts.sourcesystem)
    ndel = opts.tables.crc_connection.execute(q).rowcount
    if ndel > 0:
        print("{} {} {} deleted".format(ndel, table, pluralize(ndel, "record")))
    nins = opts.tables.crc_connection.execute(table.insert(), [as_dict(e) for e in output]).rowcount
    print("{} {} {} inserted".format(nins, table, pluralize(nins, "record")))
    return True


def load_fhir_ontology(opts: Namespace) -> Graph:
    """
    Load the fhir specification ontology and w5
    :param opts: User options
    :return: Graph containing the ontology
    """
    print("Loading fhir.ttl")
    fmv = FHIRMetaVoc(os.path.join(opts.metadatavoc, 'fhir.ttl'))
    print(" (cached)" if fmv.from_cache else "(from disc)")
    print("loading w5.ttl")
    fmv.g.load(os.path.join(opts.metadatavoc, 'w5.ttl'), format="turtle")
    print(" done\n")
    return fmv.g


def test_configuration(opts: Namespace) -> bool:
    """ Test the configuration, making sure that the tsv files exist, the database can be opened and that we have
    write access to at least some of the tables
    """
    def test_ttl_file(name: str) -> bool:
        filename = opts.metadatavoc + name
        f = Path(opts.metadatavoc + name)
        if '://' in str(filename):
            try:
                request.urlopen(filename)
            except HTTPError as e_:
                return error("{}: {}".format(filename, e_))
            print('\tURL: {} is valid'.format(filename))
        elif f.is_file():
            print("\tFile: {} exists".format(filename))
        else:
            return error("'{}' file not found in {}".format(name, opts.metadatavoc))
        return True

    def test_tn(name: str, i2b2tables: I2B2Tables) -> bool:
        if name in [k for k, _ in i2b2tables._tables()]:
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
        for tn in i2b2tablenames.all_tables():
            if not test_tn(i2b2tablenames.phys_name(tn), tables):
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


def create_parser() -> FileAwareParser:
    """
    Create a command line parser
    :return: parser
    """
    metadata_tables = [i2b2tablenames.concept_dimension,
                       i2b2tablenames.modifier_dimension,
                       i2b2tablenames.ontology_table,
                       i2b2tablenames.table_access]
    parser = FileAwareParser(description="FHIR in i2b2 metadata generator", prog="generate_i2b2")
    parser.add_argument("-od", "--outdir", metavar="TSV OUTPUT DIR",
                        help="Output directory to store .tsv files. If absent, .tsv files are not generated.")
    parser.add_argument("-t", "--table", metavar="I2B2 TABLE",
                        help="Table to update ({}) (default: All tables)".format(', '.join(metadata_tables)),
                        choices=metadata_tables)
    parser.add_argument("-r", "--resource",
                        help="Name of specific resource to emit (e.g. Observation). (default: all)")
    parser.add_argument("-l", "--load",
                        help="Load i2b2 SQL tables", action="store_true")
    parser.add_argument("--list", help="List table names", action="store_true")
    parser.add_argument("--test", help="Test the confguration", action="store_true")
    # Add the database connection arguments list
    add_connection_args(add_common_parameters(parser))

    return parser


def genargs(argv: List[str]) -> Namespace:
    """
    Generate the list of input arguments
    :param argv: input argument list
    :return: argparser namespace
    """

    def setdefault(self: Namespace, vn: str, default: object) -> None:
        assert vn in self, "Unknown option"
        if not getattr(self, vn):
            setattr(self, vn, default)

    parser = create_parser()
    opts = parser.parse_args(parser.decode_file_args(argv))
    if not (opts.version or opts.list or opts.test or opts.load or opts.outdir):
        parser.print_help()
    opts.setdefault = lambda *a: setdefault(opts, *a)
    opts.updatedate = datetime.now()
    if not opts.metadatavoc.endswith(os.sep):
        opts.metadatavoc = os.path.join(opts.metadatavoc, '')
    if opts.outdir and not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    i2b2tablenames.ontology_table = opts.onttable
    # Set the defaults for the crc and ontology tables
    return process_parsed_args(opts, parser.error) if opts.load or opts.list or opts.test else opts


def generate_i2b2(argv: List[str]) -> bool:
    """
    Generate a set of i2b2 metadata tables
    :param argv: input arguments
    :return: Success indicator
    """
    opts = genargs(argv)

    # configuration test option
    if opts.test:
        if not test_configuration(opts):
            return False

    # Load the ontology if actually generating output
    if opts.load or opts.outdir:
        g = load_fhir_ontology(opts)
    else:
        g = None

    # list table names
    opts.tables = I2B2Tables(opts) if (opts.load or opts.list) and not opts.test else None
    if opts.list:
        print('\n'.join(["{} : {}".format(tn, tp) for tn, tp in opts.tables._tables()]))

    # Generate actual output if requested
    if opts.load or opts.outdir:
        return g is not None and generate_i2b2_files(g, opts)
    else:
        return True


if __name__ == "__main__":
    generate_i2b2(sys.argv[1:])
