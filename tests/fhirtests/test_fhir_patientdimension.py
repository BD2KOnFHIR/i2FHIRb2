import os
import unittest
from collections import OrderedDict

import datetime

from dynprops import as_dict
from i2b2model.shared.i2b2core import I2B2Core, I2B2CoreWithUploadId

from tests.utils.crc_testcase import CRCTestCase
from rdflib import Graph, Literal, XSD

from tests.utils.connection_helper import connection_helper


class FHIRPatientDimensionTestCase(CRCTestCase):
    def test_load_ttl(self):
        """ Load an example patient and verify the resulting patient_dimension and mapping tables """
        from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
        from i2fhirb2.fhir.fhirspecific import FHIR

        I2B2Core.update_date = datetime.datetime(2017, 5, 25)
        I2B2CoreWithUploadId.upload_id = 12345

        g = Graph()
        g.load(os.path.abspath(os.path.join(os.path.split(__file__)[0], "data",  "patient-example.ttl")),
               format="turtle")
        s = FHIR['Patient/example']
        with self.sourcesystem_cd():
            I2B2Core.sourcesystem_cd = self._sourcesystem_cd
            pd_entry = FHIRPatientDimension(g, connection_helper().tables, s)
            rslt = as_dict(pd_entry.patient_dimension_entry)
            real_pat_num = rslt['patient_num']
            rslt['patient_num'] = 100000001
            bd = Literal("1974-12-25T14:35:45-05:00", datatype=XSD.dateTime).value
            self.assertEqual(OrderedDict([
                 ('patient_num', 100000001),
                 ('vital_status_cd', 'NH'),
                 ('birth_date', bd),
                 ('death_date', None),
                 ('sex_cd', 'M'),
                 ('age_in_years_num', 44),
                 ('language_cd', None),
                 ('race_cd', None),
                 ('marital_status_cd', None),
                 ('religion_cd', None),
                 ('zip_cd', '3999'),
                 ('statecityzip_path', 'Zip codes\\Vic\\PleasantVille\\3999\\'),
                 ('income_cd', None),
                 ('patient_blob', None),
                 ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 12345)]), rslt)

            self.assertEqual(2, len(pd_entry.patient_mappings.patient_mapping_entries))
            rslt = as_dict(pd_entry.patient_mappings.patient_mapping_entries[0])
            self.assertEqual(real_pat_num, rslt['patient_num'])
            rslt['patient_num'] = 100000001
            self.assertEqual(OrderedDict([
                 ('patient_ide', 'example'),
                 ('patient_ide_source', 'http://hl7.org/fhir/'),
                 ('patient_num', 100000001),
                 ('patient_ide_status', 'A'),
                 ('project_id', 'fhir'),
                 ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 12345)]), rslt)
            rslt = as_dict(pd_entry.patient_mappings.patient_mapping_entries[1])
            self.assertEqual(real_pat_num, rslt['patient_num'])
            self.assertEqual(str(real_pat_num), rslt['patient_ide'])
            rslt['patient_ide'] = '100000001'
            rslt['patient_num'] = 100000001
            self.assertEqual(OrderedDict([
                 ('patient_ide', '100000001'),
                 ('patient_ide_source', 'HIVE'),
                 ('patient_num', 100000001),
                 ('patient_ide_status', 'A'),
                 ('project_id', 'fhir'),
                 ('update_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('download_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('import_date', datetime.datetime(2017, 5, 25, 0, 0)),
                 ('sourcesystem_cd', self._sourcesystem_cd),
                 ('upload_id', 12345)]), rslt)

    def test_patient_death_dates(self):
        """ Test the various types of deathdates"""
        # TODO: This test needs to be completed
        from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
        from i2fhirb2.fhir.fhirspecific import FHIR

        g = Graph()
        g.load(os.path.join(os.path.split(os.path.abspath(__file__))[0], "data", "patient-example-deceased_bool.ttl"),
               format="turtle")
        s = FHIR['Patient/example']
        with self.sourcesystem_cd():
            I2B2Core.sourcesystem_cd = self._sourcesystem_cd
            pd_entry = FHIRPatientDimension(g, connection_helper().tables, s)
            self.assertEqual('ZD', pd_entry.patient_dimension_entry.vital_status_cd)
            self.assertIsNone(pd_entry.patient_dimension_entry.death_date)


if __name__ == '__main__':
    unittest.main()
