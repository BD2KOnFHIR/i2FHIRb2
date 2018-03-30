from setuptools import setup, find_packages
from os import path

from i2fhirb2 import __version__


with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

requires = ['SQLAlchemy', 'rdflib', 'fhirtordf>=1.2.1', 'isodate', 'i2b2model>=0.2.4', 'dynprops>=0.2.1']
packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    name='i2FHIRb2',
    version=__version__,
    packages=packages,
    url='https://github.com/BD2KOnFHIR/i2FHIRb2',
    license='Apache 2.0',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='FHIR in i2b2 model conversion tools',
    long_description=long_description,
    install_requires=requires,
    scripts=['scripts/conf_file', 'scripts/generate_i2b2', 'scripts/loadfacts', 'scripts/removefacts'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Database',
        'Programming Language :: Python :: 3.6'
    ]
)
