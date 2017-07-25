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
from argparse import ArgumentParser, Namespace

from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables


def add_connection_args(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("-db", "--dburl", help="Default database URL")
    parser.add_argument("--user", help="Default user name")
    parser.add_argument("--password", help="Default password")
    parser.add_argument("--crcdb", help="CRC database URL.  (default: DBURL)")
    parser.add_argument("--crcuser", help="User name for CRC database. (default: USER)")
    parser.add_argument("--crcpassword", help="Password for CRC database. (default: PASSWORD")
    parser.add_argument("--ontdb", help="Ontology database URL.  (default: DBURL)")
    parser.add_argument("--ontuser", help="User name for ontology database. (default: USER)")
    parser.add_argument("--ontpassword", help="Password for ontology database. (default: PASSWORD")
    return parser


def process_parsed_args(opts: Namespace) -> Namespace:
    def setdefault(vn: str, default: object) -> None:
        assert vn in opts, "Unknown option"
        if not getattr(opts, vn):
            setattr(opts, vn, default)

    setdefault('crcdb', opts.dburl)
    setdefault('crcuser', opts.user)
    setdefault('crcpassword', opts.password)
    setdefault('ontdb', opts.dburl)
    setdefault('ontuser', opts.user)
    setdefault('ontpassword', opts.password)
    opts.tables = I2B2Tables(opts)
    return opts
