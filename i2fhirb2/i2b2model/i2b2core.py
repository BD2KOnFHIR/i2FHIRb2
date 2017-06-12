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
from datetime import datetime
from typing import Optional

from i2fhirb2.sqlsupport.dynobject import DynObject, DynElements, DynamicPropType


class I2B2_Core(DynObject):
    _t = DynElements()

    def __init__(self,
                 update_date: Optional[DynamicPropType] = None,
                 download_date: Optional[DynamicPropType] = None,
                 sourcesystem_cd: Optional[DynamicPropType] = None,
                 import_date: Optional[DynamicPropType] = None):
        self._update_date = update_date
        self._download_date = download_date
        self._sourcesystem_cd = sourcesystem_cd
        self._import_date = import_date

    @DynObject.entry(_t)
    def update_date(self):
        return self._resolve(self._update_date) if self._update_date is not None else datetime.now()

    @DynObject.entry(_t)
    def download_date(self):
        return self._resolve(self._download_date) if self._download_date is not None else self.update_date

    @DynObject.entry(_t)
    def import_date(self):
        return self._resolve(self._import_date) if self._import_date is not None else self.update_date

    @DynObject.entry(_t)
    def sourcesystem_cd(self):
        return self._resolve(self._sourcesystem_cd) if self._sourcesystem_cd is not None else "Unspecified"


class I2B2_Core_With_Upload_Id(I2B2_Core):
    _t = DynElements(I2B2_Core)

    def __init__(self,
                 upload_id: Optional[DynamicPropType] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._upload_id = upload_id

    DynObject._after_root(_t)

    @DynObject.entry(_t)
    def upload_id(self) -> Optional[int]:
        return self._resolve(self._upload_id)
