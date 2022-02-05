#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
import os
from os.path import join as pjoin
from os import path


from jupyter_packaging import (
    create_cmdclass, install_npm, ensure_targets,
    combine_commands,
    get_version, skip_if_exists
)

from setuptools import setup, find_packages


HERE = path.dirname(path.abspath(__file__))

# The name of the project
name = 'ipycanvas'

# Get our version
version = get_version(pjoin(name, '_version.py'))

nb_path = pjoin(HERE, name, 'nbextension', 'static')
lab_path = pjoin(HERE, name, 'labextension')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(nb_path, 'index.js'),
    pjoin(lab_path, 'package.json'),
]

package_data_spec = {
    name: [
        'nbextension/static/*.*js*',
        'labextension/**'
    ]
}

data_files_spec = [
    ('share/jupyter/nbextensions/ipycanvas',
        nb_path, '*.js*'),
    ('share/jupyter/labextensions/ipycanvas', lab_path, '**'),
    ('etc/jupyter/nbconfig/notebook.d', HERE, 'ipycanvas.json')
]


cmdclass = create_cmdclass('jsdeps', package_data_spec=package_data_spec,
    data_files_spec=data_files_spec)
js_command = combine_commands(
    install_npm(HERE, npm=["yarn"], build_cmd='build:extensions'),
    ensure_targets(jstargets),
)

is_repo = os.path.exists(os.path.join(HERE, '.git'))
if is_repo:
    cmdclass['jsdeps'] = js_command
else:
    cmdclass['jsdeps'] = skip_if_exists(jstargets, js_command)

setup_args = dict(
    name=name,
    description='Interactive widgets library exposing the browser\'s Canvas API',
    version=version,
    scripts=glob(pjoin('scripts', '*')),
    cmdclass=cmdclass,
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Framework :: Jupyter',
    ],
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.6.0',
        'pillow>=6.0',
        'numpy'
    ],
    extras_require={},
    entry_points={},
)

if __name__ == '__main__':
    setup(**setup_args)
