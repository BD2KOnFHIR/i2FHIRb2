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
import unittest
from datetime import datetime, timedelta
from typing import Union

from dateutil.parser import parse
from fhirtordf.fhir.fhirmetavoc import FHIRMetaVoc
from rdflib import Graph

test_directory = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
test_conf_directory = os.path.join(test_directory, 'conf')
test_conf_file = os.path.abspath(os.path.join(test_conf_directory, 'db_conf'))
test_data_directory = os.path.join(test_directory, 'data')
mvdir = os.path.abspath(os.path.join(test_data_directory, 'fhir_metadata_vocabulary'))

test_upload_id = 117651                 # upload identifier for test cases
test_sourcesystem_cd = "i2FHIRb2_Test"  # source system code for test cases


def FHIRGraph():
    print("Loading graph", end="")
    fmv = FHIRMetaVoc(os.path.join(mvdir, 'fhir.ttl'))
    print(" (cached)" if fmv.from_cache else "(from disc)", end="")
    fmv.g.load(os.path.join(mvdir, 'w5.ttl'), format="turtle")
    print(" done\n")
    return fmv.g


class BaseTestCase(unittest.TestCase):
    @staticmethod
    def almostnow(d: Union[datetime, str]) -> bool:
        if not isinstance(d, datetime):
            d = parse(d)
        return datetime.now() - d < timedelta(seconds=2)

    @staticmethod
    def almostequal(d1: Union[datetime, str], d2: Union[datetime, str]):
        if not isinstance(d1, datetime):
            d1 = parse(d1)
        if not isinstance(d2, datetime):
            d2 = parse(d2)
        return d1 - d2 < timedelta(seconds=2)

    def assertAlmostNow(self, d: Union[datetime, str]):
        self.assertTrue(self.almostnow(d))

    def assertDatesAlmostEqual(self, d1: str, d2: str):
        self.assertTrue(self.almostequal(d1, d2))


def make_and_clear_directory(dirbase: str):
    import shutil
    safety_file = os.path.join(dirbase, "generated")
    if os.path.exists(dirbase):
        if not os.path.exists(safety_file):
            raise FileExistsError("{} not found in test directory".format(safety_file))
        shutil.rmtree(dirbase)
    os.makedirs(dirbase)
    with open(os.path.join(dirbase, "generated"), "w") as f:
        f.write("Generated for safety.  Must be present for test to remove this directory.")
