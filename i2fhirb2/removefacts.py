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
from argparse import Namespace
from typing import List, Tuple, Optional

from sqlalchemy import Table, delete
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker, Session

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
    add_connection_args(add_common_parameters(parser, multi_upload_ids=True), strong_config_file=False)
    parser.add_argument("--testlist", help="List leftover test suite entries", action="store_true")
    parser.add_argument("--removetestlist", help="Remove leftover test suite entries", action="store_true")
    return parser


def sourcesystem_test_query(c: Connection, t: Table) -> List[Tuple[Table, str]]:
    """ Generate a sourcesystem_cd test query for table t

    :param c: Connection
    :param t: Table
    :return: list of elements
    """
    q = c.query(t.c.sourcesystem_cd).filter(t.c.sourcesystem_cd.startswith('test_i2FHIRb2_')).distinct()
    return [(t, e[0]) for e in q.all()]


def list_test_artifacts(opts: Optional[Namespace], tables: Optional[I2B2Tables]=None) -> List[Tuple[Table, str]]:
    """  Return a list of tables and sourcesystem_ids from the test suite

    :param opts: Passed options.  Can be omitted if tables is present
    :param tables: I2B2 tables
    :return: List 
    """
    if tables is None:
        tables = I2B2Tables(opts)
    session = sessionmaker(bind=tables.crc_engine)()
    qr = sourcesystem_test_query(session, tables.patient_dimension)
    qr += sourcesystem_test_query(session, tables.patient_mapping)
    qr += sourcesystem_test_query(session, tables.visit_dimension)
    qr += sourcesystem_test_query(session, tables.encounter_mapping)
    qr += sourcesystem_test_query(session, tables.provider_dimension)
    qr += sourcesystem_test_query(session, tables.observation_fact)
    if qr:
        print('\n'.join(f"TABLE: {e[1]} \t: {e[0]}" for e in qr))
    return qr


def remove_test_artifacts(opts: Namespace):
    """ Remove any test artifacts (sourcesystem_id starts with 'test_i2FHIRb2_')
    
    :param opts: 
    :return: 
    """
    tables = I2B2Tables(opts)
    artifacts_list = list_test_artifacts(opts, tables)
    for table, ss_cd in artifacts_list:
        q = delete(table).where(table.c.sourcesystem_cd == ss_cd)
        ndel = opts.tables.crc_connection.execute(q).rowcount
        print(f"{ndel} rows removed from {table}")
    return True


def remove_facts(argv: List[str]) -> bool:
    """
    Convert a set of FHIR resources into their corresponding i2b2 counterparts.
    
    :param argv: Command line arguments.  See: create_parser for details
    :return:
    """
    parser = create_parser()
    local_opts = parser.parse_args(argv)                        # Pull everything from the actual command line
    if not (local_opts.uploadid or local_opts.sourcesystem or local_opts.testlist or local_opts.removetestlist):
        parser.error("Option must be one of: -ss, -u, --testlist, --removetestlist)")

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
    if opts.testlist:
        print("---> Listing orphan test elements in database")
        list_test_artifacts(opts)
    if opts.removetestlist:
        print("---> Removing orphan test elements in database")
        remove_test_artifacts(opts)
    return True


if __name__ == "__main__":
    remove_facts(sys.argv[1:])
