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
from datetime import datetime


class VisitDimensionTestCase(unittest.TestCase):

    def test_basics(self):
        from i2fhirb2.i2b2model.data.i2b2visitdimension import VisitDimension, ActiveStatusCd
        VisitDimension._clear()
        VisitDimension.update_date = datetime(2017, 1, 3)
        VisitDimension.upload_id = 100143
        x = VisitDimension(500001, 10000017, ActiveStatusCd(ActiveStatusCd.sd_day,
                                                            ActiveStatusCd.ed_ongoing), datetime(2007, 10, 4))
        self.assertEqual(OrderedDict([
             ('encounter_num', 500001),
             ('patient_num', 10000017),
             ('active_status_cd', 'OD'),
             ('start_date', datetime(2007, 10, 4, 0, 0)),
             ('end_date', None),
             ('inout_cd', None),
             ('location_cd', None),
             ('location_path', None),
             ('length_of_stay', None),
             ('visit_blob', None),
             ('update_date', datetime(2017, 1, 3, 0, 0)),
             ('download_date', datetime(2017, 1, 3, 0, 0)),
             ('import_date', datetime(2017, 1, 3, 0, 0)),
             ('sourcesystem_cd', 'Unspecified'),
             ('upload_id', 100143)]), x._freeze())


if __name__ == '__main__':
    unittest.main()
