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
from typing import Optional, List, Tuple, Callable, Dict

from sqlalchemy import Table, and_, update, delete, select
from sqlalchemy.engine import Connection

from i2fhirb2.i2b2model.shared.listchunker import ListChunker
from i2fhirb2.sqlsupport.dynobject import DynObject, DynElements, DynamicPropType


class I2B2Core(DynObject):
    _t = DynElements()
    _check_dups = False

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


class I2B2CoreWithUploadId(I2B2Core):
    _t = DynElements(I2B2Core)

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
        """
        Remove all table records with the supplied upload_id
        :param conn: sql connection
        :param table: table to modify
        :param upload_id: target upload_id
        :return: number of records removed
        """
        return conn.execute(delete(table).where(table.c.upload_id == upload_id)).rowcount if upload_id else 0

    @staticmethod
    def _delete_sourcesystem_cd(conn: Connection, table: Table, sourcesystem_cd: str) -> int:
        """
        Remove all table records with the supplied upload_id
        :param conn: sql connection
        :param table: table to modify
        :param sourcesystem_cd: target sourcesystem code
        :return: number of records removed
        """
        return conn.execute(delete(table).where(table.c.sourcesystem_cd == sourcesystem_cd)).rowcount \
            if sourcesystem_cd else 0

    @staticmethod
    def _nested_fcn(f: Callable, filters: List):
        """
        Distribute binary function f across list L
        :param f: Binary function
        :param filters: function arguments
        :return: chain of binary filters
        """
        return None if len(filters) == 0 \
            else filters[0] if len(filters) == 1 \
            else f(filters[0], I2B2CoreWithUploadId._nested_fcn(f, filters[1:]))

    @classmethod
    def _check_for_dups(cls, records: List["I2B2CoreWithUploadId"]) -> \
            Dict[Tuple, List["I2B2CoreWithUploadId"]]:
        key_map = dict()    # type: Dict[Tuple, I2B2CoreWithUploadId]
        dups = dict()       # type: Dict[Tuple, List[I2B2CoreWithUploadId]]
        for record in records:
            key = tuple(record.get(k) for k in cls.key_fields)
            if key in key_map:
                dups.setdefault(key, [key_map[key]]).append(record)
            else:
                key_map[key] = record
        return dups

    @classmethod
    def _add_or_update_records(cls, conn: Connection, table: Table,
                               records: List["I2B2CoreWithUploadId"]) -> Tuple[int, int]:
        """
        Add or update the supplied table as needed to reflect the contents of records
        :param table: i2b2 sql connection
        :param records: records to apply
        :return: number of records added / modified
        """
        num_updates = 0
        num_inserts = 0
        inserts = []
        # Iterate over the records doing updates
        # Note: This is slow as molasses - definitely not optimal for batch work, but hopefully we'll be dealing with
        #    thousands to tens of thousands of records.  May want to move to ORM model if this gets to be an issue
        for record in records:
            keys = [(table.c[k] == getattr(record, k)) for k in cls.key_fields]
            key_filter = I2B2CoreWithUploadId._nested_fcn(and_, keys)
            rec_exists = conn.execute(select([table.c.upload_id]).where(key_filter)).rowcount
            if rec_exists:
                known_values = {k: v for k, v in record._freeze().items()
                                if v is not None and k not in cls.no_update_fields and
                                k not in cls.key_fields}
                vals = [table.c[k] != v for k, v in known_values.items()]
                val_filter = I2B2CoreWithUploadId._nested_fcn(or_, vals)
                known_values['update_date'] = record.update_date
                upd = update(table).where(and_(key_filter, val_filter)).values(known_values)
                num_updates += conn.execute(upd).rowcount
            else:
                inserts.append(record._freeze())
        if inserts:
            if cls._check_dups:
                dups = cls._check_for_dups(inserts)
                nprints = 0
                # TODO: Figure out why duplicates are occuring -- they are very specific
                if dups:
                    print("{} duplicate records encountered".format(len(dups)))
                    for k, vals in dups.items():
                        if len(vals) == 2 and vals[0] == vals[1]:
                            inserts.remove(vals[1])
                        else:
                            if nprints < 20:
                                print("Key: {} has a non-identical dup".format(k))
                            elif nprints == 20:
                                print(".... more ...")
                            nprints += 1
                            for v in vals[1:]:
                                inserts.remove(v)
            # TODO: refactor this to load on a per-resource basis.  Temporary fix
            for insert in ListChunker(inserts, 500):
                num_inserts += conn.execute(table.insert(), insert).rowcount
        return num_inserts, num_updates
