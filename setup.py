#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from os import path


from jupyter_packaging import (
    get_version,
    wrap_installers,
    npm_builder,
    get_data_files
)

from setuptools import setup, find_packages


HERE = path.dirname(path.abspath(__file__))

# The name of the project
name = 'ipycanvas'

# Get our version
version = get_version(path.join(name, '_version.py'))

nb_path = path.join(HERE, name, 'nbextension', 'static')
lab_path = path.join(HERE, name, 'labextension')

# Representative files that should exist after a successful build
ensured_targets = [
    path.join(nb_path, 'index.js'),
    path.join(lab_path, 'package.json'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/ipycanvas',
        nb_path, '*.js*'),
    ('share/jupyter/labextensions/ipycanvas', lab_path, '**'),
    ('etc/jupyter/nbconfig/notebook.d', HERE, 'ipycanvas.json')
]

post_develop = npm_builder(
    npm="yarn", build_cmd="build:extensions",
    source_dir="src", build_dir=lab_path
)

cmdclass = wrap_installers(
    post_develop=post_develop,
    ensured_targets=ensured_targets
)

setup_args = dict(
    version=version,
    cmdclass=cmdclass,
    data_files=get_data_files(data_files_spec),
    packages=find_packages()
)

if __name__ == '__main__':
    setup(**setup_args)
