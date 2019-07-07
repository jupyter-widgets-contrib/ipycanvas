#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

from ipywidgets import Color, DOMWidget

from traitlets import Tuple, Unicode, Float
from traittypes import Array
from base64 import b64encode
import warnings

from ._frontend import module_name, module_version

try:
    from io import BytesIO as StringIO  # python3
except:
    from StringIO import StringIO  # python2


try:
    import numpy as np
except:
    pass

warning_printed = False

# Code extracted from maartenbreddels ipyvolume
def array_to_binary(ar, obj=None, force_contiguous=True):
    global warning_printed

    if ar is None:
        return None
    if ar.dtype != np.uint8:  # JS does not support int64
        if not warning_printed:
            print("Forcing dtype to uint8! (Warning printed only once)")
            warning_printed = True
        ar = ar.astype(np.uint8)
    if ar.ndim == 1:
        ar = ar[np.newaxis, :]
    if ar.ndim == 2:
        # extend grayscale to RGBA
        add_alpha = np.full((ar.shape[0], ar.shape[1], 4), 255, dtype=np.uint8)
        add_alpha[:, :, :3] = np.repeat(ar[:, :, np.newaxis], repeats=3, axis=2)
        ar = add_alpha
    if ar.ndim != 3:
        raise ValueError("Please supply an RGBA array with shape (width, height, 4).")
    if ar.shape[2] != 4 and ar.shape[2] == 3:
        add_alpha = np.full((ar.shape[0], ar.shape[1], 4), 255, dtype=np.uint8)
        add_alpha[:, :, :3] = ar
        ar = add_alpha
    if force_contiguous and not ar.flags["C_CONTIGUOUS"]:  # make sure it's contiguous
        ar = np.ascontiguousarray(ar, dtype=np.uint8)
    return {'buffer': memoryview(ar), 'dtype': str(ar.dtype), 'shape': ar.shape}


def binary_to_array(value, obj=None):
    return np.frombuffer(value['data'], dtype=value['dtype']).reshape(value['shape'])


ndarray_serialization = dict(to_json=array_to_binary, from_json=binary_to_array)


class Canvas(DOMWidget):
    _model_name = Unicode('CanvasModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('CanvasView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    size = Tuple((700, 500), help='Size of the Canvas, this is not equal to the size of the view').tag(sync=True)

    image = Array(default_value=None, allow_none=True).tag(sync=True, **ndarray_serialization)

    fill_style = Color('black').tag(sync=True)
    stroke_style = Color('black').tag(sync=True)
    global_alpha = Float(1.0).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        self.layout.width = str(self.size[0]) + 'px'
        self.layout.height = str(self.size[1]) + 'px'

    # Rectangles methods
    def fill_rect(self, x, y, width, height):
        """Draw a filled rectangle."""
        self._send_canvas_command('fillRect', x, y, width, height)

    def stroke_rect(self, x, y, width, height):
        """Draw a rectangular outline."""
        self._send_canvas_command('strokeRect', x, y, width, height)

    def clear_rect(self, x, y, width, height):
        """Clear the specified rectangular area, making it fully transparent."""
        self._send_canvas_command('clearRect', x, y, width, height)

    def rect(self, x, y, width, height):
        """Draw a rectangle whose top-left corner is specified by (x, y) with the specified width and height."""
        self._send_canvas_command('rect', x, y, width, height)

    # Paths methods
    def begin_path(self):
        self._send_canvas_command('beginPath')

    def close_path(self):
        self._send_canvas_command('closePath')

    def stroke(self):
        self._send_canvas_command('stroke')

    def fill(self):
        self._send_canvas_command('fill')

    def move_to(self, x, y):
        self._send_canvas_command('moveTo', x, y)

    def line_to(self, x, y):
        self._send_canvas_command('lineTo', x, y)

    def arc(self, x, y, radius, start_angle, end_angle, anticlockwise):
        self._send_canvas_command('arc', x, y, radius, start_angle, end_angle, anticlockwise)

    def arc_to(self, x1, y1, x2, y2, radius):
        self._send_canvas_command('arcTo', x1, y1, x2, y2, radius)

    def quadratic_curve_to(self, cp1x, cp1y, x, y):
        self._send_canvas_command('quadraticCurveTo', cp1x, cp1y, x, y)

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        self._send_canvas_command('bezierCurveTo', cp1x, cp1y, cp2x, cp2y, x, y)

    def _send_canvas_command(self, name, *args):
        self.send({'name': name, 'args': args})
