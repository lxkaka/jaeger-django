#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open('README.md', 'rb') as fh:
    long_description = fh.read().decode('utf-8')

with open('requirements.txt', 'rb') as f:
    requirements = [_.decode('utf-8').strip() for _ in f.readlines() if _]

setup(
    name='jaeger-django',
    version='1.0.1',
    description='service tracing using jaeger in django project',
    author='lxkaka',
    author_email='linxiaoking@gamil.com',
    long_description=long_description,
    packages=find_packages(),
    license='Apache License 2.0',
    keywords='jaeger, tracing, django',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=requirements,
    test_suite='tests',
)
