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

from tests.utils.output_redirector import OutputRedirector

output1 = """.abcdefgh-
.ijklmnop-
.qrstuvwx-
yz-

"""

class ListChunkerTestCase(unittest.TestCase, OutputRedirector):

    def test_basics(self):
        from i2fhirb2.i2b2model.shared.listchunker import ListChunker
        lc = ListChunker([], 10)
        for c in lc:
            self.assertFalse(True, "List should be empty")
        lc = ListChunker([1], 10)
        for c in lc:
            self.assertEqual(c, [1])
        lc = ListChunker(range(10, 20), 10)
        for c in lc:
            self.assertEqual(c, range(10, 20))
        lc = ListChunker(range(10,21), 10)
        self.assertEqual(lc.__next__(), range(10, 20))
        self.assertEqual(lc.__next__(), range(20, 21))
        with self.assertRaises(StopIteration):
            lc.__next__()

    def test_dots(self):
        from i2fhirb2.i2b2model.shared.listchunker import ListChunker
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        lc = ListChunker(alphabet, 8)
        result = self._push_stdout()
        for c in lc:
            print(c + '-')
        result.flush()
        self._pop_stdout()
        self.assertEqual(output1, result.getvalue())

        lc = ListChunker(alphabet, 8)
        result = self._push_stdout()
        for c in lc:
            pass
        result.flush()
        self._pop_stdout()
        self.assertEqual('...\n', result.getvalue())


if __name__ == '__main__':
    unittest.main()
