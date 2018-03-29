import re
from argparse import Namespace
import shlex
from typing import List, Optional
import sys
import os

from i2fhirb2 import __version__
from i2fhirb2.common_cli_parameters import add_common_parameters
from i2b2model.sqlsupport.dbconnection import add_connection_args
from i2b2model.sqlsupport.file_aware_parser import FileAwareParser

meta_parameters = ["file", "show", "create", "createorrep"]


def print_conf_file(opts: Namespace) -> Optional[str]:
    """ Print the config file contents

    :param opts: Options carrying file name
    :return: None if success otherwise error message
    """
    with open(opts.file) as f:
        args = shlex.split(f.read())
    parser = create_parser(use_defaults=False)
    opts = parser.parse_args(args)
    for k, v in opts.__dict__.items():
        if v is not None:
            print(f"{k}:\t\t{v}")
    return None


def create_conf_file(opts: Namespace) -> Optional[str]:
    """ Create the configuration file

    :param opts: Creation options
    :return: Error message if problems, otherwise None
    """
    if not opts.createorrep:
        if os.path.exists(opts.file):
            return f"{opts.file} already exists!"
    with open(opts.file, 'w') as f:
        for k, v in opts.__dict__.items():
            if k not in meta_parameters and v is not None:
                f.write(f"--{k} {esc(v)}\n")
    return None


def esc(arg: str) -> str:
    """ Escape arg in a way that the shlex (argv) processor keeps it whole

    :param arg: argument to escape
    :return: What to write in the file
    """
    arg = re.sub(r'\\', r'\\\\', str(arg))
    return f'"{arg}"' if re.search(r'\s', arg) else arg


def add_meta_args(parser: FileAwareParser) -> None:
    """ dd the control (meta) arguments to the parser

    :param parser: Parser to add arguments to
    """
    parser.add_argument("-f", "--file", help="Configuration file", default="db_conf")
    parser.add_argument("-s", "--show", help="Display current configuration", action="store_true")
    parser.add_argument("-c", "--create", help="Create new configuration file if not exists", action="store_true")
    parser.add_argument("-c!", "--createorrep", help="Create or replace configuration file ", action="store_true")


def create_parser(use_defaults: bool = True) -> FileAwareParser:
    """
    Create a command line argument parser

    :param use_defaults: Add defaults
    :return: parser
    """
    parser = FileAwareParser(description="Create configuration file for i2FHIRb2 software", prog="conf_file",
                             use_defaults=use_defaults)
    return add_connection_args(add_common_parameters(parser))


def conf_file(argv: List[str]) -> bool:
    """
    Create and/or print a configuration file

    :param argv: Parameter list -- see create_parser for details
    :return: True if success - otherwise an exception is thrown
    """
    parser = create_parser()
    add_meta_args(parser)
    opts = parser.parse_args(argv)

    # Note that "help" and "version" exit immediately
    if not (opts.create or opts.createorrep or opts.show):
        parser.print_usage()
        return False

    rval = create_conf_file(opts) if opts.create or opts.createorrep else None

    if not rval and opts.show:
        rval = print_conf_file(opts)

    if rval:
        parser.error(rval)

    return True


if __name__ == "__main__":
    conf_file(sys.argv[1:])
