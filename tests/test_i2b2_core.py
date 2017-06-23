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
from datetime import datetime, timedelta

from i2fhirb2.i2b2model.i2b2core import I2B2_Core, I2B2_Core_With_Upload_Id
from tests.base_test_case import BaseTestCase


class I2B2CoreTestCase(BaseTestCase):

    def test_defaults(self):
        rtn = I2B2_Core()
        rtnf = rtn._freeze()
        self.assertAlmostNow(rtn.update_date)
        self.assertDatesAlmostEqual(rtn.update_date, rtnf['update_date'])
        self.assertAlmostNow(rtn.download_date)
        self.assertDatesAlmostEqual(rtn.download_date, rtnf['download_date'])
        self.assertAlmostNow(rtn.import_date)
        self.assertDatesAlmostEqual(rtn.import_date, rtnf['import_date'])
        self.assertEqual('Unspecified', rtn.sourcesystem_cd)
        self.assertEqual(rtn.sourcesystem_cd, rtnf['sourcesystem_cd'])
        self.assertEqual(['update_date', 'download_date', 'import_date', 'sourcesystem_cd'], list(rtnf.keys()))

        rtn = I2B2_Core()
        I2B2_Core.download_date = datetime(2009, 1, 1, 12, 0)
        I2B2_Core.sourcesystem_cd = "MASTER"
        I2B2_Core.import_date = datetime(2011, 1, 1, 12, 0)
        I2B2_Core.update_date = datetime.now() + timedelta(hours=2)
        self.assertEqual('2009-01-01 12:00:00', str(rtn.download_date))
        self.assertEqual('2011-01-01 12:00:00', str(rtn.import_date))
        self.assertEqual('MASTER', rtn.sourcesystem_cd)
        self.assertDatesAlmostEqual(rtn.update_date, str(datetime.now() + timedelta(hours=2)))

        I2B2_Core._clear()
        rtn = I2B2_Core_With_Upload_Id(upload_id=1777439)
        self.assertEqual('Unspecified', rtn.sourcesystem_cd)
        self.assertEqual(1777439, rtn.upload_id)
        self.assertEqual('update_date\tdownload_date\timport_date\tsourcesystem_cd\tupload_id', rtn._header())
        rtn = I2B2_Core()
        with self.assertRaises(AttributeError):
            _ = rtn.upload_id

    def test_settings(self):
        I2B2_Core._clear()
        rtn = I2B2_Core(sourcesystem_cd="abcd",
                        update_date=datetime(2014, 7, 31),
                        download_date=datetime.now)
        rtnf = rtn._freeze()
        self.assertEqual(str(rtnf['update_date']), '2014-07-31 00:00:00')
        self.assertAlmostNow(rtn.download_date)
        self.assertEqual(rtn.update_date, rtn.import_date)
        self.assertEqual(rtnf['sourcesystem_cd'], 'abcd')
        self.assertEqual('update_date\tdownload_date\timport_date\tsourcesystem_cd', rtn._header())


if __name__ == '__main__':
    unittest.main()
