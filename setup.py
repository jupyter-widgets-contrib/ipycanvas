#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
from os import path


from jupyter_packaging import (
    ensure_python,
    get_version,
    wrap_installers,
    npm_builder,
    get_data_files
)

from setuptools import setup, find_packages


HERE = path.dirname(path.abspath(__file__))

# The name of the project
name = 'ipycanvas'

# Ensure a valid python version
ensure_python('>=3.5')

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
    name=name,
    description='Interactive widgets library exposing the browser\'s Canvas API',
    version=version,
    scripts=glob(path.join('scripts', '*')),
    cmdclass=cmdclass,
    data_files=get_data_files(data_files_spec),
    packages=find_packages(),
    author='Martin Renou',
    author_email='martin.renou@gmail.com',
    url='https://github.com/martinRenou/ipycanvas',
    license='BSD',
    platforms="Linux, Mac OS X, Windows",
    keywords=['Jupyter', 'Widgets', 'IPython'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Jupyter',
    ],
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.6.0',
        'pillow>=6.0',
        'numpy',
        'orjson'
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
