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
import unittest
from typing import Callable, List

import os

from tests.utils.output_redirector import OutputRedirector


class ScriptTestBase(unittest.TestCase, OutputRedirector):
    dirname = None
    save_output: bool = False              # Override this to save output
    tst_dir: str = None
    tst_fcn: Callable[[List[str]], bool] = None

    @classmethod
    def call_tst_fcn(cls, args: str):
        return cls.tst_fcn(args.split())

    def check_output(self, test_file: str, output: str) -> None:
        assert self.dirname is not None, "dirname must be set to local file path"
        fullfilename = os.path.join(self.dirname, 'data_out', self.tst_dir, test_file)
        if self.save_output:
            with open(fullfilename, 'w') as outf:
                outf.write(output)
        self.maxDiff = None
        with open(fullfilename) as testf:
            self.assertEqual(testf.read(), output)
        self.assertFalse(self.save_output, "save_output is true")

    def check_output_output(self, args: str,  test_file: str, exception: bool=False) -> None:
        self._push_stdout()
        if exception:
            with self.assertRaises(SystemExit):
                self.call_tst_fcn(args)
        else:
            self.call_tst_fcn(args)
        output = self._pop_stdout()
        self.check_output(test_file, output.getvalue())

    def check_filtered_output(self, args: str, test_file: str, filtr: Callable[[str], str]) -> None:
        self._push_stdout()
        self.call_tst_fcn(args)
        output = self._pop_stdout()
        self.check_output(test_file, filtr(output.getvalue()))

    def check_error_output(self, args: str, test_file: str) -> None:
        self._push_stderr()
        with self.assertRaises(SystemExit):
            self.call_tst_fcn(args)
        output = self._pop_stderr()
        self.check_output(test_file, output.getvalue())
