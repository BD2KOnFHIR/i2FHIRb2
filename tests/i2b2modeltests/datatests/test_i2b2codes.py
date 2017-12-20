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


class I2B2CodesTestCase(unittest.TestCase):

    def test_codes(self):
        from i2fhirb2.i2b2model.data.i2b2codes import I2B2DemographicsCodes
        self.assertEqual('DEM|AGE:-1', I2B2DemographicsCodes.age())
        self.assertEqual('DEM|AGE:17', I2B2DemographicsCodes.age(17))
        self.assertEqual('DEM|AGE:0', I2B2DemographicsCodes.age(0))
        self.assertEqual('DEM|DATE:birth', I2B2DemographicsCodes.birthdate)
        self.assertEqual('DEM|LANGUAGE:bulg', I2B2DemographicsCodes.language('bulg'))
        self.assertEqual('DEM|SEX:m', I2B2DemographicsCodes.sex_male)
        self.assertEqual('DEM|SEX:@', I2B2DemographicsCodes.sex_unknown)
        self.assertEqual('DEM|VITAL:y', I2B2DemographicsCodes.vital_dead)
        self.assertEqual('DEM|ZIP:55901', I2B2DemographicsCodes.zip(55901))

        self.assertEqual('DEM|SEX:m', I2B2DemographicsCodes().sex_male)


if __name__ == '__main__':
    unittest.main()
