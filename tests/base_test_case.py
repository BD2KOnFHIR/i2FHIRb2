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
from datetime import datetime, timedelta
import unittest
from typing import Union

from dateutil.parser import parse
from rdflib import Graph


class FHIRGraph(Graph):
    def __init__(self):
        super().__init__()
        print("Loading graph...", end="")
        self.dirname, _ = os.path.split(os.path.abspath(__file__))
        self.load(os.path.join(self.dirname, 'data', 'w5.ttl'), format="turtle")
        self.load(os.path.join(self.dirname, 'data', 'fhir.ttl'), format="turtle")
        print("done")

shared_graph = FHIRGraph()


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

    def test_almostnow(self):
        self.assertTrue(self.almostnow(str(datetime.now())))
        self.assertTrue(self.almostnow(str(datetime.now() - timedelta(seconds=1))))
        self.assertFalse(self.almostnow(str(datetime.now() - timedelta(seconds=5))))

    def test_almostequal(self):
        self.assertTrue(self.almostequal(str(datetime.now()), str(datetime.now())))
        self.assertTrue(self.almostequal(str(datetime.now()), str(datetime.now() - timedelta(seconds=1))))
        self.assertFalse(self.almostequal(str(datetime.now()), str(datetime.now() - timedelta(seconds=5))))
