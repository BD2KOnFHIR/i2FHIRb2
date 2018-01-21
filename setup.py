from setuptools import setup

import sys

from i2fhirb2 import __version__

requires = ['SQLAlchemy', 'python_dateutil', 'rdflib', 'psycopg2', 'jsonasobj>=1.1.1',
            'dirlistproc', 'fhirtordf>=0.9.3', 'isodate']
if sys.version_info < (3, 5):
    requires.append('typing')

setup(
    name='i2FHIRb2',
    version=__version__,
    packages=['tests', 'scripts', 'i2fhirb2', 'i2fhirb2.fhir', 'i2fhirb2.i2b2model', 'i2fhirb2.sqlsupport',
              'i2fhirb2.i2b2model.data', 'i2fhirb2.i2b2model.metadata', 'i2fhirb2.i2b2model.shared',
              'i2fhirb2.tsv_support', 'i2fhirb2.loaders'],
    url='https://github.com/BD2KOnFHIR/i2FHIRb2',
    license='Apache 2.0',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='FHIR in i2b2 model conversion tools',
    long_description='Toolkit to represent the "FHIR Ontology" in i2b2',
    install_requires=requires,
    scripts=['scripts/generate_i2b2', 'scripts/loadfacts', 'scripts/removefacts', 'scripts/conf_file'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Database',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
