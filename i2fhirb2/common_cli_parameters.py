# Copyright (c) 2018, Mayo Clinic
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
from fhirtordf.rdfsupport.namespaces import FHIR

from i2fhirb2.fhir.fhirspecific import DEFAULT_SOURCE_SYSTEM, DEFAULT_BASE_PATH
from i2fhirb2.sqlsupport.dbconnection import FileAwareParser
from i2fhirb2 import __version__


def add_common_parameters(parser: FileAwareParser, multi_upload_ids: bool=False) -> FileAwareParser:
    """ Add the common parameters used (or at least recognized by) all script fundtions

    :param parser: parser to add parameters to
    :param multi_upload_ids: True means accept more than one upload identifier
    :return: Parser for chaining functions
    """
    parser.add_argument("-v", "--version", action='version', version='Version: {}'.format(__version__), default=None)
    parser.add_file_argument("-mv", "--metadatavoc", help="Location of FHIR Metavocabulary file",
                             default=DEFAULT_FMV)
    parser.add_argument("-ss", "--sourcesystem", metavar="SOURCE SYSTEM CODE", default=DEFAULT_SOURCE_SYSTEM,
                        help="Sourcesystem code")
    parser.add_argument("-u", "--uploadid", metavar="UPLOAD IDENTIFIER",
                        help="Upload identifer -- uniquely identifies this batch", type=int,
                        nargs='*' if multi_upload_ids else None)
    parser.add_argument("--base", metavar="CONCEPT IDENTIFIER BASE", default=DEFAULT_BASE_PATH,
                        help="Concept dimension and ontology base path")
    parser.add_argument("-ub", "--uribase", help="RESOURCE URI BASE", default=str(FHIR))
    parser.add_argument("-p", "--providerid", metavar="DEFAULT PROVIDER ID", help="Default provider id",
                        default=DEFAULT_PROVIDER_ID)
    return parser


DEFAULT_FMV = "http://build.fhir.org/"
DEFAULT_PROVIDER_ID = "FHIR:DefaultProvider"
DEFAULT_NAME_BASE = '\\FHIR\\'              # Default hame base
DEFAULT_PROJECT_ID = 'fhir'                 # Default project id for mapping tables
DEFAULT_ENCOUNTER_NUMBER_START = 500000     # Default starting encounter number if none is present
DEFAULT_PATIENT_NUMBER_START = 100000001    # Default starting patient number if none is present
IDE_SOURCE_HIVE = "HIVE"                    # Source for number to id mapping
