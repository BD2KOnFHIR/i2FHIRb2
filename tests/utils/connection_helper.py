from argparse import Namespace, ArgumentParser

from i2b2model.sqlsupport.dbconnection import add_connection_args, process_parsed_args
from i2b2model.sqlsupport.file_aware_parser import FileAwareParser
from i2b2model.testingutils.connection_helper import create_parser, parse_args
from tests.utils.fhir_graph import test_conf_file


def connection_helper() -> Namespace:
    parser = create_parser()
    parser.add_argument("-mv", "--metavoc", help="Unused")
    return process_parsed_args(parse_args(parser, 41713, test_conf_file, []), FileAwareParser.error)
