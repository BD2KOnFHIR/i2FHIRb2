
import unittest

import os

from fhirtordf.rdfsupport.namespaces import namespace_for, FHIR
from sqlalchemy import select, and_, or_

from i2b2model.sqlsupport.dbconnection import process_parsed_args
from tests.utils.fhir_graph import test_conf_directory

fhir_concept_prefix = namespace_for(FHIR).upper() + ':'
max_to_print = 100

# If this is true, the tests below are skipped
skip_tests = False

# Note: while the construct 'x == None' is technically incorrect, 'x is None' does not work in SQLAlchemy


class ConceptCoverageTestCase(unittest.TestCase):
    from i2fhirb2.generate_i2b2 import genargs
    conf_file = os.path.abspath(os.path.join(test_conf_directory, 'db_conf'))

    opts = genargs('-l --conf {} '.format(conf_file).split())
    process_parsed_args(opts, None)

    @unittest.skipIf(skip_tests, "Test skipped because data tables not loaded")
    def test_concept_coverage(self):
        """
        This test determines whether there are any concept codes in the observation fact table that don't have
        matching codes in the concept_dimension
        """
#         select count(distinct i2b2demodata.observation_fact.concept_cd)
#   from i2b2demodata.observation_fact left join i2b2demodata.concept_dimension on observation_fact.concept_cd
        # = concept_dimension.concept_cd where i2b2demodata.observation_fact.concept_cd like '%FHIR%' and
        # i2b2demodata.concept_dimension.concept_cd is null
# group by i2b2demodata.observation_fact.concept_cd;

        from i2b2model.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        s = select([x.observation_fact.c.concept_cd.distinct()]).\
            select_from(x.observation_fact.
                        join(x.concept_dimension, x.observation_fact.c.concept_cd ==
                             x.concept_dimension.c.concept_cd, isouter=True)).\
            where(and_(x.observation_fact.c.concept_cd.like(fhir_concept_prefix + '%'),
                       x.observation_fact.c.modifier_cd == '@',
                       x.concept_dimension.c.concept_cd is None))

        count = 0
        for e in x.crc_engine.execute(s).fetchall():
            if count < max_to_print:
                print("----> Orphan concept code: {}".format(e[0]))
            elif count == max_to_print:
                print("    ....     ")
            count += 1
        self.assertEqual(0, count, "Orphan concept codes in observation fact table")

    @unittest.skipIf(skip_tests, "Test skipped because data tables not loaded")
    def test_modifier_coverage(self):
        """
        This test determines whether there are any modifier codes in the observation fact table that don't have
        matching codes in the modifier_dimension
        """

        from i2b2model.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        s = select([x.observation_fact.c.modifier_cd.distinct()]).\
            select_from(x.observation_fact.
                        join(x.modifier_dimension, x.observation_fact.c.modifier_cd ==
                             x.modifier_dimension.c.modifier_cd, isouter=True)).\
            where(and_(x.observation_fact.c.modifier_cd.like(fhir_concept_prefix + '%'),
                       x.modifier_dimension.c.modifier_cd is None))

        count = 0
        for e in x.crc_engine.execute(s).fetchall():
            if count < max_to_print:
                print("----> Orphan modifier code: {}".format(e[0]))
            elif count == max_to_print:
                print("    ....     ")
            count += 1
        self.assertEqual(0, count, "Orphan concept codes in observation fact table")

    @unittest.skipIf(skip_tests, "Test skipped because data tables not loaded")
    def test_ontology_coverage_1(self):
        """
        Locate any ontology table concept references that aren't in the concept file.  Note that 'like' queries
        (which we don't currently emit) should probably produce values but don't require exact matches
        """
        from i2b2model.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        ont_table = x.ontology_table
        s = select([ont_table.c.c_dimcode.distinct()]). \
            select_from(ont_table.
                        join(x.concept_dimension, ont_table.c.c_dimcode ==
                             x.concept_dimension.c.concept_path, isouter=True)). \
            where(and_(ont_table.c.c_tablename == 'concept_dimension',
                       ont_table.c.c_columnname == 'concept_path',
                       ont_table.c.c_operator == '=',
                       ont_table.c.c_dimcode.like('%FHIR%'),
                       x.concept_dimension.c.concept_path is None))

        count = 0
        for e in x.crc_engine.execute(s).fetchall():
            if count < max_to_print:
                print("Orphan concept path: {}".format(e[0]))
            elif count == max_to_print:
                print("    ....     ")
            count += 1
        self.assertEqual(0, count, "Orphan concept codes in observation fact table")

    @unittest.skipIf(skip_tests, "Test skipped because data tables not loaded")
    def test_ontology_coverage_2(self):
        """
        Locate any concept file entries that don't have ontology table references
        """
        from i2b2model.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        ont_table = x.ontology_table
        s = select([x.concept_dimension.c.concept_path.distinct()]). \
            select_from(x.concept_dimension.
                        join(ont_table, x.concept_dimension.c.concept_path ==
                             ont_table.c.c_dimcode, isouter=True)). \
            where(and_(or_(ont_table.c.c_tablename == 'concept_dimension', ont_table.c.c_tablename is None),
                       or_(ont_table.c.c_columnname == 'concept_path', ont_table.c.c_columnname is None),
                       x.concept_dimension.c.concept_path.like('%FHIR%'),
                       ont_table.c.c_tablename is None))

        count = 0
        for e in x.crc_engine.execute(s).fetchall():
            if count < max_to_print:
                print("Orphan concept path: {}".format(e[0]))
            elif count == max_to_print:
                print("    ....     ")
            count += 1
        self.assertEqual(0, count, "Orphan concept codes in concept_dimension table")

    @unittest.skipIf(skip_tests, "Test skipped because data tables not loaded")
    def test_ontology_coverage_3(self):
        """
        Locate any ontology table modifier references that aren't in the modifier dimension
        """
        from i2b2model.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        ont_table = x.ontology_table
        s = select([ont_table.c.c_dimcode.distinct()]). \
            select_from(ont_table.
                        join(x.modifier_dimension, ont_table.c.c_dimcode ==
                             x.modifier_dimension.c.modifier_path, isouter=True)). \
            where(and_(ont_table.c.c_tablename == 'modifier_dimension',
                       ont_table.c.c_columnname == 'modifier_path',
                       ont_table.c.c_visualattributes == 'RA',
                       ont_table.c.c_dimcode.like('%FHIR%'),
                       x.modifier_dimension.c.modifier_path is None))

        count = 0
        for e in x.crc_engine.execute(s).fetchall():
            if count < max_to_print:
                print("Orphan modifier path: {}".format(e[0]))
            elif count == max_to_print:
                print("    ....     ")
            count += 1
        self.assertEqual(0, count, "Orphan modifier codes in observation fact table")

    @unittest.skipIf(skip_tests, "Test skipped because data tables not loaded")
    def test_ontology_coverage_4(self):
        """
        Determine whether there is a 1-1 mapping betwen the FHIR ontology and the dimension tables
        """
        from i2b2model.sqlsupport.dbconnection import I2B2Tables
        x = I2B2Tables(self.opts)

        ont_table = x.ontology_table
        s = select([x.modifier_dimension.c.modifier_path.distinct()]). \
            select_from(x.modifier_dimension.
                        join(ont_table, x.modifier_dimension.c.modifier_path ==
                             ont_table.c.c_dimcode, isouter=True)). \
            where(and_(or_(ont_table.c.c_tablename == 'modifier_dimension', ont_table.c.c_tablename is None),
                       or_(ont_table.c.c_columnname == 'modifier_path', ont_table.c.c_columnname is None),
                       x.modifier_dimension.c.modifier_path.like('%FHIR%'),
                       ont_table.c.c_tablename is None))        # see note at front of document

        count = 0
        for e in x.crc_engine.execute(s).fetchall():
            if count < max_to_print:
                print("Orphan modifier path: {}".format(e[0]))
            elif count == max_to_print:
                print("    ....     ")
            count += 1
        self.assertEqual(0, count, "Orphan modifier codes in modifier_dimension table")


if __name__ == '__main__':
    unittest.main()
