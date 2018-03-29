
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
