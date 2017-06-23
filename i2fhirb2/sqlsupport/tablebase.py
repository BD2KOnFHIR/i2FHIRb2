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
import inspect
from collections import OrderedDict
from typing import List, Callable, Union

from i2fhirb2.sqlsupport.orderedset import OrderedSet

EvalParam = Union[Callable[[object], object], Callable[[], object], object]


class ColumnsBase:
    """
    Base class for a dynamically evaluated columns list
    """
    _columns = []                 # type: OrderedSet

    @classmethod
    def _bind_keys(cls, keys: List[str]):
        for k in keys:
            if k not in cls._columns:
                cls._columns.add(k)

    def _freeze(self) -> OrderedDict:
        """
        Evaluate all of the column values and return the result
        :return: column/value tuples
        """
        return OrderedDict(**{k: getattr(self, k, None) for k in super().__getattribute__("_columns")})

    def _eval(self, m: EvalParam) -> object:
        """
        Evaluate m returning the method / function invocation or value.  Kind of like a static method
        :param m: object to evaluate
        :return: return
        """
        if inspect.ismethod(m) or inspect.isroutine(m):
            return m()
        elif inspect.isfunction(m):
            return m(self) if len(inspect.signature(m)) > 0 else m()
        else:
            return m

    def __getattribute__(self, item):
        if item.startswith("_"):
            return super().__getattribute__(item)
        cols = super().__getattribute__("_columns")
        if item in cols:
            return self._eval(super().__getattribute__(item))
        return super().__getattribute__(item)
