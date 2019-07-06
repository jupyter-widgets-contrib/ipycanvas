#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

from ipywidgets import Color, DOMWidget

from traitlets import Float, Tuple, Unicode

from ._frontend import module_name, module_version


class Canvas(DOMWidget):
    _model_name = Unicode('CanvasModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('CanvasView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    size = Tuple((700, 500), help='Size of the Canvas, this is not equal to the size of the view').tag(sync=True)

    fill_style = Color('black').tag(sync=True)
    stroke_style = Color('black').tag(sync=True)
    global_alpha = Float(1.0).tag(sync=True)

    # Rectangles methods
    def fill_rect(self, x, y, width, height):
        """Draw a filled rectangle."""
        self._send_canvas_msg('fillRect', x, y, width, height)

    def stroke_rect(self, x, y, width, height):
        """Draw a rectangular outline."""
        self._send_canvas_msg('strokeRect', x, y, width, height)

    def clear_rect(self, x, y, width, height):
        """Clear the specified rectangular area, making it fully transparent."""
        self._send_canvas_msg('clearRect', x, y, width, height)

    def rect(self, x, y, width, height):
        """Draw a rectangle whose top-left corner is specified by (x, y) with the specified width and height."""
        self._send_canvas_msg('rect', x, y, width, height)

    # Paths methods
    def begin_path(self):
        self._send_canvas_msg('beginPath')

    def close_path(self):
        self._send_canvas_msg('closePath')

    def stroke(self):
        self._send_canvas_msg('stroke')

    def fill(self):
        self._send_canvas_msg('fill')

    def move_to(self, x, y):
        self._send_canvas_msg('moveTo', x, y)

    def line_to(self, x, y):
        self._send_canvas_msg('lineTo', x, y)

    def arc(self, x, y, radius, start_angle, end_angle, anticlockwise):
        self._send_canvas_msg('arc', x, y, radius, start_angle, end_angle, anticlockwise)

    def arc_to(self, x1, y1, x2, y2, radius):
        self._send_canvas_msg('arcTo', x1, y1, x2, y2, radius)

    def quadratic_curve_to(self, cp1x, cp1y, x, y):
        self._send_canvas_msg('quadraticCurveTo', cp1x, cp1y, x, y)

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        self._send_canvas_msg('bezierCurveTo', cp1x, cp1y, cp2x, cp2y, x, y)

    def _send_canvas_msg(self, msg_name, *args):
        self.send({'msg': msg_name, 'args': args})
