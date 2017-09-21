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
from collections import OrderedDict

from i2fhirb2.sqlsupport.dynobject import DynObject, DynElements


def const_f():
    return "Constant Function"


class OneClass(DynObject):
    _t = DynElements()
    classvalue = "Class Value"

    def __init__(self):
        super().__init__()
        self._rv = "Regular Value"

    @classmethod
    def class_method(cls):
        return cls.classvalue

    @staticmethod
    def static_method():
        return "Static Value"

    def regular_method(self):
        return self._rv

    _t.add(class_method)
    _t.add(static_method)
    _t.add(regular_method)
    _t.add_func(const_f)
    _t.add_const("const", 1173)


class MiddleClass(OneClass):
    _t = DynElements(OneClass)
    classvalue = "Middle Class Value"

    def __init__(self):
        super().__init__()
        self._av = "Another Value"

    @classmethod
    def class_method(cls):
        return cls.classvalue

    def another_method(self):
        return self._av

    _t.add(class_method)
    _t.add(another_method)


class InnerClass(MiddleClass):
    _t = DynElements(MiddleClass)

    def __init__(self):
        super().__init__()

    def yet_another_method(self):
        _ = self
        return "YAM"

    @staticmethod
    def another_method():
        return "YA"

    _t.add(yet_another_method)
    _t.add(another_method)


class DynamicElementTestCase(unittest.TestCase):

    def test_basics(self):
        tc = OneClass()
        self.assertTrue(tc._t.has_entry('class_method'))
        self.assertTrue(tc._t.has_entry('static_method'))
        self.assertTrue(tc._t.has_entry('regular_method'))
        self.assertTrue(tc._t.has_entry('const_f'))
        self.assertTrue(tc._t.has_entry('const'))
        self.assertFalse(tc._t.has_entry('foo'))

        self.assertEqual("Class Value", tc._t.get_entry(tc, 'class_method'))
        self.assertEqual("Static Value", tc._t.get_entry(tc, 'static_method'))
        self.assertEqual("Regular Value", tc._t.get_entry(tc, 'regular_method'))
        self.assertEqual("Constant Function", tc._t.get_entry(tc, 'const_f'))
        self.assertEqual(1173, tc._t.get_entry(tc, 'const'))
        with self.assertRaises(AttributeError):
            tc._t.get_entry(tc, 'foo')
        self.assertEqual(OrderedDict([
             ('class_method', 'Class Value'),
             ('static_method', 'Static Value'),
             ('regular_method', 'Regular Value'),
             ('const_f', 'Constant Function'),
             ('const', 1173)]), tc._t.freeze(tc))
        self.assertEqual(DynElements._delimiter.join(['class_method', 'static_method', 'regular_method',
                                                      'const_f', 'const']), tc._t.header)

    def test_inheritence(self):
        oc = OneClass()
        mc = MiddleClass()
        ic = InnerClass()
        self.assertEqual('class_method\tstatic_method\tregular_method\tconst_f\tconst', oc._t.header)
        self.assertEqual('another_method\t' + oc._t.header, mc._t.header)
        self.assertEqual('yet_another_method\t' + mc._t.header, ic._t.header)

        self.assertEqual('YA', ic._t.get_entry(ic, 'another_method'))
        self.assertEqual('Another Value', mc._t.get_entry(mc, 'another_method'))
        with self.assertRaises(AttributeError):
            oc._t.get_entry(oc, 'another_method')
        self.assertEqual(OrderedDict([
             ('yet_another_method', 'YAM'),
             ('another_method', 'YA'),
             ('class_method', 'Middle Class Value'),
             ('static_method', 'Static Value'),
             ('regular_method', 'Regular Value'),
             ('const_f', 'Constant Function'),
             ('const', 1173)]), ic._t.freeze(ic))
        self.assertEqual(OrderedDict([
             ('another_method', 'Another Value'),
             ('class_method', 'Middle Class Value'),
             ('static_method', 'Static Value'),
             ('regular_method', 'Regular Value'),
             ('const_f', 'Constant Function'),
             ('const', 1173)]), mc._t.freeze(mc))
        self.assertEqual(OrderedDict([
             ('class_method', 'Class Value'),
             ('static_method', 'Static Value'),
             ('regular_method', 'Regular Value'),
             ('const_f', 'Constant Function'),
             ('const', 1173)]), oc._t.freeze(oc))


class DynamicObjTestCase(unittest.TestCase):

    def test_base(self):

        class t1(DynObject):
            _t = DynElements()
            clsv = "Class value"

            def __init__(self, v):
                self._v = v

            @DynObject.entry(_t)
            @staticmethod
            def v1():
                return "Static value"

            @DynObject.entry(_t)
            @classmethod
            def v2(cls):
                return cls.clsv

            @DynObject.entry(_t)
            def v3(self):
                return self._v

            _t.add_const('v4', "Constant")
            _t.add_func(const_f)

        t = t1("Instance value")
        self.assertEqual("Static value", t.v1)
        self.assertEqual("Class value", t.v2)
        self.assertEqual("Instance value", t.v3)
        self.assertEqual("Constant", t.v4)
        self.assertEqual("Constant Function", t.const_f)
        with self.assertRaises(AttributeError):
            _ = t.v6
        self.assertEqual(OrderedDict([
             ('v1', 'Static value'),
             ('v2', 'Class value'),
             ('v3', 'Instance value'),
             ('v4', 'Constant'),
             ('const_f', 'Constant Function')]), t._freeze())
        self.assertEqual("DynObject(v1:'Static value', v2:'Class value', v3:'Instance value', v4:"
                         "'Constant', const_f:'Constant Function')", str(t))
        self.assertEqual('Static value\tClass value\tInstance value\tConstant\tConstant Function', repr(t))
        self.assertEqual('v1\tv2\tv3\tv4\tconst_f', t._header())

    def test_inheritence(self):
        class t1(DynObject):
            _t = DynElements()
            clsv = "Class value"

            def __init__(self, v):
                self._v = v

            @DynObject.entry(_t)
            @staticmethod
            def v1():
                return "Static value"

            @DynObject.entry(_t)
            @classmethod
            def v2(cls):
                return cls.clsv

            @DynObject.entry(_t)
            def v3(self):
                return self._v

            _t.add_const('v4', "Constant")
            _t.add_func(const_f)

        class t2(t1):
            _t = DynElements(t1)

            def __init__(self, v):
                super().__init__(v)

            @DynObject.entry(_t)
            @classmethod
            def v3(cls):
                return "Overridden"

            @DynObject.entry(_t)
            def v8(self):
                return self._v

        t = t2("Instance value")
        self.assertEqual("Static value", t.v1)
        self.assertEqual("Class value", t.v2)
        self.assertEqual("Overridden", t.v3)
        self.assertEqual("Constant", t.v4)
        self.assertEqual("Constant Function", t.const_f)
        self.assertEqual("Instance value", t.v8)
        with self.assertRaises(AttributeError):
            _ = t.v6
        self.assertEqual(OrderedDict([('v8', 'Instance value'),
                                      ('v1', 'Static value'),
                                      ('v2', 'Class value'),
                                      ('v3', 'Overridden'),
                                      ('v4', 'Constant'),
                                      ('const_f', 'Constant Function')]), t._freeze())
        self.assertEqual("DynObject(v8:'Instance value', v1:'Static value', v2:'Class value', v3:'Overridden', v4:"
                         "'Constant', const_f:'Constant Function')", str(t))
        self.assertEqual('Instance value\tStatic value\tClass value\tOverridden\tConstant\tConstant Function', repr(t))
        self.assertEqual('v8\tv1\tv2\tv3\tv4\tconst_f', t._header())

    def test_overrides(self):
        class t1(DynObject):
            _t = DynElements()
            clsv = "Class value"

            def __init__(self, v2):
                self._v = v2

            @DynObject.entry(_t)
            @staticmethod
            def v1():
                return "Static value"

            @DynObject.entry(_t)
            @classmethod
            def v2(cls):
                return cls.clsv

            @DynObject.entry(_t)
            def v3(self):
                return self._v

            _t.add_const('v4', "Constant")
            _t.add_func(const_f)

        v = t1("Test")
        self.assertEqual("Test", v.v3)
        t1.v3 = "Overridden"
        self.assertEqual("Overridden", v.v3)
        v._t.clear_overrides()
        self.assertEqual("Test", v.v3)

    def test_instance_setting(self):
        class t1(DynObject):
            _t = DynElements()

            @DynObject.entry(_t)
            def clsv(self):
                return "Untested"

        v = t1()

        with self.assertRaises(ValueError):
            v.clsv = "Test"
        t1.clsv = "Test"
        self.assertEqual("Test", v.clsv)

    def test_null_text(self):
        """
        There are issues in loading null fields in the pycharm table loader.  _null_text allows you to change
        the setting of the nulled out fields.
        :return:
        """
        class t1(DynObject):
            _t = DynElements()

            @DynObject.entry(_t)
            def clsv(self):
                return None

        v = t1()

        self.assertEqual('', repr(v))
        t1._null_text = "<null>"
        self.assertEqual('<null>', repr(v))


if __name__ == '__main__':
    unittest.main()
