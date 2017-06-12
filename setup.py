from distutils.core import setup

import sys

requires = ['SQLAlchemy', 'python_dateutil', 'rdflib']
if sys.version_info < (3, 5):
    requires.append('typing')

setup(
    name='i2FHIRb2',
    version='0.0.1',
    packages=['tests', 'scripts', 'i2fhirb2', 'i2fhirb2.fhir', 'i2fhirb2.i2b2model', 'i2fhirb2.sqlsupport'],
    url='https://github.com/BD2KOnFHIR/i2FHIRb2',
    license='Apache 2.0',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='FHIR in i2b2 model conversion tools',
    long_description='Toolkit to represent the "FHIR Ontology" in i2b2',
    install_requires=requires,
    scripts=['scripts/generate_i2b2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License'
        'Topic :: Database',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
