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
