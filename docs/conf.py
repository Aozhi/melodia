import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

project = 'melodia'
copyright = '2020, Egor Malykh'
author = 'Egor Malykh'
extensions = [
    'sphinx.ext.autodoc'
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'default'
html_static_path = ['_static']
master_doc = 'index'
