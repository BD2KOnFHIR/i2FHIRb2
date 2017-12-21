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
import argparse
from argparse import ArgumentParser
import shlex
from typing import List

import sys

from i2fhirb2.loaders.i2b2graphmap import I2B2GraphMap
from i2fhirb2.sqlsupport.dbconnection import add_connection_args, process_parsed_args, I2B2Tables, decode_file_args, \
    FileAwareParser


def create_parser() -> FileAwareParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = FileAwareParser(description="Clear data from FHIR observation fact table")
    parser.add_argument("uploadid", metavar="Upload identifiers",
                        help="Upload identifer(s) -- unique batch identifiers", type=int, nargs='*')
    parser.add_argument("--sourcesystemcd", metavar="Source system code",
                        help="sourcesystem_code to remove")
    parser.add_argument("-mv", "--metavoc", help="Metavocabulary directory - ignored")
    return parser


def remove_facts(argv: List[str]) -> bool:
    """
    Convert a set of FHIR resources into their corresponding i2b2 counterparts.
    :param argv: Command line arguments.  See: create_parser for details
    :return:
    """
    parser = add_connection_args(create_parser())
    opts = parser.parse_args(decode_file_args(argv, parser))
    if opts is None:
        return False
    process_parsed_args(opts)           # Update CRC and Meta table connection information
    if not opts.uploadid and not opts.sourcesystemcd:
        parser.print_usage()
        return False
    for uploadid in opts.uploadid:
        print("---> Removing entries for id {}".format(uploadid))
        I2B2GraphMap.clear_i2b2_tables(I2B2Tables(opts), uploadid)
    if opts.sourcesystemcd:
        print("---> Removing entries for sourcesystem_cd {}".format(opts.sourcesystemcd))
        I2B2GraphMap.clear_i2b2_sourcesystems(I2B2Tables(opts), opts.sourcesystemcd)
    return True


if __name__ == "__main__":
    remove_facts(sys.argv[1:])
