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
from typing import Sized

import sys


class ListChunker:
    """
    Wrapper to iterate over potentially large lists in chunks.  We use this to commit large volumes of data in
    batches.
    """
    def __init__(self, lst: Sized, interval: int, print_progress: bool = True) -> None:
        """
        Iterator that returns elements of lst in chunks of size interval or less
        :param lst: List to be returned in batches
        :param interval: chunk size
        :param print_progress: True means print a '.' on stdout per chunk
        """
        self.input = lst
        self.interval = interval
        self._pos = 0
        self._dotted = False
        self._print_progress = print_progress

    def __iter__(self):
        return self

    def __next__(self) -> Sized:
        if self._pos < len(self.input):
            start = self._pos
            self._pos = self._pos + self.interval
            if self._pos < len(self.input) and self._print_progress:
                print('.', end='')
                sys.stdout.flush()
                self._dotted = True
            return self.input[start:self._pos]
        else:
            if self._dotted:
                print()
            raise StopIteration
