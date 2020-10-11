#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='melodia',
    version='1.1',
    description='Python library for MIDI music creation',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Egor Malykh',
    author_email='hello@meownoid.pro',
    url='https://github.com/meownoid/melodia',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'Typing :: Typed'
    ],
    keywords=[
        'music',
        'midi',
        'note',
        'track',
        'composer',
        'daw',
        'audio'
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
