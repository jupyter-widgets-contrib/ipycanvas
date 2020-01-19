#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

import warnings
from contextlib import contextmanager

import numpy as np

from traitlets import Bool, Bytes, CInt, Enum, Float, Instance, List, Unicode

from ipywidgets import CallbackDispatcher, Color, DOMWidget, Image, widget_serialization
from ipywidgets.widgets.trait_types import bytes_serialization

from ._frontend import module_name, module_version

from .utils import binary_image, populate_args, to_camel_case, image_bytes_to_array


class _CanvasBase(DOMWidget):
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    width = CInt(700).tag(sync=True)
    height = CInt(500).tag(sync=True)

    #: (bool) Specifies if the image should be synchronized from front-end to Python back-end
    sync_image_data = Bool(False).tag(sync=True)

    #: (bytes) Current image data as bytes (PNG encoded). It is ``None`` by default and will not be
    #: updated if ``sync_image_data`` is ``False``.
    image_data = Bytes(default_value=None, allow_none=True, read_only=True).tag(sync=True, **bytes_serialization)

    def to_file(self, filename):
        """Save the current Canvas image to a PNG file.

        This will raise an exception if there is no image to save (_e.g._ if ``image_data`` is ``None``).
        """
        if self.image_data is None:
            raise RuntimeError('No image data to save, please be sure that ``sync_image_data`` is set to True')
        if not filename.endswith('.png') and not filename.endswith('.PNG'):
            raise RuntimeError('Can only save to a PNG file')

        with open(filename, 'wb') as fobj:
            fobj.write(self.image_data)

    def get_image_data(self, x=0, y=0, width=None, height=None):
        """Return a NumPy array representing the underlying pixel data for a specified portion of the canvas.

        This will throw an error if there is no ``image_data`` to retrieve, this happens when nothing was drawn yet or
        when the ``sync_image_data`` attribute is not set to ``True``.
        The returned value is a NumPy array containing the image data for the rectangle of the canvas specified. The
        coordinates of the rectangle's top-left corner are (``x``, ``y``), while the coordinates of the bottom corner
        are (``x + width``, ``y + height``).
        """
        if self.image_data is None:
            raise RuntimeError('No image data, please be sure that ``sync_image_data`` is set to True')

        x = int(x)
        y = int(y)

        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y

        width = int(width)
        height = int(height)

        image_data = image_bytes_to_array(self.image_data)
        return image_data[y:y + height, x:x + width]

    @property
    def size(self):
        """Get the canvas size."""
        return (self.width, self.height)

    @size.setter
    def size(self, value):
        """Set the size of the canvas, this is deprecated, use width and height attributes instead."""
        warnings.warn(
            'size is deprecated and will be removed in a future release, please use width and height instead.',
            DeprecationWarning
        )
        (self.width, self.height) = value


class Canvas(_CanvasBase):
    """Create a Canvas widget.

    Args:
        width (int): The width (in pixels) of the canvas
        height (int): The height (in pixels) of the canvas
        caching (boolean): Whether commands should be cached or not
    """

    _model_name = Unicode('CanvasModel').tag(sync=True)
    _view_name = Unicode('CanvasView').tag(sync=True)

    #: (valid HTML color) The color for filling rectangles and paths. Default to ``'black'``.
    fill_style = Color('black')

    #: (valid HTML color) The color for rectangles and paths stroke. Default to ``'black'``.
    stroke_style = Color('black')

    #: (float) Transparency level. Default to ``1.0``.
    global_alpha = Float(1.0)

    #: (str) Font for the text rendering. Default to ``'12px serif'``.
    font = Unicode('12px serif')

    #: (str) Text alignment, possible values are ``'start'``, ``'end'``, ``'left'``, ``'right'``, and ``'center'``.
    #: Default to ``'start'``.
    text_align = Enum(['start', 'end', 'left', 'right', 'center'], default_value='start')

    #: (str) Text baseline, possible values are ``'top'``, ``'hanging'``, ``'middle'``, ``'alphabetic'``, ``'ideographic'``
    #: and ``'bottom'``.
    #: Default to ``'alphabetic'``.
    text_baseline = Enum(['top', 'hanging', 'middle', 'alphabetic', 'ideographic', 'bottom'], default_value='alphabetic')

    #: (str) Text direction, possible values are ``'ltr'``, ``'rtl'``, and ``'inherit'``.
    #: Default to ``'inherit'``.
    direction = Enum(['ltr', 'rtl', 'inherit'], default_value='inherit')

    #: (str) Global composite operation, possible values are listed below:
    #: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Compositing#globalCompositeOperation
    global_composite_operation = Enum(
        ['source-over', 'source-in', 'source-out', 'source-atop',
         'destination-over', 'destination-in', 'destination-out',
         'destination-atop', 'lighter', 'copy', 'xor', 'multiply',
         'screen', 'overlay', 'darken', 'lighten', 'color-dodge',
         'color-burn', 'hard-light', 'soft-light', 'difference',
         'exclusion', 'hue', 'saturation', 'color', 'luminosity'],
        default_value='source-over'
    )

    #: (float) Indicates the horizontal distance the shadow should extend from the object.
    #: This value isn't affected by the transformation matrix. The default is 0.
    shadow_offset_x = Float(0.0)

    #: (float) Indicates the vertical distance the shadow should extend from the object.
    #: This value isn't affected by the transformation matrix. The default is 0.
    shadow_offset_y = Float(0.0)

    #: (float) Indicates the size of the blurring effect; this value doesn't correspond to a number of pixels
    #: and is not affected by the current transformation matrix. The default value is 0.
    shadow_blur = Float(0.0)

    #: (valid HTML color) A standard CSS color value indicating the color of the shadow effect; by default,
    #: it is fully-transparent black.
    shadow_color = Color('rgba(0, 0, 0, 0)')

    #: (float) Sets the width of lines drawn in the future, must be a positive number. Default to ``1.0``.
    line_width = Float(1.0)

    #: (str) Sets the appearance of the ends of lines, possible values are ``'butt'``, ``'round'`` and ``'square'``.
    #: Default to ``'butt'``.
    line_cap = Enum(['butt', 'round', 'square'], default_value='butt')

    #: (str) Sets the appearance of the "corners" where lines meet, possible values are ``'round'``, ``'bevel'`` and ``'miter'``.
    #: Default to ``'miter'``
    line_join = Enum(['round', 'bevel', 'miter'], default_value='miter')

    #: (float) Establishes a limit on the miter when two lines join at a sharp angle, to let you control how thick
    #: the junction becomes. Default to ``10.``.
    miter_limit = Float(10.)

    _line_dash = List()

    #: (float) Specifies where to start a dash array on a line. Default is ``0.``.
    line_dash_offset = Float(0.)

    _client_ready_callbacks = Instance(CallbackDispatcher, ())

    _mouse_move_callbacks = Instance(CallbackDispatcher, ())
    _mouse_down_callbacks = Instance(CallbackDispatcher, ())
    _mouse_up_callbacks = Instance(CallbackDispatcher, ())
    _mouse_out_callbacks = Instance(CallbackDispatcher, ())

    _touch_start_callbacks = Instance(CallbackDispatcher, ())
    _touch_end_callbacks = Instance(CallbackDispatcher, ())
    _touch_move_callbacks = Instance(CallbackDispatcher, ())
    _touch_cancel_callbacks = Instance(CallbackDispatcher, ())

    def __init__(self, *args, **kwargs):
        """Create a Canvas widget."""
        #: Whether commands should be cached or not
        self.caching = kwargs.get('caching', False)
        self._commands_cache = []
        self._buffers_cache = []

        if 'size' in kwargs:
            size = kwargs['size']

            kwargs['width'] = size[0]
            kwargs['height'] = size[1]

            del kwargs['size']

            warnings.warn(
                'size is deprecated and will be removed in a future release, please use width and height instead.',
                DeprecationWarning
            )

        super(Canvas, self).__init__(*args, **kwargs)

        self.on_msg(self._handle_frontend_event)

    # Rectangles methods
    def fill_rect(self, x, y, width, height=None):
        """Draw a filled rectangle of size ``(width, height)`` at the ``(x, y)`` position."""
        if height is None:
            height = width

        self._send_canvas_command('fillRect', (x, y, width, height))

    def stroke_rect(self, x, y, width, height=None):
        """Draw a rectangular outline of size ``(width, height)`` at the ``(x, y)`` position."""
        if height is None:
            height = width

        self._send_canvas_command('strokeRect', (x, y, width, height))

    def fill_rects(self, x, y, width, height=None):
        """Draw filled rectangles of sizes ``(width, height)`` at the ``(x, y)`` positions.

        Where ``x``, ``y``, ``width`` and ``height`` arguments are NumPy arrays, lists or scalar values.
        If ``height`` is None, it is set to the same value as width.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(width, args, buffers)

        if height is None:
            args.append(args[-1])
        else:
            populate_args(height, args, buffers)

        self._send_canvas_command('fillRects', args, buffers)

    def stroke_rects(self, x, y, width, height=None):
        """Draw a rectangular outlines of sizes ``(width, height)`` at the ``(x, y)`` positions.

        Where ``x``, ``y``, ``width`` and ``height`` arguments are NumPy arrays, lists or scalar values.
        If ``height`` is None, it is set to the same value as width.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(width, args, buffers)

        if height is None:
            args.append(args[-1])
        else:
            populate_args(height, args, buffers)

        self._send_canvas_command('strokeRects', args, buffers)

    def clear_rect(self, x, y, width, height=None):
        """Clear the specified rectangular area of size ``(width, height)`` at the ``(x, y)`` position, making it fully transparent."""
        if height is None:
            height = width

        self._send_canvas_command('clearRect', (x, y, width, height))

    # Arc methods
    def fill_arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Draw a filled arc centered at ``(x, y)`` with a radius of ``radius``."""
        self._send_canvas_command('fillArc', (x, y, radius, start_angle, end_angle, anticlockwise))

    def stroke_arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Draw an arc outline centered at ``(x, y)`` with a radius of ``radius``."""
        self._send_canvas_command('strokeArc', (x, y, radius, start_angle, end_angle, anticlockwise))

    def fill_arcs(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Draw filled arcs centered at ``(x, y)`` with a radius of ``radius``.

        Where ``x``, ``y``, ``radius`` and other arguments are NumPy arrays, lists or scalar values.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(radius, args, buffers)
        populate_args(start_angle, args, buffers)
        populate_args(end_angle, args, buffers)
        args.append(anticlockwise)

        self._send_canvas_command('fillArcs', args, buffers)

    def stroke_arcs(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Draw an arc outlines centered at ``(x, y)`` with a radius of ``radius``.

        Where ``x``, ``y``, ``radius`` and other arguments are NumPy arrays, lists or scalar values.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(radius, args, buffers)
        populate_args(start_angle, args, buffers)
        populate_args(end_angle, args, buffers)
        args.append(anticlockwise)

        self._send_canvas_command('strokeArcs', args, buffers)

    # Paths methods
    def begin_path(self):
        """Call this method when you want to create a new path."""
        self._send_canvas_command('beginPath')

    def close_path(self):
        """Add a straight line from the current point to the start of the current path.

        If the shape has already been closed or has only one point, this function does nothing.
        This method doesn't draw anything to the canvas directly. You can render the path using the stroke() or fill() methods.
        """
        self._send_canvas_command('closePath')

    def stroke(self):
        """Stroke (outlines) the current path with the current ``stroke_style``."""
        self._send_canvas_command('stroke')

    def fill(self, rule='nonzero'):
        """Fill the current path with the current ``fill_style`` and given the rule.

        Possible rules are ``nonzero`` and ``evenodd``.
        """
        self._send_canvas_command('fill', (rule, ))

    def move_to(self, x, y):
        """Move the "pen" to the given ``(x, y)`` coordinates."""
        self._send_canvas_command('moveTo', (x, y))

    def line_to(self, x, y):
        """Add a straight line to the current path by connecting the path's last point to the specified ``(x, y)`` coordinates.

        Like other methods that modify the current path, this method does not directly render anything. To
        draw the path onto the canvas, you can use the fill() or stroke() methods.
        """
        self._send_canvas_command('lineTo', (x, y))

    def rect(self, x, y, width, height):
        """Draw a rectangle of size ``(width, height)`` at the ``(x, y)`` position in the current path."""
        self._send_canvas_command('rect', (x, y, width, height))

    def arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Create a circular arc centered at ``(x, y)`` with a radius of ``radius``.

        The path starts at ``start_angle`` and ends at ``end_angle``, and travels in the direction given by
        ``anticlockwise`` (defaulting to clockwise: ``False``).
        """
        self._send_canvas_command('arc', (x, y, radius, start_angle, end_angle, anticlockwise))

    def arc_to(self, x1, y1, x2, y2, radius):
        """Add a circular arc to the current path.

        Using the given control points ``(x1, y1)`` and ``(x2, y2)`` and the ``radius``.
        """
        self._send_canvas_command('arcTo', (x1, y1, x2, y2, radius))

    def quadratic_curve_to(self, cp1x, cp1y, x, y):
        """Add a quadratic Bezier curve to the current path.

        It requires two points: the first one is a control point and the second one is the end point.
        The starting point is the latest point in the current path, which can be changed using move_to()
        before creating the quadratic Bezier curve.
        """
        self._send_canvas_command('quadraticCurveTo', (cp1x, cp1y, x, y))

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        """Add a cubic Bezier curve to the current path.

        It requires three points: the first two are control points and the third one is the end point.
        The starting point is the latest point in the current path, which can be changed using move_to()
        before creating the Bezier curve.
        """
        self._send_canvas_command('bezierCurveTo', (cp1x, cp1y, cp2x, cp2y, x, y))

    # Text methods
    def fill_text(self, text, x, y, max_width=None):
        """Fill a given text at the given ``(x, y)`` position. Optionally with a maximum width to draw."""
        self._send_canvas_command('fillText', (text, x, y, max_width))

    def stroke_text(self, text, x, y, max_width=None):
        """Stroke a given text at the given ``(x, y)`` position. Optionally with a maximum width to draw."""
        self._send_canvas_command('strokeText', (text, x, y, max_width))

    # Line methods
    def get_line_dash(self):
        """Return the current line dash pattern array containing an even number of non-negative numbers."""
        return self._line_dash

    def set_line_dash(self, segments):
        """Set the current line dash pattern."""
        if len(segments) % 2:
            self._line_dash = segments + segments
        else:
            self._line_dash = segments
        self._send_canvas_command('setLineDash', (self._line_dash, ))

    # Image methods
    def draw_image(self, image, x=0, y=0, width=None, height=None):
        """Draw an ``image`` on the Canvas at the coordinates (``x``, ``y``) and scale it to (``width``, ``height``)."""
        if (not isinstance(image, (Canvas, Image))):
            raise TypeError('The image argument should be an Image widget or a Canvas widget')

        if width is not None and height is None:
            height = width

        serialized_image = widget_serialization['to_json'](image, None)

        self._send_canvas_command('drawImage', (serialized_image, x, y, width, height))

    def put_image_data(self, image_data, x=0, y=0):
        """Draw an image on the Canvas.

        ``image_data`` should be  a NumPy array containing the image to draw and ``x`` and ``y`` the pixel position where to
        draw. Unlike the CanvasRenderingContext2D.putImageData method, this method **is** affected by the canvas transformation
        matrix, and supports transparency.
        """
        image_metadata, image_buffer = binary_image(image_data)
        self._send_canvas_command('putImageData', (image_metadata, x, y), (image_buffer, ))

    def create_image_data(self, width, height):
        """Create a NumPy array of shape (width, height, 4) representing a table of pixel colors."""
        return np.zeros((width, height, 4), dtype=int)

    # Clipping
    def clip(self):
        """Turn the path currently being built into the current clipping path.

        You can use clip() instead of close_path() to close a path and turn it into a clipping
        path instead of stroking or filling the path.
        """
        self._send_canvas_command('clip')

    # Transformation methods
    def save(self):
        """Save the entire state of the canvas."""
        self._send_canvas_command('save')

    def restore(self):
        """Restore the most recently saved canvas state."""
        self._send_canvas_command('restore')

    def translate(self, x, y):
        """Move the canvas and its origin on the grid.

        ``x`` indicates the horizontal distance to move,
        and ``y`` indicates how far to move the grid vertically.
        """
        self._send_canvas_command('translate', (x, y))

    def rotate(self, angle):
        """Rotate the canvas clockwise around the current origin by the ``angle`` number of radians."""
        self._send_canvas_command('rotate', (angle, ))

    def scale(self, x, y=None):
        """Scale the canvas units by ``x`` horizontally and by ``y`` vertically. Both parameters are real numbers.

        If ``y`` is not provided, it is defaulted to the same value as ``x``.
        Values that are smaller than 1.0 reduce the unit size and values above 1.0 increase the unit size.
        Values of 1.0 leave the units the same size.
        """
        if y is None:
            y = x
        self._send_canvas_command('scale', (x, y))

    def transform(self, a, b, c, d, e, f):
        """Multiply the current transformation matrix with the matrix described by its arguments.

        The transformation matrix is described by:
        ``[[a, c, e], [b, d, f], [0, 0, 1]]``.
        """
        self._send_canvas_command('transform', (a, b, c, d, e, f))

    def set_transform(self, a, b, c, d, e, f):
        """Reset the current transform to the identity matrix, and then invokes the transform() method with the same arguments.

        This basically undoes the current transformation, then sets the specified transform, all in one step.
        """
        self._send_canvas_command('setTransform', (a, b, c, d, e, f))

    def reset_transform(self):
        """Reset the current transform to the identity matrix.

        This is the same as calling: set_transform(1, 0, 0, 1, 0, 0).
        """
        self._send_canvas_command('resetTransform')

    # Extras
    def clear(self):
        """Clear the entire canvas. This is the same as calling ``clear_rect(0, 0, canvas.width, canvas.height)``."""
        self._send_command({'name': 'clear'})

    def flush(self):
        """Flush all the cached commands and clear the cache."""
        if not self.caching:
            return

        self.send(self._commands_cache, self._buffers_cache)

        self.caching = False
        self._commands_cache = []
        self._buffers_cache = []

    # Events
    def on_client_ready(self, callback, remove=False):
        """Register a callback that will be called when a new client is ready to receive draw commands.

        When a new client connects to the kernel he will get an empty Canvas (because the canvas is
        almost stateless, the new client does not know what draw commands were previously sent). So
        this function is useful for replaying your drawing whenever a new client connects and is
        ready to receive draw commands.
        """
        self._client_ready_callbacks.register_callback(callback, remove=remove)

    def on_mouse_move(self, callback, remove=False):
        """Register a callback that will be called on mouse move."""
        self._mouse_move_callbacks.register_callback(callback, remove=remove)

    def on_mouse_down(self, callback, remove=False):
        """Register a callback that will be called on mouse click down."""
        self._mouse_down_callbacks.register_callback(callback, remove=remove)

    def on_mouse_up(self, callback, remove=False):
        """Register a callback that will be called on mouse click up."""
        self._mouse_up_callbacks.register_callback(callback, remove=remove)

    def on_mouse_out(self, callback, remove=False):
        """Register a callback that will be called on mouse out of the canvas."""
        self._mouse_out_callbacks.register_callback(callback, remove=remove)

    def on_touch_start(self, callback, remove=False):
        """Register a callback that will be called on touch start (new finger on the screen)."""
        self._touch_start_callbacks.register_callback(callback, remove=remove)

    def on_touch_end(self, callback, remove=False):
        """Register a callback that will be called on touch end (a finger is not touching the screen anymore)."""
        self._touch_end_callbacks.register_callback(callback, remove=remove)

    def on_touch_move(self, callback, remove=False):
        """Register a callback that will be called on touch move (finger moving on the screen)."""
        self._touch_move_callbacks.register_callback(callback, remove=remove)

    def on_touch_cancel(self, callback, remove=False):
        """Register a callback that will be called on touch cancel."""
        self._touch_cancel_callbacks.register_callback(callback, remove=remove)

    def __setattr__(self, name, value):
        super(Canvas, self).__setattr__(name, value)

        canvas_attrs = ['fill_style', 'stroke_style', 'global_alpha', 'font', 'text_align',
                        'text_baseline', 'direction', 'global_composite_operation',
                        'line_width', 'line_cap', 'line_join', 'miter_limit', 'line_dash_offset',
                        'shadow_offset_x', 'shadow_offset_y', 'shadow_blur', 'shadow_color']
        if name in canvas_attrs:
            command = {
                'name': 'set',
                'attr': to_camel_case(name),
                'value': value
            }
            self._send_command(command)

    def _send_canvas_command(self, name, args=[], buffers=[]):
        command = {
            'name': name,
            'n_buffers': len(buffers),
            'args': [arg for arg in args if arg is not None]
        }
        self._send_command(command, buffers)

    def _send_command(self, command, buffers=[]):
        if self.caching:
            self._commands_cache.append(command)
            self._buffers_cache += buffers
        else:
            self.send(command, buffers)

    def _handle_frontend_event(self, _, content, buffers):
        if content.get('event', '') == 'client_ready':
            self._client_ready_callbacks()

        if content.get('event', '') == 'mouse_move':
            self._mouse_move_callbacks(content['x'], content['y'])
        if content.get('event', '') == 'mouse_down':
            self._mouse_down_callbacks(content['x'], content['y'])
        if content.get('event', '') == 'mouse_up':
            self._mouse_up_callbacks(content['x'], content['y'])
        if content.get('event', '') == 'mouse_out':
            self._mouse_out_callbacks(content['x'], content['y'])

        if content.get('event', '') == 'touch_start':
            self._touch_start_callbacks([(touch['x'], touch['y']) for touch in content['touches']])
        if content.get('event', '') == 'touch_end':
            self._touch_end_callbacks([(touch['x'], touch['y']) for touch in content['touches']])
        if content.get('event', '') == 'touch_move':
            self._touch_move_callbacks([(touch['x'], touch['y']) for touch in content['touches']])
        if content.get('event', '') == 'touch_cancel':
            self._touch_cancel_callbacks([(touch['x'], touch['y']) for touch in content['touches']])


class MultiCanvas(_CanvasBase):
    """Create a MultiCanvas widget with n_canvases Canvas widgets.

    Args:
        n_canvases (int): The number of canvases to create
        width (int): The width (in pixels) of the canvases
        height (int): The height (in pixels) of the canvases
    """

    _model_name = Unicode('MultiCanvasModel').tag(sync=True)
    _view_name = Unicode('MultiCanvasView').tag(sync=True)

    _canvases = List(Instance(Canvas)).tag(sync=True, **widget_serialization)

    def __init__(self, n_canvases=3, *args, **kwargs):
        """Constructor."""
        super(MultiCanvas, self).__init__(*args, _canvases=[Canvas() for _ in range(n_canvases)], **kwargs)

    def __getitem__(self, key):
        """Access one of the Canvas instances."""
        return self._canvases[key]

    def __setattr__(self, name, value):
        super(MultiCanvas, self).__setattr__(name, value)

        if name in ('caching', 'width', 'height'):
            for layer in self._canvases:
                setattr(layer, name, value)

    def on_client_ready(self, callback, remove=False):
        """Register a callback that will be called when a new client is ready to receive draw commands.

        When a new client connects to the kernel he will get an empty Canvas (because the canvas is
        almost stateless, the new client does not know what draw commands were previously sent). So
        this function is useful for replaying your drawing whenever a new client connects and is
        ready to receive draw commands.
        """
        self._canvases[-1]._client_ready_callbacks.register_callback(callback, remove=remove)

    def clear(self):
        """Clear the Canvas."""
        for layer in self._canvases:
            layer.clear()

    def flush(self):
        """Flush all the cached commands and clear the cache."""
        for layer in self._canvases:
            layer.flush()


@contextmanager
def hold_canvas(canvas):
    """Hold any drawing on the canvas, and perform all commands in a single shot at the end.

    This is way more efficient than sending commands one by one.

    Args:
        canvas (ipycanvas.canvas.Canvas): The canvas widget on which to hold the commands
    """
    canvas.caching = True
    yield
    canvas.flush()
