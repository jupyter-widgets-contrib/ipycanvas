#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

from .canvas import Canvas, SketchyCanvas, MultiCanvas, MultiSketchyCanvas, hold_canvas  # noqa
from ._version import __version__, version_info  # noqa

from .nbextension import _jupyter_nbextension_paths  # noqa
