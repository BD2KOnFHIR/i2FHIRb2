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
import sys
from argparse import ArgumentParser
from typing import List

from i2fhirb2.common_cli_parameters import add_common_parameters
from i2fhirb2.file_aware_parser import FileAwareParser
from i2fhirb2.loaders.i2b2graphmap import I2B2GraphMap
from i2fhirb2.sqlsupport.dbconnection import add_connection_args, process_parsed_args, I2B2Tables


def create_parser() -> FileAwareParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = FileAwareParser(description="Clear data from FHIR observation fact table", prog="removefacts",
                             use_defaults=False)
    return add_connection_args(add_common_parameters(parser, multi_upload_ids=True),
                               strong_config_file=False)


def remove_facts(argv: List[str]) -> bool:
    """
    Convert a set of FHIR resources into their corresponding i2b2 counterparts.
    :param argv: Command line arguments.  See: create_parser for details
    :return:
    """
    parser = create_parser()
    local_opts = parser.parse_args(argv)                        # Pull everything from the actual command line
    if not local_opts.uploadid and not local_opts.sourcesystem:
        parser.error("Upload identifiers and/or source system codes must be supplied")

    opts = parser.parse_args(parser.decode_file_args(argv))     # Include the options file
    if opts is None:
        return False
    opts.uploadid = local_opts.uploadid
    opts.sourcesystem = local_opts.sourcesystem

    process_parsed_args(opts, parser.error)           # Update CRC and Meta table connection information

    if opts.uploadid:
        for uploadid in opts.uploadid:
            print("---> Removing entries for id {}".format(uploadid))
            I2B2GraphMap.clear_i2b2_tables(I2B2Tables(opts), uploadid)
    if opts.sourcesystem:
        print("---> Removing entries for sourcesystem_cd {}".format(opts.sourcesystem))
        I2B2GraphMap.clear_i2b2_sourcesystems(I2B2Tables(opts), opts.sourcesystem)
    return True


if __name__ == "__main__":
    remove_facts(sys.argv[1:])
