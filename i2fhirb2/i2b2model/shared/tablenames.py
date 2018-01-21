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

# TODO: The mapping portion of this function should be loaded from the i2b2 table mapping table
from typing import List

DEFAULT_ONTOLOGY_TABLE = "custom_meta"      # Default metadata ontology table


class _I2B2Tables:
    _funcs = {"phys_name", "all_tables"}

    def __init__(self) -> None:
        self.concept_dimension = None
        self.modifier_dimension = None
        self.table_access = None
        self.observation_fact = None
        self.ontology_table = DEFAULT_ONTOLOGY_TABLE
        self.patient_dimension = None
        self.patient_mapping = None
        self.visit_dimension = None
        self.provider_dimension = None
        self.encounter_mapping = None

    def __getattribute__(self, item):
        """ Return the logical name of a table  """
        if item.startswith("_") or item not in self.__dict__:
            return super().__getattribute__(item)
        return self.__dict__[item] if item in _I2B2Tables._funcs else item

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def _clear(self):
        for k in self.all_tables():
            setattr(self, k, None if k != 'ontology_table' else DEFAULT_ONTOLOGY_TABLE)

    def phys_name(self, item: str) -> str:
        """Return the physical (mapped) name of item.

        :param item: logical table name
        :return: physical name of table
        """
        v = self.__dict__[item]
        return v if v is not None else item

    def all_tables(self) -> List[str]:
        """
        List of all known tables
        :return:
        """
        return sorted([k for k in self.__dict__.keys()
                       if k not in _I2B2Tables._funcs and not k.startswith("_")])


i2b2tablenames = _I2B2Tables()
