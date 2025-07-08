#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.


import sys
import os
from pathlib import Path
is_emscripten = sys.platform.startswith("emscripten")


from .canvas import (
    Path2D,
    Canvas,
    RoughCanvas,
    MultiCanvas,
    MultiRoughCanvas,
    hold_canvas,
)  # noqa
from ._version import __version__  # noqa

if is_emscripten:
    from . offscreen_canvas import OffscreenCanvasCore, OffscreenCanvas  # noqa


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
