#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

"""
Information about the frontend package of the widgets.
"""

from ._version import __version__

major, minor, *_ = __version__.split('.')

module_name = "ipycanvas"
module_version = f"^{major}.{minor}"
