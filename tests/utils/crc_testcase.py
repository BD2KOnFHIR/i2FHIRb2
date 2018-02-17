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
import io
import unittest

import sys
from contextlib import contextmanager, redirect_stdout
from functools import reduce

from i2fhirb2.removefacts import remove_facts
from tests.utils.base_test_case import test_conf_file


class CRCTestCase(unittest.TestCase):

    def tearDown(self):
        if getattr(self, "_sourcesystem_cd", None):
            remove_facts(f"--conf {test_conf_file} -ss {self._sourcesystem_cd}".split())

    @staticmethod
    def text_to_number(txt: str) -> int:
        return reduce(lambda acc, upd: (((acc ^ ord(upd)) << 8) + ord(upd)) % 0xFFFF, txt, sys.maxsize)


    @contextmanager
    def sourcesystem_cd(self) -> str:
        """ Generate a sourcesystem_code that identifies the test case and make sure it doesn't pollute the database.
        _sourcesystem_cd and _upload_id are added to the specific object

        :return: sourcesystem code
        """
        save_ss_cd = getattr(self, "_sourcesystem_cd", None)
        save_up_id = getattr(self, "_upload_id", None)
        self._sourcesystem_cd = "test_i2FHIRb2_" + type(self).__name__
        self._upload_id = self.text_to_number(self._sourcesystem_cd)
        print(f"+++++ {self._sourcesystem_cd}")
        print(f"      {self._upload_id}")
        try:
            yield self._sourcesystem_cd
        finally:
            # with redirect_stdout(io.StringIO()):
            remove_facts(f"--conf {test_conf_file} -ss {self._sourcesystem_cd}".split())
            print(f"      {self._upload_id}")
            print(f"----- {self._sourcesystem_cd}")
            if save_ss_cd:
                self._sourcesystem_cd = save_ss_cd
                self._upload_id = save_up_id
            else:
                delattr(self, '_sourcesystem_cd')
                delattr(self, '_upload_id')
