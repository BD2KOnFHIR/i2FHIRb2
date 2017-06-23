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
#
# import unittest
#
# from i2fhirb2.sqlsupport.tablebase import ColumnsBase
#
#
# def const_fun():
#     return "Constant Function"
#
#
# class OneClass(ColumnsBase):
#     classvalue = "Class Value"
#     const_f = const_fun
#     const = 1173
#
#     _columns = ["class_method", "static_method", "regular_method", "const_f", "const"]
#
#     def __init__(self):
#         self._rv = "Regular Value"
#
#     @classmethod
#     def class_method(cls):
#         return cls.classvalue
#
#     @staticmethod
#     def static_method():
#         return "Static Value"
#
#     def regular_method(self):
#         return self._rv
#
#
# class MiddleClass(OneClass):
#     classvalue = "Middle Class Value"
#
#     def __init__(self):
#         super().__init__()
#         self._av = "Another Value"
#
#     @classmethod
#     def class_method(cls):
#         return cls.classvalue
#
#     def another_method(self):
#         return self._av
#
#     OneClass._columns.append(["another_method"])
#
#
#
# class TableBaseTestCase(unittest.TestCase):
#     def test_basics(self):
#         self.assertEqual(True, False)
#
#
# if __name__ == '__main__':
#     unittest.main()
