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
from argparse import ArgumentParser
import shlex
from typing import List

import sys

from i2fhirb2.loaders.i2b2graphmap import I2B2GraphMap
from i2fhirb2.sqlsupport.dbconnection import add_connection_args, process_parsed_args, I2B2Tables


def create_parser() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgumentParser(description="Clear data from FHIR observation fact table")
    parser.add_argument("-u", "--uploadid", metavar="Upload identifier",
                        help="Upload identifer -- uniquely identifies this batch", type=int, required=True)
    # Add the database connection arguments
    add_connection_args(parser)
    return parser


def decode_file_args(argv: List[str]) -> List[str]:
    """
    Preprocess any arguments that begin with an '@' sign.  This replaces the one in Argparse because it
    a) doesn't process "-x y" correctly and b) ignores bad files
    :param argv: raw options list
    :return: options list with file references replaced
    """
    for arg in [arg for arg in argv if arg[0] == '@']:
        argv.remove(arg)
        with open(arg[1:]) as config_file:
            argv += shlex.split(config_file.read())
            return decode_file_args(argv)
    return argv


def remove_facts(argv: List[str]) -> bool:
    """
    Convert a set of FHIR resources into their corresponding i2b2 counterparts.
    :param argv: Command line arguments.  See: create_parser for details
    :return:
    """
    opts = create_parser().parse_args(decode_file_args(argv))
    if opts is None:
        return False
    process_parsed_args(opts)           # Update CRC and Meta table connection information
    I2B2GraphMap.clear_i2b2_tables(I2B2Tables(opts), opts.uploadid)
    return True


if __name__ == "__main__":
    remove_facts(sys.argv[1:])
