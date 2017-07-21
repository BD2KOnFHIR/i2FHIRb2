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

from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension, VitalStatusCd


class PatientDimensionTestCase(unittest.TestCase):
    def test_basics(self):
        PatientDimension.update_date = datetime(2017, 1, 3)
        x = PatientDimension(12345, VitalStatusCd(VitalStatusCd.bd_unknown, VitalStatusCd.dd_unknown))
        self.assertEqual('patient_num\tvital_status_cd\tbirth_date\tdeath_date\tsex_cd\tage_in_years_num\tlanguage_cd\t'
                         'race_cd\tmarital_status_cd\treligion_cd\tzip_cd\tstatecityzip_path\tincome_cd\tpatient_blob\t'
                         'update_date\tdownload_date\timport_date\tsourcesystem_cd\tupload_id', x._header())
        self.assertEqual(OrderedDict([
             ('patient_num', 12345),
             ('vital_status_cd', 'UL'),
             ('birth_date', None),
             ('death_date', None),
             ('sex_cd', None),
             ('age_in_years_num', None),
             ('language_cd', None),
             ('race_cd', None),
             ('marital_status_cd', None),
             ('religion_cd', None),
             ('zip_cd', None),
             ('statecityzip_path', None),
             ('income_cd', None),
             ('patient_blob', None),
             ('update_date', datetime(2017, 1, 3, 0, 0)),
             ('download_date', datetime(2017, 1, 3, 0, 0)),
             ('import_date', datetime(2017, 1, 3, 0, 0)),
             ('sourcesystem_cd', 'Unspecified'),
             ('upload_id', None)]), x._freeze())
        x._birth_date = datetime(1955, 8, 10)
        x._death_date =  datetime(2017, 9, 11)
        x.birth = VitalStatusCd.bd_day
        x.death = VitalStatusCd.dd_deceased
        x._sex_cd = "M"
        x._age_in_years = 62
        x._language_cd = 'english'
        x._race_cd = 'white'
        x._marital_status_cd = 'married'
        x._religion_cd = 'atheist'
        x._zip_cd = "55901-0138"
        x._statecityzip_path = 'Zip codes\\Minnesota\\Rochester\\55901\\'
        x._income_cd = "Medium"
        x._patient_blob = "<div>some text</div>"
        self.assertEqual(OrderedDict([('patient_num', 12345),
             ('vital_status_cd', 'UL'),
             ('birth_date', datetime(1955, 8, 10, 0, 0)),
             ('death_date', datetime(2017, 9, 11, 0, 0)),
             ('sex_cd', 'M'),
             ('age_in_years_num', None),
             ('language_cd', 'english'),
             ('race_cd', 'white'),
             ('marital_status_cd', 'married'),
             ('religion_cd', 'atheist'),
             ('zip_cd', '55901-0138'),
             ('statecityzip_path', 'Zip codes\\Minnesota\\Rochester\\55901\\'),
             ('income_cd', 'Medium'),
             ('patient_blob', '<div>some text</div>'),
             ('update_date', datetime(2017, 1, 3, 0, 0)),
             ('download_date', datetime(2017, 1, 3, 0, 0)),
             ('import_date', datetime(2017, 1, 3, 0, 0)),
             ('sourcesystem_cd', 'Unspecified'),
             ('upload_id', None)]), x._freeze())


if __name__ == '__main__':
    unittest.main()
