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

import datetime
from collections import OrderedDict


from i2fhirb2.fhir.fhirencountermapping import EncounterNumberGenerator
from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.common_cli_parameters import IDE_SOURCE_HIVE
from tests.utils.connection_helper import connection_helper


class FHIREncounterMappingTestCase(unittest.TestCase):

    def test_basic_mapping(self):
        """ Test the basic encounter mapping entry
        Process:
        1) Prime the EncounterMapping tables
        2) Generate a simple FHIR EncounterMapping entry and verify that two
           entries are generated - one for the number to external IDE and a second
           for the HIVE ide
        """
        from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
        from i2fhirb2.i2b2model.data.i2b2encountermapping import EncounterMapping

        EncounterMapping._clear()
        EncounterMapping.update_date = datetime.datetime(2017, 5, 25)
        EncounterMapping.sourcesystem_cd = "FHIR"
        FHIREncounterMapping._clear()

        em = FHIREncounterMapping(FHIR["Patient/f001"], "patient01", "http://hl7.org/fhir")
        self.assertEqual(OrderedDict([
             ('encounter_ide', 'Patient/f001'),
             ('encounter_ide_source', 'http://hl7.org/fhir/'),
             ('project_id', 'fhir'),
             ('encounter_num', 500000),
             ('patient_ide', 'patient01'),
             ('patient_ide_source', 'http://hl7.org/fhir'),
             ('encounter_ide_status', 'A'),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', None)]), em.encounter_mapping_entries[0]._freeze())
        self.assertEqual(OrderedDict([
             ('encounter_ide', '500000'),
             ('encounter_ide_source', IDE_SOURCE_HIVE),
             ('project_id', 'fhir'),
             ('encounter_num', 500000),
             ('patient_ide', 'patient01'),
             ('patient_ide_source', 'http://hl7.org/fhir'),
             ('encounter_ide_status', 'A'),
             ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', None)]), em.encounter_mapping_entries[1]._freeze())
        self.assertEqual(2, len(em.encounter_mapping_entries))
        self.assertEqual(500000, em.encounter_num)

    def test_encounternum_refresh(self):
        """ Test the EncounterNumberGenerator refresh function.
         Process:
         1) Create a couple of local (non-db) encounter numbers
         2) Do a refresh and show that the number gets set to something else
         3) Do a refresh ignoring an upload id and do the same
         """
        png = EncounterNumberGenerator(2000017)
        self.assertEqual(png.new_number(), 2000017)
        self.assertEqual(png.new_number(), 2000018)
        opts = connection_helper()
        png.refresh(opts.tables, None)
        print("Next encounter number: {}".format(png.new_number()))
        self.assertNotEqual(png.new_number(), 2000019)
        png.refresh(opts.tables, 4321)
        self.assertNotEqual(png.new_number(), 2000019)


if __name__ == '__main__':
    unittest.main()
