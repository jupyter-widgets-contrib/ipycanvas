#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

import warnings
from contextlib import contextmanager

import numpy as np

from traitlets import (
    Bool,
    Bytes,
    CInt,
    Enum,
    Float,
    Instance,
    List,
    Unicode,
    TraitError,
    Union,
)

from ipywidgets import (
    CallbackDispatcher,
    Color,
    DOMWidget,
    Image,
    Widget,
    widget_serialization,
)
from ipywidgets.widgets.trait_types import (
    bytes_serialization,
    _color_names,
    _color_hex_re,
    _color_hexa_re,
    _color_rgbhsl_re,
)

from ._frontend import module_name, module_version

from .utils import binary_image, populate_args, image_bytes_to_array, commands_to_buffer

_CMD_LIST = [
    "fillRect",
    "strokeRect",
    "fillRects",
    "strokeRects",
    "clearRect",
    "fillArc",
    "fillCircle",
    "strokeArc",
    "strokeCircle",
    "fillArcs",
    "strokeArcs",
    "fillCircles",
    "strokeCircles",
    "strokeLine",
    "beginPath",
    "closePath",
    "stroke",
    "fillPath",
    "fill",
    "moveTo",
    "lineTo",
    "rect",
    "arc",
    "ellipse",
    "arcTo",
    "quadraticCurveTo",
    "bezierCurveTo",
    "fillText",
    "strokeText",
    "setLineDash",
    "drawImage",
    "putImageData",
    "clip",
    "save",
    "restore",
    "translate",
    "rotate",
    "scale",
    "transform",
    "setTransform",
    "resetTransform",
    "set",
    "clear",
    "sleep",
    "fillPolygon",
    "strokePolygon",
    "strokeLines",
    "fillPolygons",
    "strokePolygons",
    "strokeLineSegments",
    "fillStyledRects",
    "strokeStyledRects",
    "fillStyledCircles",
    "strokeStyledCircles",
    "fillStyledArcs",
    "strokeStyledArcs",
    "fillStyledPolygons",
    "strokeStyledPolygons",
    "strokeStyledLineSegments",
    "switchCanvas",
]
COMMANDS = {v: i for i, v in enumerate(_CMD_LIST)}


# Traitlets does not allow validating without creating a trait class, so we need this
def _validate_color(value):
    if isinstance(value, str):
        if (
            value.lower() in _color_names
            or _color_hex_re.match(value)
            or _color_hexa_re.match(value)
            or _color_rgbhsl_re.match(value)
        ):
            return value
    raise TraitError("{} is not a valid HTML Color".format(value))


def _validate_number(value, min_val, max_val):
    try:
        number = float(value)

        if number >= min_val and number <= max_val:
            return number
    except ValueError:
        raise TraitError("{} is not a number".format(value))
    raise TraitError("{} is not in the range [{}, {}]".format(value, min_val, max_val))


def _serialize_list_of_polygons_or_linestrokes(
    points, points_per_item, item_name, min_elements
):
    if isinstance(points, list):
        if points_per_item is not None:
            raise RuntimeError("when points are a list, points_per_item must be None")
        points_per_item = []
        np_polygons = []
        for i, polygon_points in enumerate(points):
            polygon_points = np.require(polygon_points, requirements=["C"])
            if polygon_points.shape[1] != 2:
                raise RuntimeError(
                    f"item {i} in points have wrong shape: `{polygon_points.shape}` but must be of type (n,2)"
                )
            points_per_item.append(polygon_points.shape[0])
            np_polygons.append(polygon_points.ravel())

        num_polygons = len(points)
        flat_points = np.concatenate(np_polygons)
        points_per_item = np.array(points_per_item)

    elif isinstance(points, np.ndarray):
        points = np.require(points, requirements=["C"])
        shape = points.shape
        ndim = points.ndim

        if ndim <= 2:
            if points_per_item is None:
                raise RuntimeError(
                    "when points are given as a 1d / 2d array, points_per_item must not be None"
                )
            if ndim == 1:
                flat_points = points
            elif ndim == 2:
                if shape[1] != 2:
                    raise RuntimeError(
                        f"points have wrong shape: `{shape}`. When points are given as a 2D array the shape must be of (n,2)"
                    )
                flat_points = points.ravel()
            num_polygons = len(points_per_item)
        elif ndim == 3:
            if points_per_item is not None:
                raise RuntimeError(
                    "when points are a list, points_per_item must be None"
                )
            if shape[2] != 2:
                raise RuntimeError(
                    f"Points have wrong shape: `{shape}`: When points are given as a 3D array the shape must be of (n_{item_name}, n_points_per_{item_name}, 2)"
                )
            if shape[1] < min_elements:
                raise RuntimeError(
                    f"Points have wrong shape: `{shape}`: when points are given as a 3D array the shape must be of (n_{item_name}, n_points_per_{item_name}, 2) and n_points_per_{item_name} must be >= {min_elements} "
                )
            flat_points = points.ravel()
            num_polygons = shape[0]
            points_per_item = shape[1]
        else:
            raise RuntimeError("ndarray must have ndim <= 3")
    else:
        raise RuntimeError("points must be a list or an ndarray")
    return num_polygons, flat_points, points_per_item


class _CanvasManager(Widget):
    """Private Canvas manager."""

    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _model_name = Unicode("CanvasManagerModel").tag(sync=True)

    def __init__(self, *args, **kwargs):
        self._caching = kwargs.get("caching", False)
        self._commands_cache = []
        self._buffers_cache = []
        self._current_canvas = None

        super(_CanvasManager, self).__init__()

    def send_draw_command(self, canvas, name, args=[], buffers=[]):
        while len(args) and args[len(args) - 1] is None:
            args.pop()
        self.send_command(canvas, [name, args, len(buffers)], buffers)

    def send_command(self, canvas, command, buffers=[]):
        if self._caching:
            if self._current_canvas is not canvas:
                self._commands_cache.append(
                    [
                        COMMANDS["switchCanvas"],
                        [widget_serialization["to_json"](canvas, None)],
                    ]
                )
                self._current_canvas = canvas
            self._commands_cache.append(command)
            self._buffers_cache += buffers

            return

        # TODO Send the switch and the message in one batch?
        if self._current_canvas is not canvas:
            self._send_custom(
                [
                    COMMANDS["switchCanvas"],
                    [widget_serialization["to_json"](canvas, None)],
                ]
            )
            self._current_canvas = canvas

        self._send_custom(command, buffers)

    def flush(self):
        """Flush all the cached commands and clear the cache."""
        if not self._caching or not len(self._commands_cache):
            return

        self._send_custom(self._commands_cache, self._buffers_cache)

        self._commands_cache = []
        self._buffers_cache = []

    def _send_custom(self, command, buffers=[]):
        metadata, command_buffer = commands_to_buffer(command)
        self.send(metadata, buffers=[command_buffer] + buffers)


# Main canvas manager
_CANVAS_MANAGER = _CanvasManager()


class Path2D(Widget):
    """Create a Path2D.

    Args:
        value (str): The path value, e.g. "M10 10 h 80 v 80 h -80 Z"
    """

    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _model_name = Unicode("Path2DModel").tag(sync=True)

    value = Unicode(allow_none=False, read_only=True).tag(sync=True)

    def __init__(self, value):
        """Create a Path2D object given the path string."""
        self.set_trait("value", value)

        super(Path2D, self).__init__()


class Pattern(Widget):
    """Create a Pattern.

    Args:
        image (Canvas or MultiCanvas or ipywidgets.Image): The source to be used as the pattern's image
        repetition (str): A string indicating how to repeat the pattern's image, can be "repeat" (both directions), "repeat-x" (horizontal only), "repeat-y" (vertical only), "no-repeat" (neither direction)
    """

    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _model_name = Unicode("PatternModel").tag(sync=True)

    image = Union(
        (
            Instance(Image),
            Instance("ipycanvas.Canvas"),
            Instance("ipycanvas.MultiCanvas"),
        ),
        allow_none=False,
        read_only=True,
    ).tag(sync=True, **widget_serialization)
    repetition = Enum(
        ["repeat", "repeat-x", "repeat-y", "no-repeat"],
        allow_none=False,
        read_only=True,
    ).tag(sync=True)

    def __init__(self, image, repetition="repeat"):
        """Create a Pattern object given the image and the type of repetition."""
        self.set_trait("image", image)
        self.set_trait("repetition", repetition)

        super(Pattern, self).__init__()

    def _ipython_display_(self, *args, **kwargs):
        return self.image._ipython_display_(*args, **kwargs)


class _CanvasGradient(Widget):
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    x0 = Float(allow_none=False, read_only=True).tag(sync=True)
    y0 = Float(allow_none=False, read_only=True).tag(sync=True)
    x1 = Float(allow_none=False, read_only=True).tag(sync=True)
    y1 = Float(allow_none=False, read_only=True).tag(sync=True)

    color_stops = List(allow_none=False, read_only=True).tag(sync=True)

    def __init__(self, x0, y0, x1, y1, color_stops):
        self.set_trait("x0", x0)
        self.set_trait("y0", y0)
        self.set_trait("x1", x1)
        self.set_trait("y1", y1)

        for color_stop in color_stops:
            _validate_number(color_stop[0], 0, 1)
            _validate_color(color_stop[1])
        self.set_trait("color_stops", color_stops)

        super(_CanvasGradient, self).__init__()


class LinearGradient(_CanvasGradient):
    """Create a LinearGradient."""

    _model_name = Unicode("LinearGradientModel").tag(sync=True)

    def __init__(self, x0, y0, x1, y1, color_stops):
        """Create a LinearGradient object given the start point, end point and color stops.

        Args:
            x0 (float): The x-axis coordinate of the start point.
            y0 (float): The y-axis coordinate of the start point.
            x1 (float): The x-axis coordinate of the end point.
            y1 (float): The y-axis coordinate of the end point.
            color_stops (list): The list of color stop tuples (offset, color) defining the gradient.
        """
        super(LinearGradient, self).__init__(x0, y0, x1, y1, color_stops)


class RadialGradient(_CanvasGradient):
    """Create a RadialGradient."""

    _model_name = Unicode("RadialGradientModel").tag(sync=True)

    r0 = Float(allow_none=False, read_only=True).tag(sync=True)
    r1 = Float(allow_none=False, read_only=True).tag(sync=True)

    def __init__(self, x0, y0, r0, x1, y1, r1, color_stops):
        """Create a RadialGradient object given the start circle, end circle and color stops.

        Args:
            x0 (float): The x-axis coordinate of the start circle.
            y0 (float): The y-axis coordinate of the start circle.
            r0 (float): The radius of the start circle.
            x1 (float): The x-axis coordinate of the end circle.
            y1 (float): The y-axis coordinate of the end circle.
            r1 (float): The radius of the end circle.
            color_stops (list): The list of color stop tuples (offset, color) defining the gradient.
        """
        _validate_number(r0, 0, float("inf"))
        _validate_number(r1, 0, float("inf"))

        self.set_trait("r0", r0)
        self.set_trait("r1", r1)

        super(RadialGradient, self).__init__(x0, y0, x1, y1, color_stops)


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
    image_data = Bytes(default_value=None, allow_none=True, read_only=True).tag(
        sync=True, **bytes_serialization
    )

    def to_file(self, filename):
        """Save the current Canvas image to a PNG file.

        This will raise an exception if there is no image to save (_e.g._ if ``image_data`` is ``None``).
        """
        if self.image_data is None:
            raise RuntimeError(
                "No image data to save, please be sure that ``sync_image_data`` is set to True"
            )
        if not filename.endswith(".png") and not filename.endswith(".PNG"):
            raise RuntimeError("Can only save to a PNG file")

        with open(filename, "wb") as fobj:
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
            raise RuntimeError(
                "No image data, please be sure that ``sync_image_data`` is set to True"
            )

        x = int(x)
        y = int(y)

        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y

        width = int(width)
        height = int(height)

        image_data = image_bytes_to_array(self.image_data)
        return image_data[y : y + height, x : x + width]


class Canvas(_CanvasBase):
    """Create a Canvas widget.

    Args:
        width (int): The width (in pixels) of the canvas
        height (int): The height (in pixels) of the canvas
    """

    _model_name = Unicode("CanvasModel").tag(sync=True)
    _view_name = Unicode("CanvasView").tag(sync=True)

    _send_client_ready_event = Bool(True).tag(sync=True)

    #: (valid HTML color or Gradient or Pattern) The color for filling rectangles and paths. Default to ``'black'``.
    fill_style = Union(
        (Color(), Instance(_CanvasGradient), Instance(Pattern)), default_value="black"
    )

    #: (valid HTML color or Gradient or Pattern) The color for rectangles and paths stroke. Default to ``'black'``.
    stroke_style = Union(
        (Color(), Instance(_CanvasGradient), Instance(Pattern)), default_value="black"
    )

    #: (float) Transparency level. Default to ``1.0``.
    global_alpha = Float(1.0)

    #: (str) Font for the text rendering. Default to ``'12px serif'``.
    font = Unicode("12px serif")

    #: (str) Text alignment, possible values are ``'start'``, ``'end'``, ``'left'``, ``'right'``, and ``'center'``.
    #: Default to ``'start'``.
    text_align = Enum(
        ["start", "end", "left", "right", "center"], default_value="start"
    )

    #: (str) Text baseline, possible values are ``'top'``, ``'hanging'``, ``'middle'``, ``'alphabetic'``, ``'ideographic'``
    #: and ``'bottom'``.
    #: Default to ``'alphabetic'``.
    text_baseline = Enum(
        ["top", "hanging", "middle", "alphabetic", "ideographic", "bottom"],
        default_value="alphabetic",
    )

    #: (str) Text direction, possible values are ``'ltr'``, ``'rtl'``, and ``'inherit'``.
    #: Default to ``'inherit'``.
    direction = Enum(["ltr", "rtl", "inherit"], default_value="inherit")

    #: (str) Global composite operation, possible values are listed below:
    #: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Compositing#globalCompositeOperation
    global_composite_operation = Enum(
        [
            "source-over",
            "source-in",
            "source-out",
            "source-atop",
            "destination-over",
            "destination-in",
            "destination-out",
            "destination-atop",
            "lighter",
            "copy",
            "xor",
            "multiply",
            "screen",
            "overlay",
            "darken",
            "lighten",
            "color-dodge",
            "color-burn",
            "hard-light",
            "soft-light",
            "difference",
            "exclusion",
            "hue",
            "saturation",
            "color",
            "luminosity",
        ],
        default_value="source-over",
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
    shadow_color = Color("rgba(0, 0, 0, 0)")

    #: (float) Sets the width of lines drawn in the future, must be a positive number. Default to ``1.0``.
    line_width = Float(1.0)

    #: (str) Sets the appearance of the ends of lines, possible values are ``'butt'``, ``'round'`` and ``'square'``.
    #: Default to ``'butt'``.
    line_cap = Enum(["butt", "round", "square"], default_value="butt")

    #: (str) Sets the appearance of the "corners" where lines meet, possible values are ``'round'``, ``'bevel'`` and ``'miter'``.
    #: Default to ``'miter'``
    line_join = Enum(["round", "bevel", "miter"], default_value="miter")

    #: (float) Establishes a limit on the miter when two lines join at a sharp angle, to let you control how thick
    #: the junction becomes. Default to ``10.``.
    miter_limit = Float(10.0)

    #: (str) Filter effects such as blurring and grayscaling. It is similar to the CSS filter property and accepts the same values.
    #: This property has no effect on Safari, see https://bugs.webkit.org/show_bug.cgi?id=198416
    filter = Unicode("none")

    _line_dash = List()

    #: (float) Specifies where to start a dash array on a line. Default is ``0.``.
    line_dash_offset = Float(0.0)

    _client_ready_callbacks = Instance(CallbackDispatcher, ())

    _mouse_move_callbacks = Instance(CallbackDispatcher, ())
    _mouse_down_callbacks = Instance(CallbackDispatcher, ())
    _mouse_up_callbacks = Instance(CallbackDispatcher, ())
    _mouse_out_callbacks = Instance(CallbackDispatcher, ())

    _touch_start_callbacks = Instance(CallbackDispatcher, ())
    _touch_end_callbacks = Instance(CallbackDispatcher, ())
    _touch_move_callbacks = Instance(CallbackDispatcher, ())
    _touch_cancel_callbacks = Instance(CallbackDispatcher, ())

    _key_down_callbacks = Instance(CallbackDispatcher, ())

    ATTRS = {
        "fill_style": 0,
        "stroke_style": 1,
        "global_alpha": 2,
        "font": 3,
        "text_align": 4,
        "text_baseline": 5,
        "direction": 6,
        "global_composite_operation": 7,
        "line_width": 8,
        "line_cap": 9,
        "line_join": 10,
        "miter_limit": 11,
        "line_dash_offset": 12,
        "shadow_offset_x": 13,
        "shadow_offset_y": 14,
        "shadow_blur": 15,
        "shadow_color": 16,
        "filter": 17,
    }

    def __init__(self, *args, **kwargs):
        """Create a Canvas widget."""
        super(Canvas, self).__init__(*args, **kwargs)

        if "caching" in kwargs:
            _CANVAS_MANAGER._caching = kwargs["caching"]

            warnings.warn(
                "caching is deprecated and will be removed in a future release, please use hold_canvas() instead.",
                DeprecationWarning,
            )

        self.on_msg(self._handle_frontend_event)

    def sleep(self, time):
        """Make the Canvas sleep for `time` milliseconds."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["sleep"], [time])

    # Gradient methods
    def create_linear_gradient(self, x0, y0, x1, y1, color_stops):
        """Create a LinearGradient object given the start point, end point, and color stops.

        Args:
            x0 (float): The x-axis coordinate of the start point.
            y0 (float): The y-axis coordinate of the start point.
            x1 (float): The x-axis coordinate of the end point.
            y1 (float): The y-axis coordinate of the end point.
            color_stops (list): The list of color stop tuples (offset, color) defining the gradient.
        """
        return LinearGradient(x0, y0, x1, y1, color_stops)

    def create_radial_gradient(self, x0, y0, r0, x1, y1, r1, color_stops):
        """Create a RadialGradient object given the start circle, end circle and color stops.

        Args:
            x0 (float): The x-axis coordinate of the start circle.
            y0 (float): The y-axis coordinate of the start circle.
            r0 (float): The radius of the start circle.
            x1 (float): The x-axis coordinate of the end circle.
            y1 (float): The y-axis coordinate of the end circle.
            r1 (float): The radius of the end circle.
            color_stops (list): The list of color stop tuples (offset, color) defining the gradient.
        """
        return RadialGradient(x0, y0, r0, x1, y1, r1, color_stops)

    # Pattern method
    def create_pattern(self, image, repetition="repeat"):
        """Create a Pattern.

        Args:
            image (Canvas or MultiCanvas or ipywidgets.Image): The source to be used as the pattern's image
            repetition (str): A string indicating how to repeat the pattern's image, can be "repeat" (both directions), "repeat-x" (horizontal only), "repeat-y" (vertical only), "no-repeat" (neither direction)
        """
        return Pattern(image, repetition)

    # Rectangles methods
    def fill_rect(self, x, y, width, height=None):
        """Draw a filled rectangle of size ``(width, height)`` at the ``(x, y)`` position."""
        if height is None:
            height = width

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["fillRect"], [x, y, width, height]
        )

    def stroke_rect(self, x, y, width, height=None):
        """Draw a rectangular outline of size ``(width, height)`` at the ``(x, y)`` position."""
        if height is None:
            height = width

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeRect"], [x, y, width, height]
        )

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

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["fillRects"], args, buffers)

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

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["strokeRects"], args, buffers)

    def fill_styled_rects(self, x, y, width, height, color, alpha=1):
        """Draw filled and styled rectangles of sizes ``(width, height)`` at the ``(x, y)`` positions

        Where ``x``, ``y``, ``width`` and ``height`` arguments are NumPy arrays, lists or scalar values.
        If ``height`` is None, it is set to the same value as width.
        ``color`` is an (n_rect x 3) NumPy array with the colors and ``alpha`` is an (n_rect) NumPy array
        with the alpha channel values.
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

        populate_args(color, args, buffers)
        populate_args(alpha, args, buffers)
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["fillStyledRects"], args, buffers
        )

    def stroke_styled_rects(self, x, y, width, height, color, alpha=1):
        """Draw rectangular styled outlines of sizes ``(width, height)`` at the ``(x, y)`` positions.of sizes ``(width, height)``

        Where ``x``, ``y``, ``width`` and ``height`` arguments are NumPy arrays, lists or scalar values.
        If ``height`` is None, it is set to the same value as width.
        ``color`` is an (n_rect x 3) NumPy array with the colors and ``alpha`` is an (n_rect) NumPy array
        with the alpha channel values.
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

        populate_args(color, args, buffers)
        populate_args(alpha, args, buffers)
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeStyledRects"], args, buffers
        )

    def clear_rect(self, x, y, width, height=None):
        """Clear the specified rectangular area of size ``(width, height)`` at the ``(x, y)`` position, making it fully transparent."""
        if height is None:
            height = width

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["clearRect"], [x, y, width, height]
        )

    # Arc methods
    def fill_arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Draw a filled arc centered at ``(x, y)`` with a radius of ``radius`` from ``start_angle`` to ``end_angle``."""
        _CANVAS_MANAGER.send_draw_command(
            self,
            COMMANDS["fillArc"],
            [x, y, radius, start_angle, end_angle, anticlockwise],
        )

    def fill_circle(self, x, y, radius):
        """Draw a filled circle centered at ``(x, y)`` with a radius of ``radius``."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["fillCircle"], [x, y, radius])

    def stroke_arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Draw an arc outline centered at ``(x, y)`` with a radius of ``radius``."""
        _CANVAS_MANAGER.send_draw_command(
            self,
            COMMANDS["strokeArc"],
            [x, y, radius, start_angle, end_angle, anticlockwise],
        )

    def stroke_circle(self, x, y, radius):
        """Draw a circle centered at ``(x, y)`` with a radius of ``radius``."""
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeCircle"], [x, y, radius]
        )

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

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["fillArcs"], args, buffers)

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

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["strokeArcs"], args, buffers)

    def fill_circles(self, x, y, radius):
        """Draw filled circles centered at ``(x, y)`` with a radius of ``radius``.

        Where ``x``, ``y``, ``radius`` and other arguments are NumPy arrays, lists or scalar values.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(radius, args, buffers)

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["fillCircles"], args, buffers)

    def stroke_circles(self, x, y, radius):
        """Draw a circle outlines centered at ``(x, y)`` with a radius of ``radius``.

        Where ``x``, ``y``, ``radius`` and other arguments are NumPy arrays, lists or scalar values.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(radius, args, buffers)

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeCircles"], args, buffers
        )

    def fill_styled_circles(self, x, y, radius, color, alpha=1):
        """Draw a filled circles centered at ``(x, y)`` with a radius of ``radius``.

        Where ``x``, ``y``, ``radius``  and ``alpha`  are NumPy arrays, lists or scalar values.
        ``color`` must be an (nx3) NumPy arrays with the color for each circle.
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(radius, args, buffers)
        populate_args(color, args, buffers)
        populate_args(alpha, args, buffers)
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["fillStyledCircles"], args, buffers
        )

    def stroke_styled_circles(self, x, y, radius, color, alpha=1):
        """Draw filled circles centered at ``(x, y)`` with a radius of ``radius``.

        Where ``x``, ``y``, ``radius``  and ``alpha``  are NumPy arrays, lists or scalar values.
        ``color`` must be an nx3 NumPy arrays with the color for each circle
        """
        args = []
        buffers = []

        populate_args(x, args, buffers)
        populate_args(y, args, buffers)
        populate_args(radius, args, buffers)
        populate_args(color, args, buffers)
        populate_args(alpha, args, buffers)

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeStyledCircles"], args, buffers
        )

    def fill_styled_arcs(
        self, x, y, radius, start_angle, end_angle, color, alpha=1, anticlockwise=False
    ):
        """Draw filled and styled arcs centered at ``(x, y)`` with a radius of ``radius``.

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
        populate_args(color, args, buffers)
        populate_args(alpha, args, buffers)

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["fillStyledArcs"], args, buffers
        )

    def stroke_styled_arcs(
        self, x, y, radius, start_angle, end_angle, color, alpha=1, anticlockwise=False
    ):
        """Draw an styled arc outlines centered at ``(x, y)`` with a radius of ``radius``.

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
        populate_args(color, args, buffers)
        populate_args(alpha, args, buffers)

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeStyledArcs"], args, buffers
        )

    # Polygon methods
    def fill_polygon(self, points):
        """Fill a polygon from a list of points ``[(x1, y1), (x2, y2), ..., (xn, yn)]``."""
        args = []
        buffers = []

        populate_args(points, args, buffers)

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["fillPolygon"], args, buffers)

    def stroke_polygon(self, points):
        """Draw polygon outline from a list of points ``[(x1, y1), (x2, y2), ..., (xn, yn)]``."""
        args = []
        buffers = []

        populate_args(points, args, buffers)

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokePolygon"], args, buffers
        )

    def fill_polygons(self, points, points_per_polygon=None):
        """ " Draw many filled polygons at once:

        Args:
            points (list or ndarray): The polygons points:

                The points can be specified as list or as ndarray:
                If the points are a list it must a an be a list of ndarrays,
                where each ndarray is a nx2 array of coordinates
                (n can be different for each entry)
                If the points are given as ndarray it must be either:

                - a 3d array: the shape of the array is (n_polyons, n_points_per_polygon, 2)
                - a 2d array: the shape of the array is (n,  2) and in additional  `points_per_polygon`
                  must be specified st. we know the the number of points for each individual polygon.
                  Note that the number of points in ``points`` must match the points_per_polygon.
                  array: ie: `np.sum(points_per_polygon) == points.shape[0]`

            points_per_polygon (ndarray):
                ndarray with number of points for each polygon. Must **only** be given if points are
                given as `flat` 2D array.

        """
        self._draw_polygons_or_linesegments(
            "fillPolygons", points, None, None, points_per_polygon, False, 3, "polygon"
        )

    def stroke_polygons(self, points, points_per_polygon=None):
        """ " Draw many stroked polygons at once:

        Args:
            points (list or ndarray): The polygons points:

                The points can be specified as list or as ndarray:
                If the points are a list it must a an be a list of ndarrays,
                where each ndarray is a nx2 array of coordinates
                (n can be different for each entry)
                If the points are given as ndarray it must be either:

                - a 3d array: the shape of the array is (n_polyons, n_points_per_polygon, 2)
                - a 2d array: the shape of the array is (n,  2) and in additional  `points_per_polygon`
                  must be specified st. we know the the number of points for each individual polygon.
                  Note that the number of points in ``points`` must match the points_per_polygon.
                  array: ie: `np.sum(points_per_polygon) == points.shape[0]`

            points_per_polygon (ndarray):
                ndarray with number of points for each polygon. Must **only** be given if points are
                given as `flat` 2D array.
        """
        self._draw_polygons_or_linesegments(
            "strokePolygons",
            points,
            None,
            None,
            points_per_polygon,
            False,
            3,
            "polygon",
        )

    def fill_styled_polygons(self, points, color, alpha=1, points_per_polygon=None):
        """ " Draw many filled polygons at once:

        Args:
            points (list or ndarray): The polygons points:

                The points can be specified as list or as ndarray:
                If the points are a list it must a an be a list of ndarrays,
                where each ndarray is a nx2 array of coordinates
                (n can be different for each entry)
                If the points are given as ndarray it must be either:

                - a 3d array: the shape of the array is (n_polyons, n_points_per_polygon, 2)
                - a 2d array: the shape of the array is (n,  2) and in additional  `points_per_polygon`
                  must be specified st. we know the the number of points for each individual polygon.
                  Note that the number of points in ``points`` must match the points_per_polygon.
                  array: ie: `np.sum(points_per_polygon) == points.shape[0]`

            color (ndarray)
                An (n_polyons,3) array with the color for each polygon
            alpha (ndarray,list,scalar):
                An  array with the alpha value for each polygon. Can be a scalar and the
                same value is used for all polygons
            points_per_polygon (ndarray):
                ndarray with number of points for each polygon. Must **only** be given if points are
                given as `flat` 2D array.

        """
        self._draw_polygons_or_linesegments(
            "fillStyledPolygons",
            points,
            color,
            alpha,
            points_per_polygon,
            True,
            3,
            "polygon",
        )

    def stroke_styled_polygons(self, points, color, alpha=1, points_per_polygon=None):
        """ " Draw many stroked polygons at once:

        Args:
            points (list or ndarray): The polygons points:

                The points can be specified as list or as ndarray:
                If the points are a list it must a an be a list of ndarrays,
                where each ndarray is a nx2 array of coordinates
                (n can be different for each entry)
                If the points are given as ndarray it must be either:

                - a 3d array: the shape of the array is (n_polyons, n_points_per_polygon, 2)
                - a 2d array: the shape of the array is (n,  2) and in additional  `points_per_polygon`
                  must be specified st. we know the the number of points for each individual polygon.
                  Note that the number of points in ``points`` must match the points_per_polygon.
                  array: ie: `np.sum(points_per_polygon) == points.shape[0]`

            color (ndarray)
                An (n_polyons,3) array with the color for each polygon
            alpha (ndarray,list,scalar):
                An  array with the alpha value for each polygon. Can be a scalar and the
                same value is used for all polygons
            points_per_polygon (ndarray):
                ndarray with number of points for each polygon. Must **only** be given if points are
                given as `flat` 2D array.

        """
        self._draw_polygons_or_linesegments(
            "strokeStyledPolygons",
            points,
            color,
            alpha,
            points_per_polygon,
            True,
            3,
            "polygon",
        )

    # Lines methods
    def stroke_line(self, x1, y1, x2, y2):
        """Draw a line from ``(x1, y1)`` to ``(x2, y2)``."""
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeLine"], [x1, y1, x2, y2]
        )

    def stroke_lines(self, points):
        """Draw a path of consecutive lines from a list of points ``[(x1, y1), (x2, y2), ..., (xn, yn)]``."""
        args = []
        buffers = []

        populate_args(points, args, buffers)

        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["strokeLines"], args, buffers)

    def stroke_styled_line_segments(
        self, points, color, alpha=1, points_per_line_segment=None
    ):
        """Draw many line segments at once:

        Args:
            points (list or ndarray): The line_segments points:

                The points can be specified as list or as ndarray:
                If the points are a list it must a an be a list of ndarrays,
                where each ndarray is a nx2 array of coordinates
                (n can be different for each entry)
                If the points are given as ndarray it must be either:

                - a 3d array: the shape of the array is (n_line_segments, n_points_per_polygon, 2)
                - a 2d array: the shape of the array is (n,  2) and in additional  `points_per_line_segment`
                    must be specified st. we know the the number of points for each individual line_segment.
                    Note that the number of points in ``points`` must match the points_per_line_segment.
                    array: ie: `np.sum(points_per_line_segment) == points.shape[0]`

            color (ndarray)
                An (n_line_segments,3) array with the color for each line_segment
            alpha (ndarray,list,scalar):
                An  array with the alpha value for each line_segment. Can be a scalar and the
                same value is used for all line_segments
            points_per_line_segment (ndarray):
                ndarray with number of points for each line_segment. Must **only** be given if points are
                given as `flat` 2D array.

        """
        self._draw_polygons_or_linesegments(
            "strokeStyledLineSegments",
            points,
            color,
            alpha,
            points_per_line_segment,
            True,
            2,
            "line_segment",
        )

    def stroke_line_segments(self, points, points_per_line_segment=None):
        """ Draw many stroked line_segments at once:

            Args:
                points (list or ndarray): The line_segments points:

                    The points can be specified as list or as ndarray:
                    If the points are a list it must a an be a list of ndarrays,
                    where each ndarray is a nx2 array of coordinates
                    (n can be different for each entry)
                    If the points are given as ndarray it must be either:

                    - a 3d array: the shape of the array is (n_line_segments, n_points_per_polygon, 2)
                    - a 2d array: the shape of the array is (n,  2) and in additional  `points_per_line_segment `
                      must be specified st. we know the the number of points for each individual polygon.
                      Note that the number of points in ``points`` must match the points_per_line_segment .
                      array: ie: `np.sum(points_per_line_segment  ) == points.shape[0]`\

                points_per_line_segment  (ndarray):
                    ndarray with number of points for each polygon. Must **only** be given if points are
                    given as `flat` 2D array.
        """
        self._draw_polygons_or_linesegments(
            "strokeLineSegments",
            points,
            None,
            None,
            points_per_line_segment,
            False,
            2,
            "line_segment",
        )

    # Paths methods
    def begin_path(self):
        """Call this method when you want to create a new path."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["beginPath"])

    def close_path(self):
        """Add a straight line from the current point to the start of the current path.

        If the shape has already been closed or has only one point, this function does nothing.
        This method doesn't draw anything to the canvas directly. You can render the path using the stroke() or fill() methods.
        """
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["closePath"])

    def stroke(self):
        """Stroke (outlines) the current path with the current ``stroke_style``."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["stroke"])

    def fill(self, rule_or_path="nonzero"):
        """Fill the current path with the current ``fill_style`` and given the rule, or fill the given Path2D.

        Possible rules are ``nonzero`` and ``evenodd``.
        """
        if isinstance(rule_or_path, Path2D):
            _CANVAS_MANAGER.send_draw_command(
                self,
                COMMANDS["fillPath"],
                [widget_serialization["to_json"](rule_or_path, None)],
            )
        else:
            _CANVAS_MANAGER.send_draw_command(self, COMMANDS["fill"], [rule_or_path])

    def move_to(self, x, y):
        """Move the "pen" to the given ``(x, y)`` coordinates."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["moveTo"], [x, y])

    def line_to(self, x, y):
        """Add a straight line to the current path by connecting the path's last point to the specified ``(x, y)`` coordinates.

        Like other methods that modify the current path, this method does not directly render anything. To
        draw the path onto the canvas, you can use the fill() or stroke() methods.
        """
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["lineTo"], [x, y])

    def rect(self, x, y, width, height):
        """Add a rectangle of size ``(width, height)`` at the ``(x, y)`` position in the current path."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["rect"], [x, y, width, height])

    def arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        """Add a circular arc centered at ``(x, y)`` with a radius of ``radius`` to the current path.

        The path starts at ``start_angle`` and ends at ``end_angle``, and travels in the direction given by
        ``anticlockwise`` (defaulting to clockwise: ``False``).
        """
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["arc"], [x, y, radius, start_angle, end_angle, anticlockwise]
        )

    def ellipse(
        self,
        x,
        y,
        radius_x,
        radius_y,
        rotation,
        start_angle,
        end_angle,
        anticlockwise=False,
    ):
        """Add an ellipse centered at ``(x, y)`` with the radii ``radius_x`` and ``radius_y`` to the current path.

        The path starts at ``start_angle`` and ends at ``end_angle``, and travels in the direction given by
        ``anticlockwise`` (defaulting to clockwise: ``False``).
        """
        _CANVAS_MANAGER.send_draw_command(
            self,
            COMMANDS["ellipse"],
            [x, y, radius_x, radius_y, rotation, start_angle, end_angle, anticlockwise],
        )

    def arc_to(self, x1, y1, x2, y2, radius):
        """Add a circular arc to the current path.

        Using the given control points ``(x1, y1)`` and ``(x2, y2)`` and the ``radius``.
        """
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["arcTo"], [x1, y1, x2, y2, radius]
        )

    def quadratic_curve_to(self, cp1x, cp1y, x, y):
        """Add a quadratic Bezier curve to the current path.

        It requires two points: the first one is a control point and the second one is the end point.
        The starting point is the latest point in the current path, which can be changed using move_to()
        before creating the quadratic Bezier curve.
        """
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["quadraticCurveTo"], [cp1x, cp1y, x, y]
        )

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        """Add a cubic Bezier curve to the current path.

        It requires three points: the first two are control points and the third one is the end point.
        The starting point is the latest point in the current path, which can be changed using move_to()
        before creating the Bezier curve.
        """
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["bezierCurveTo"], [cp1x, cp1y, cp2x, cp2y, x, y]
        )

    # Text methods
    def fill_text(self, text, x, y, max_width=None):
        """Fill a given text at the given ``(x, y)`` position. Optionally with a maximum width to draw."""
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["fillText"], [text, x, y, max_width]
        )

    def stroke_text(self, text, x, y, max_width=None):
        """Stroke a given text at the given ``(x, y)`` position. Optionally with a maximum width to draw."""
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["strokeText"], [text, x, y, max_width]
        )

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
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["setLineDash"], [self._line_dash]
        )

    # Image methods
    def draw_image(self, image, x=0, y=0, width=None, height=None):
        """Draw an ``image`` on the Canvas at the coordinates (``x``, ``y``) and scale it to (``width``, ``height``)."""
        if not isinstance(image, (Canvas, MultiCanvas, Image)):
            raise TypeError(
                "The image argument should be an Image, a Canvas or a MultiCanvas widget"
            )

        if width is not None and height is None:
            height = width

        serialized_image = widget_serialization["to_json"](image, None)

        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["drawImage"], [serialized_image, x, y, width, height]
        )

    def put_image_data(self, image_data, x=0, y=0):
        """Draw an image on the Canvas.

        ``image_data`` should be  a NumPy array containing the image to draw and ``x`` and ``y`` the pixel position where to
        draw. Unlike the CanvasRenderingContext2D.putImageData method, this method **is** affected by the canvas transformation
        matrix, and supports transparency.
        """
        image_buffer = binary_image(image_data)
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["putImageData"], [x, y], [image_buffer]
        )

    def create_image_data(self, width, height):
        """Create a NumPy array of shape (width, height, 4) representing a table of pixel colors."""
        return np.zeros((width, height, 4), dtype=int)

    # Clipping
    def clip(self):
        """Turn the path currently being built into the current clipping path.

        You can use clip() instead of close_path() to close a path and turn it into a clipping
        path instead of stroking or filling the path.
        """
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["clip"])

    # Transformation methods
    def save(self):
        """Save the entire state of the canvas."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["save"])

    def restore(self):
        """Restore the most recently saved canvas state."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["restore"])

    def translate(self, x, y):
        """Move the canvas and its origin on the grid.

        ``x`` indicates the horizontal distance to move,
        and ``y`` indicates how far to move the grid vertically.
        """
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["translate"], [x, y])

    def rotate(self, angle):
        """Rotate the canvas clockwise around the current origin by the ``angle`` number of radians."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["rotate"], [angle])

    def scale(self, x, y=None):
        """Scale the canvas units by ``x`` horizontally and by ``y`` vertically. Both parameters are real numbers.

        If ``y`` is not provided, it is defaulted to the same value as ``x``.
        Values that are smaller than 1.0 reduce the unit size and values above 1.0 increase the unit size.
        Values of 1.0 leave the units the same size.
        """
        if y is None:
            y = x
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["scale"], [x, y])

    def transform(self, a, b, c, d, e, f):
        """Multiply the current transformation matrix with the matrix described by its arguments.

        The transformation matrix is described by:
        ``[[a, c, e], [b, d, f], [0, 0, 1]]``.
        """
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["transform"], [a, b, c, d, e, f]
        )

    def set_transform(self, a, b, c, d, e, f):
        """Reset the current transform to the identity matrix, and then invokes the transform() method with the same arguments.

        This basically undoes the current transformation, then sets the specified transform, all in one step.
        """
        _CANVAS_MANAGER.send_draw_command(
            self, COMMANDS["setTransform"], [a, b, c, d, e, f]
        )

    def reset_transform(self):
        """Reset the current transform to the identity matrix.

        This is the same as calling: set_transform(1, 0, 0, 1, 0, 0).
        """
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["resetTransform"])

    # Extras
    def clear(self):
        """Clear the entire canvas. This is the same as calling ``clear_rect(0, 0, canvas.width, canvas.height)``."""
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS["clear"])

    def flush(self):
        """Flush all the cached commands and clear the cache."""
        _CANVAS_MANAGER.flush()

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

    def on_key_down(self, callback, remove=False):
        """Register a callback that will be called on keyboard event."""
        self._key_down_callbacks.register_callback(callback, remove=remove)

    def __setattr__(self, name, value):
        super(Canvas, self).__setattr__(name, value)

        if name in self.ATTRS:
            # If it's a Widget we need to serialize it
            if isinstance(value, Widget):
                value = widget_serialization["to_json"](value, None)

            _CANVAS_MANAGER.send_command(
                self, [COMMANDS["set"], [self.ATTRS[name], value]]
            )

    def _handle_frontend_event(self, _, content, buffers):
        if content.get("event", "") == "client_ready":
            self._client_ready_callbacks()

        if content.get("event", "") == "mouse_move":
            self._mouse_move_callbacks(content["x"], content["y"])
        if content.get("event", "") == "mouse_down":
            self._mouse_down_callbacks(content["x"], content["y"])
        if content.get("event", "") == "mouse_up":
            self._mouse_up_callbacks(content["x"], content["y"])
        if content.get("event", "") == "mouse_out":
            self._mouse_out_callbacks(content["x"], content["y"])

        if content.get("event", "") == "touch_start":
            self._touch_start_callbacks(
                [(touch["x"], touch["y"]) for touch in content["touches"]]
            )
        if content.get("event", "") == "touch_end":
            self._touch_end_callbacks(
                [(touch["x"], touch["y"]) for touch in content["touches"]]
            )
        if content.get("event", "") == "touch_move":
            self._touch_move_callbacks(
                [(touch["x"], touch["y"]) for touch in content["touches"]]
            )
        if content.get("event", "") == "touch_cancel":
            self._touch_cancel_callbacks(
                [(touch["x"], touch["y"]) for touch in content["touches"]]
            )

        if content.get("event", "") == "key_down":
            self._key_down_callbacks(
                content["key"],
                content["shift_key"],
                content["ctrl_key"],
                content["meta_key"],
            )

    def _draw_polygons_or_linesegments(
        self,
        cmd,
        points,
        color,
        alpha,
        points_per_item,
        with_style,
        min_elements,
        item_name,
    ):
        args = []
        buffers = []

        (
            num_polygons,
            flat_points,
            points_per_item,
        ) = _serialize_list_of_polygons_or_linestrokes(
            points=points,
            points_per_item=points_per_item,
            item_name=item_name,
            min_elements=min_elements,
        )

        if with_style:
            color = np.require(color, requirements=["C"], dtype="uint8")
            if color.ndim != 1:
                color = color.ravel()

        populate_args(num_polygons, args, buffers)
        populate_args(flat_points, args, buffers)
        populate_args(points_per_item, args, buffers)
        if with_style:
            populate_args(color, args, buffers)
            populate_args(alpha, args, buffers)
        _CANVAS_MANAGER.send_draw_command(self, COMMANDS[cmd], args, buffers)


class RoughCanvas(Canvas):
    """Create a RoughCanvas widget. It gives a hand-drawn-like style to your drawings.

    Args:
        width (int): The width (in pixels) of the canvas
        height (int): The height (in pixels) of the canvas
    """

    _model_name = Unicode("RoughCanvasModel").tag(sync=True)
    _view_name = Unicode("CanvasView").tag(sync=True)

    #: (str) Sets the appearance of the filling, possible values are ``'hachure'``, ``'solid'``, ``'zigzag'``,
    #: ``'cross-hatch'``, ``'dots'``, ``'sunburst'``, ``'dashed'``, ``'zigzag-line'``.
    #: Default to ``'hachure'``.
    rough_fill_style = Enum(
        [
            "hachure",
            "solid",
            "zigzag",
            "cross-hatch",
            "dots",
            "sunburst",
            "dashed",
            "zigzag-line",
        ],
        default_value="hachure",
    )

    #: (float) Numerical value indicating how rough the drawing is. A rectangle with the roughness of 0 would be a perfect rectangle.
    #: There is no upper limit to this value, but a value over 10 is mostly useless.
    #: Default to ``'1'``.
    roughness = Float(1)

    #: (float) Numerical value indicating how curvy the lines are when drawing a sketch. A value of 0 will cause straight lines.
    #: Default to ``'1'``.
    bowing = Float(1)

    ROUGH_ATTRS = {
        "rough_fill_style": 100,
        "roughness": 101,
        "bowing": 102,
    }

    def __setattr__(self, name, value):
        super(RoughCanvas, self).__setattr__(name, value)

        if name in self.ROUGH_ATTRS:
            _CANVAS_MANAGER.send_command(
                self, [COMMANDS["set"], [self.ROUGH_ATTRS[name], value]]
            )


class MultiCanvas(_CanvasBase):
    """Create a MultiCanvas widget with n_canvases Canvas widgets.

    Args:
        n_canvases (int): The number of canvases to create
        width (int): The width (in pixels) of the canvases
        height (int): The height (in pixels) of the canvases
    """

    _model_name = Unicode("MultiCanvasModel").tag(sync=True)
    _view_name = Unicode("MultiCanvasView").tag(sync=True)

    _canvases = List(Instance(Canvas)).tag(sync=True, **widget_serialization)

    def __init__(self, n_canvases=3, *args, **kwargs):
        """Constructor."""
        super(MultiCanvas, self).__init__(
            *args, _canvases=[Canvas() for _ in range(n_canvases)], **kwargs
        )

        # The latest canvas receives events (interaction layer)
        self.on_msg(self._canvases[-1]._handle_frontend_event)

    def __getitem__(self, key):
        """Access one of the Canvas instances."""
        return self._canvases[key]

    def __setattr__(self, name, value):
        super(MultiCanvas, self).__setattr__(name, value)

        if name in ("width", "height"):
            for layer in self._canvases:
                setattr(layer, name, value)

        if name == "caching":
            _CANVAS_MANAGER._caching = value

            warnings.warn(
                "caching is deprecated and will be removed in a future release, please use hold_canvas() instead.",
                DeprecationWarning,
            )

    def __getattr__(self, name):
        if name in ("width", "height"):
            return getattr(self._canvases[0], name)

        if name == "caching":
            warnings.warn(
                "caching is deprecated and will be removed in a future release, please use hold_canvas() instead.",
                DeprecationWarning,
            )
            return _CANVAS_MANAGER._caching

        raise AttributeError(f"'MultiCanvas' object has no attribute '{name}'")

    def on_client_ready(self, callback, remove=False):
        """Register a callback that will be called when a new client is ready to receive draw commands.

        When a new client connects to the kernel he will get an empty Canvas (because the canvas is
        almost stateless, the new client does not know what draw commands were previously sent). So
        this function is useful for replaying your drawing whenever a new client connects and is
        ready to receive draw commands.
        """
        self._canvases[-1].on_client_ready(callback, remove=remove)

    def on_mouse_move(self, callback, remove=False):
        """Register a callback that will be called on mouse move."""
        self._canvases[-1].on_mouse_move(callback, remove=remove)

    def on_mouse_down(self, callback, remove=False):
        """Register a callback that will be called on mouse click down."""
        self._canvases[-1].on_mouse_down(callback, remove=remove)

    def on_mouse_up(self, callback, remove=False):
        """Register a callback that will be called on mouse click up."""
        self._canvases[-1].on_mouse_up(callback, remove=remove)

    def on_mouse_out(self, callback, remove=False):
        """Register a callback that will be called on mouse out of the canvas."""
        self._canvases[-1].on_mouse_out(callback, remove=remove)

    def on_touch_start(self, callback, remove=False):
        """Register a callback that will be called on touch start (new finger on the screen)."""
        self._canvases[-1].on_touch_start(callback, remove=remove)

    def on_touch_end(self, callback, remove=False):
        """Register a callback that will be called on touch end (a finger is not touching the screen anymore)."""
        self._canvases[-1].on_touch_end(callback, remove=remove)

    def on_touch_move(self, callback, remove=False):
        """Register a callback that will be called on touch move (finger moving on the screen)."""
        self._canvases[-1].on_touch_move(callback, remove=remove)

    def on_touch_cancel(self, callback, remove=False):
        """Register a callback that will be called on touch cancel."""
        self._canvases[-1].on_touch_cancel(callback, remove=remove)

    def on_key_down(self, callback, remove=False):
        """Register a callback that will be called on keyboard event."""
        self._canvases[-1].on_key_down(callback, remove=remove)

    def clear(self):
        """Clear the Canvas."""
        for layer in self._canvases:
            layer.clear()

    def flush(self):
        """Flush all the cached commands and clear the cache."""
        _CANVAS_MANAGER.flush()


class MultiRoughCanvas(MultiCanvas):
    """Create a MultiRoughCanvas widget with n_canvases RoughCanvas widgets.

    Args:
        n_canvases (int): The number of rough canvases to create
        width (int): The width (in pixels) of the canvases
        height (int): The height (in pixels) of the canvases
    """

    _canvases = List(Instance(RoughCanvas)).tag(sync=True, **widget_serialization)

    def __init__(self, n_canvases=3, *args, **kwargs):
        """Constructor."""
        super(MultiCanvas, self).__init__(
            *args, _canvases=[RoughCanvas() for _ in range(n_canvases)], **kwargs
        )


@contextmanager
def hold_canvas(canvas=None):
    """Hold any drawing, and perform all commands in a single shot at the end.

    This is way more efficient than sending commands one by one.
    """
    if canvas is not None:
        warnings.warn(
            "hold_canvas does not take a canvas as parameter anymore, please use hold_canvas() instead.",
            DeprecationWarning,
        )

    orig_caching = _CANVAS_MANAGER._caching

    _CANVAS_MANAGER._caching = True
    yield
    _CANVAS_MANAGER.flush()

    if not orig_caching:
        _CANVAS_MANAGER._caching = False
