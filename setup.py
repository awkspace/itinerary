#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

with open('version.txt') as version_file:
    version = version_file.read().split('\n')[0]

setup(
    name='itinerary',
    author='awk',
    author_email='awk@awk.space',
    version=version,
    description='A tool to apply pure SQL migrations to PostgreSQL' +
                'databases at runtime.',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/awkspace/itinerary',
    install_requires=requirements,
    packages=find_packages()
)
