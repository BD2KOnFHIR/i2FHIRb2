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


class StatusCodeErrorsTestCase(unittest.TestCase):
    """
    The ability to accidentally say "visit_dim_record._active_status_code._date = ..." produces undetected errors.
    Fixed and this validates it
    """
    def test_active_status_code(self):
        from i2b2model.data.i2b2visitdimension import ActiveStatusCd
        active_status_code = ActiveStatusCd(ActiveStatusCd.sd_day, ActiveStatusCd.ed_ongoing)
        self.assertEqual("OD", active_status_code.code)
        with self.assertRaises(ValueError):
            active_status_code._date = 1
        active_status_code.startcode = ActiveStatusCd.sd_ongoing
        active_status_code.endcode = ActiveStatusCd.ed_year
        self.assertEqual("XA", active_status_code.code)

    def test_vital_status_code(self):
        from i2b2model.data.i2b2patientdimension import VitalStatusCd
        vital_status_code = VitalStatusCd(VitalStatusCd.bd_unknown, VitalStatusCd.dd_living)
        self.assertEqual("NL", vital_status_code.code)
        with self.assertRaises(ValueError):
            vital_status_code._date = 1
        vital_status_code.birthcode = VitalStatusCd.bd_day
        vital_status_code.deathcode = VitalStatusCd.dd_deceased
        self.assertEqual("ZD", vital_status_code.code)


if __name__ == '__main__':
    unittest.main()
