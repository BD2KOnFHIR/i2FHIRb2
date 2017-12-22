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
from collections import OrderedDict
from typing import Any, Dict, Tuple, Callable, Union, List, Type

DynamicPropType = Union[Type[classmethod], Type[staticmethod], Callable[[object], object], object]


class DynElements:
    """
    A map from an element name to either a function that returns an object or an object itself.
    :param parent: parent DynObject
    """
    _delimiter = '\t'

    def __init__(self, parent: Type["DynObject"]=None) -> None:
        """
        Construct a set of dynamic elements
        :param parent:
        """
        self.elements = OrderedDict()               # type: OrderedDict[str, Tuple[bool, DynamicPropType]]
        self.override_elements = OrderedDict()      # type: OrderedDict[str, Tuple[bool, DynamicPropType]]
        self.parent_dynelements = parent._t if parent else None

    def add(self, c: DynamicPropType) -> DynamicPropType:
        """
        Add an method to the set
        :param c: method to add
        :return: added method
        """
        fname = c.__func__.__name__ if isinstance(c, (classmethod, staticmethod)) else c.__name__
        self.elements[fname] = (True, c)
        return c

    def add_func(self, f: Callable[[], Any]) -> Callable[[], Any]:
        """
        Add a function to the set
        :param f: function to add
        :return: added function
        """
        self.elements[f.__name__] = (False, f)
        return f

    def add_const(self, name: str, c: Any) -> Any:
        """
        Add a constant to the set
        :param name:
        :param c:
        :return:
        """
        self.elements[name] = (False, c)
        return c

    def add_override_const(self, name: str, c: Any) -> Any:
        self.override_elements[name] = (False, c)
        return c

    def add_parents(self):
        """ Indicator to insert the parent dynelements here instead of at the end """
        self.elements[""] = (False, None)

    def clear_overrides(self):
        self.override_elements.clear()

    def clear_override(self, item):
        if item in self.override_elements:
            del(self.override_elements[item])

    def has_entry(self, name: str) -> bool:
        """
        Determine whether name is in the list
        :param name: name to test
        :return:
        """
        return name in self.elements or (self.parent_dynelements and self.parent_dynelements.has_entry(name))

    @staticmethod
    def resolve_entry(context: object, v: DynamicPropType, has_context: bool) -> Any:
        if isinstance(v, classmethod):
            return v.__func__(context)
        elif isinstance(v, staticmethod):
            return v.__func__()
        elif callable(v):
            return v(context) if has_context else v()
        return v

    def get_entry(self, context: object, name: str):
        if name in self.elements or name in self.override_elements:
            has_context, v = self.override_elements[name] if name in self.override_elements else self.elements[name]
            return self.resolve_entry(context, v, has_context)
        elif self.parent_dynelements:
            return self.parent_dynelements.get_entry(context, name)
        else:
            raise AttributeError("{} Not Found".format(name))

    def keys(self) -> List[str]:
        parent_keys = [k for k in self.parent_dynelements.keys()] if self.parent_dynelements else []
        rval = []
        for k in self.elements.keys():
            if k == "":
                rval += parent_keys
            elif k not in parent_keys:
                rval.append(k)
        if "" not in self.elements.keys():
            rval += parent_keys
        return rval

    def freeze(self, context: object) -> Dict[str, Any]:
        """
        Resolve all of the functions and return a set of values
        :param context: Reification context
        :return: ordered dictionary of reified results
        """
        return OrderedDict(**{k: self.get_entry(context, k) for k in self.keys()})

    @property
    def header(self):
        return self._delimiter.join(self.keys())


class DynObjectMetaClass(type):
    _t = None                   # type: DynElements

    def __setattr__(self, key, value):
        """
        Set a dynamic value.  This is always local - it will not replace the parent attribute
        """
        if self._t.has_entry(key):
            self._t.add_override_const(key, value)
        else:
            super().__setattr__(key, value)

    def __delitem__(self, item):
        """
        Remove an attribute from elements it it exists
        :param item:
        :return:
        """
        if self._t.has_entry(item):
            self._t.clear_override(item)
        else:
            super().__delattr__(item)


class DynObject(metaclass=DynObjectMetaClass):

    """
    A "Dynamic Object' - a class whose
    """
    _t = None           # type: DynElements
    _null_text = ''

    @staticmethod
    def entry(dynelements: DynElements) -> Callable[[object], Any]:
        def f(c: DynamicPropType):
            return dynelements.add(c)
        return f

    @classmethod
    def _clear(cls):
        cls._t.clear_overrides()

    def __setattr__(self, key, value):
        """
        Set a dynamic value.  This is always local - it will not replace the parent attribute
        """
        elements = super().__getattribute__('_t')
        if elements.has_entry(key):
            raise ValueError("Attributes must be changed on class level")
        else:
            super().__setattr__(key, value)

    def __getattribute__(self, item: str):
        """
        Translate distinguished elements into attributes
        :param item: name of item to retrieve
        :return: value for item
        """
        elements = super().__getattribute__('_t')
        if elements.has_entry(item):
            return elements.get_entry(self, item)
        else:
            return super().__getattribute__(item)

    def _freeze(self) -> Dict[str, Any]:
        """
        Return the distinguished list, removing all functional dependencies
        :return:
        """
        return self._t.freeze(self)

    @classmethod
    def _after_root(cls, dynelements: DynElements) -> None:
        dynelements.add_parents()

    @classmethod
    def _header(cls) -> str:
        return cls._t.header

    def _resolve(self, f: DynamicPropType) -> Any:
        return self._t.resolve_entry(self, f, False)

    @classmethod
    def _escape(cls, txt: str) -> str:
        return txt.replace(cls._t._delimiter, '\\' + cls._t._delimiter)

    def __str__(self):
        return "DynObject({})".format(', '.join(["{}:'{}'".format(k, getattr(self, k)) for k in self._t.keys()]))

    def __repr__(self):
        return self._t._delimiter.join(str(e) if e is not None else self._null_text for e in self._freeze().values())

    def __lt__(self, other):
        return repr(self) < repr(other)

    def __eq__(self, other):
        return repr(self) == repr(other)
