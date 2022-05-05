#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

from .canvas import (
    Path2D,
    Canvas,
    RoughCanvas,
    MultiCanvas,
    MultiRoughCanvas,
    hold_canvas,
)  # noqa
from ._version import __version__, version_info  # noqa


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "nbextension/static",
            "dest": "ipycanvas",
            "require": "ipycanvas/extension",
        }
    ]


def _jupyter_labextension_paths():
    return [
        {
            "src": "labextension",
            "dest": "ipycanvas",
        }
    ]
