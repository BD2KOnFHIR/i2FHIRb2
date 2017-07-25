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
from operator import or_
from typing import Optional, List, Tuple

from sqlalchemy import Table, and_, update, delete, select
from sqlalchemy.engine import Connection

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
    def update_date(self) -> datetime:
        return self._resolve(self._update_date) if self._update_date is not None else datetime.now()

    @DynObject.entry(_t)
    def download_date(self) -> datetime:
        return self._resolve(self._download_date) if self._download_date is not None else self.update_date

    @DynObject.entry(_t)
    def import_date(self) -> datetime:
        return self._resolve(self._import_date) if self._import_date is not None else self.update_date

    @DynObject.entry(_t)
    def sourcesystem_cd(self) -> str:
        return self._resolve(self._sourcesystem_cd) if self._sourcesystem_cd is not None else "Unspecified"


class I2B2_Core_With_Upload_Id(I2B2_Core):
    _t = DynElements(I2B2_Core)

    no_update_fields = ["update_date", "download_date", "import_date", "sourcesystem_cd", "upload_id"]
    key_fields = None

    def __init__(self,
                 upload_id: Optional[DynamicPropType] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._upload_id = upload_id

    DynObject._after_root(_t)

    @DynObject.entry(_t)
    def upload_id(self) -> Optional[int]:
        return self._resolve(self._upload_id)

    @staticmethod
    def _delete_upload_id(conn: Connection, table: Table, upload_id: int) -> int:
        if not upload_id:
            return 0
        else:
            q = delete(table).where(table.c.upload_id == upload_id)
            return conn.execute(q).rowcount

    @classmethod
    def _add_or_update_records(cls, conn: Connection, table: Table,
                               records: List["I2B2_Core_With_Upload_Id"]) -> Tuple[int, int]:
        num_updates = 0
        num_inserts = 0
        inserts = []
        # Iterate over the records doing updates
        # Note: This is slow as molasses - definitely not optimal for batch work, but hopefully we'll be dealing with
        #    thousands to tens of thousands of records.  May want to move to ORM model if this gets to be an issue
        for record in records:
            keys = [(table.c[k] == getattr(record, k)) for k in cls.key_fields]
            key_filter = and_(*keys) if len(keys) > 1 else keys[0]
            rec_exists = conn.execute(select([table.c.upload_id]).where(key_filter)).rowcount
            if rec_exists:
                known_values = {k: v for k, v in record._freeze().items()
                                if v is not None and k not in cls.no_update_fields and
                                k not in cls.key_fields}
                vals = [table.c[k] != v for k, v in known_values.items()]
                val_filter = or_(*vals) if len(vals) > 1 else vals[0]
                known_values['update_date'] = record.update_date
                upd = update(table).where(and_(key_filter, val_filter)).values(known_values)
                num_updates += conn.execute(upd).rowcount
            else:
                inserts.append(record._freeze())
        if inserts:
            num_inserts = conn.execute(table.insert(), inserts).rowcount
        return num_updates, num_inserts
