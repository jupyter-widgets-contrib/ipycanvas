from .offscreen_canvas_core import OffscreenCanvasCore
from contextlib import contextmanager
from functools import partial,partialmethod
import pyjs
import numpy as np
from numbers import Number
from pathlib import Path
from IPython.display import display
from ipywidgets import Image as IpywidgetImage
import io
import PIL

@contextmanager
def hold_canvas(canvas):
    yield None








class OffscreenCanvas(OffscreenCanvasCore):
    


    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        initial_buffer_size = 10
        n_buffers = 8 # max number of args / buffers we need at the same time
        self._buffers = [ np.zeros(initial_buffer_size, dtype=np.float32) for _ in range(n_buffers)]
        self._js_buffers = [
            pyjs.buffer_to_js_typed_array(fbuffer, view=True) for fbuffer in self._buffers
        ]

    def initialize(self):
        super().initialize()
        if  self._canvas is None:
            raise RuntimeError("Canvas is not displayed yet")
        self._ctx = self._canvas.getContext("2d")

    async def async_initialize(self):
        """Initialize the canvas asynchronously."""
        await super().async_initialize()
        if  self._canvas is None:
            raise RuntimeError("Canvas is not displayed yet")
        self._ctx = self._canvas.getContext("2d")
    
    async def display(self):
        display(self)
        await self.async_initialize()

    
    def _ensure_size(self, index, size):
        buffer_size = len(self._buffers[index])
        if size > buffer_size:
            # resize the buffer
            new_size = max(size, buffer_size * 2)
            new_buffer = np.zeros(new_size, dtype=np.float32)
            self._buffers[index] =  new_buffer
            self._js_buffers[index] = pyjs.buffer_to_js_typed_array(new_buffer, view=True)

    def _points_to_buffer(self,index, points):
        points = np.require(points, requirements='C', dtype=np.float32)
        n_points = int(points.shape[0])
        n_points2 = 2 * n_points
        self._ensure_size(index, n_points2)
        self._buffers[index][:n_points2] = points.flatten()
        return n_points

    


    # ipycanvas api
    def clear(self):
        self._ctx.clearRect(0, 0, self._canvas.width, self._canvas.height)
    
    def sleep(self, seconds):
        """in the non-lite version this sleeps in the fronend / canvas, but not in the kernel.
        THis make little sense  in the offscreen canvas version, since the canvas **is** the frontend.
        """
        pass



    def create_linear_gradient(self):
        raise NotImplementedError("create_linear_gradient is not implemented in the offscreen canvas version yet")
    def create_radial_gradient(self):
        raise NotImplementedError("create_radial_gradient is not implemented in the offscreen canvas version yet")        
    def create_pattern(self):
        raise NotImplementedError("create_pattern is not implemented in the offscreen canvas version yet")
    def fill_rect(self, x, y, width, height):
        self._ctx.fillRect(x, y, width, height)
    def stroke_rect(self, x, y, width, height):
        self._ctx.strokeRect(x, y, width, height)
    def clear_rect(self):
        self._ctx.clearRect(x, y, width, height)
    def fill_arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        self._ctx.fillArc(x, y, radius, start_angle, end_angle, anticlockwise)
    def fill_circle(self, x, y, radius):
        self._ctx.fillCircle(x, y, radius)
    def stroke_arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        self._ctx.strokeArc(x, y, radius, start_angle, end_angle, anticlockwise)
    def stroke_circle(self, x, y, radius):
        self._ctx.strokeCircle(x, y, radius)



    def fill_polygon(self, points):
        n_points = self._points_to_buffer(0, points)
        self._ctx.fillPolygon(n_points, self._js_buffers[0] )

    def stroke_polygon(self, points):
        n_points = self._points_to_buffer(0, points)
        self._ctx.strokePolygon(n_points ,self._js_buffers[0])

    def fill_and_stroke_polygon(self, points):
        n_points = self._points_to_buffer(0, points)
        self._ctx.fillAndStrokePolygon(n_points, self._js_buffers[0])

    def stroke_line(self, x1, y1, x2, y2):
        self._ctx.strokeLine(x1, y1, x2, y2)
    def begin_path(self):
        self._ctx.beginPath()
    def close_path(self):
        self._ctx.closePath()
    def stroke(self):
        self._ctx.stroke()
    def fill(self):
        self._ctx.fill()
    def move_to(self, x, y):
        self._ctx.moveTo(x, y)
    def line_to(self, x, y):
        self._ctx.lineTo(x, y)
    def rect(self, x, y, width, height):
        self._ctx.rect(x, y, width, height)
    def arc(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        self._ctx.arc(x, y, radius, start_angle, end_angle, anticlockwise)  
    def ellipse(self, x, y, radius_x, radius_y, rotation=0, start_angle=0, end_angle=2 * 3.14159, anticlockwise=False):
        self._ctx.ellipse(x, y, radius_x, radius_y, rotation, start_angle, end_angle, anticlockwise)
    def arc_to(self, x1, y1, x2, y2, radius):
        self._ctx.arcTo(x1, y1, x2, y2, radius)
    def quadratic_curve_to(self, cp_x, cp_y, to_x, to_y):
        self._ctx.quadraticCurveTo(cp_x, cp_y, to_x, to_y)
    def bezier_curve_to(self, cp1_x, cp1_y, cp2_x, cp2_y, to_x, to_y):
        self._ctx.bezierCurveTo(cp1_x, cp1_y, cp2_x, cp2_y, to_x, to_y)
    def fill_text(self, text, x, y, max_width=None):
        if max_width is not None:
            self._ctx.fillText(text, x, y, max_width)
        else:
            self._ctx.fillText(text, x, y)
    def stroke_text(self, text, x, y, max_width=None):
        if max_width is not None:
            self._ctx.strokeText(text, x, y, max_width)
        else:
            self._ctx.strokeText(text, x, y)
    def get_line_dash(self):
        raise NotImplementedError("get_line_dash is not implemented in the offscreen canvas version yet")
    def set_line_dash(self, segments):
        raise NotImplementedError("set_line_dash is not implemented in the offscreen canvas version yet")
    def draw_image(self):
        raise NotImplementedError("draw_image is not implemented in the offscreen canvas version yet")
    def put_image_data(self, image_data, dx, dy, dirty_x=None, dirty_y=None, dirty_width=None, dirty_height=None):
        raise NotImplementedError("put_image_data is not implemented in the offscreen canvas version yet")
    def create_image_data(self, sw=None, sh=None):
        raise NotImplementedError("create_image_data is not implemented in the offscreen canvas version yet")
    def clip(self):
        self._ctx.clip()
    def save(self):
        self._ctx.save()
    def restore(self):
        self._ctx.restore()
    def translate(self, x, y):
        self._ctx.translate(x, y)
        
    def rotate(self, angle):
        self._ctx.rotate(angle)
        
    def scale(self, x, y):
        self._ctx.scale(x, y)
        
    def transform(self, a, b, c, d, e, f):
        self._ctx.transform(a, b, c, d, e, f)
        
    def set_transform(self, a, b, c, d, e, f):
        self._ctx.setTransform(a, b, c, d, e, f)
    def reset_transform(self):
        self._ctx.resetTransform()  
    def clear(self):
        """Clear the canvas."""
        self._ctx.clearRect(0, 0, self._canvas.width, self._canvas.height)
        
    def flush(self):
        """Flush the canvas. In the offscreen canvas version this does nothing."""
        pass


    def create_linear_gradient(self, x0, y0, x1, y1, color_stops):
        """Create a linear gradient."""
        gradient = self._ctx.createLinearGradient(x0, y0, x1, y1)
        for offset, color in color_stops:
            gradient.addColorStop(offset, color)
        return gradient
    
    def create_radial_gradient(self, x0, y0, r0, x1, y1, r1, color_stops):
        """Create a radial gradient."""
        gradient = self._ctx.createRadialGradient(x0, y0, r0, x1, y1, r1)
        for offset, color in color_stops:
            gradient.addColorStop(offset, color)
        return gradient

    def create_pattern(self, image, repetition='repeat'):
        if isinstance(image, OffscreenCanvasCore):
            # if the image is an OffscreenCanvasCore, we need to convert it to a js image
            image = image._canvas
        else:
            raise NotImplementedError("create_pattern only supports OffscreenCanvas images at the moment")
        
        """Create a pattern."""
        pattern = self._ctx.createPattern(image, repetition)
        return pattern
    
    def draw_image(self, image, dx, dy, dw=None, dh=None):
        """Draw an image on the canvas."""
        if isinstance(image, OffscreenCanvasCore):
            # if the image is an OffscreenCanvasCore, we need to convert it to a js image
            drawable_image = image._canvas




        elif isinstance(image, IpywidgetImage):
            if dw is not None and dh is not None:
                raise NotImplementedError("ipywidget.Image does not support width and height parameters in draw_image")

            # convert to stream an open with pillow
            data_stream = io.BytesIO(image.value)
            pil_img = PIL.Image.open(data_stream)

            # convert to RGBA if not already in that mode
            if pil_img.mode != 'RGBA':
                pil_img = pil_img.convert('RGBA'
            )

            # convert to numpy
            img_rgba = np.array(pil_img) 

            # create a js array view (this will be of the type Uint8)
            js_arr = pyjs.buffer_to_js_typed_array(img_rgba.ravel(), view=True)
            # convert to Uint8ClampedArray without copying the data
            js_arr = pyjs.js.Uint8ClampedArray.new(js_arr.buffer, js_arr.byteOffset, js_arr.length)

            # create settings to ensure the pixel format is correct
            settings = pyjs.js_object()
            settings.pixelFormat = "rgba-unorm8"

            # create the ImageData object
            image = pyjs.js.ImageData.new(js_arr, pil_img.width, pil_img.height, settings)

            # create an OffscreenCanvas and draw the image data on it
            offscreen_canvas = pyjs.js.OffscreenCanvas.new( pil_img.width, pil_img.height)
            ctx = offscreen_canvas.getContext('2d')

            # put the image data on the offscreen canvas
            ctx.putImageData(image,0,0)
            drawable_image = offscreen_canvas
          
        else:
            raise NotImplementedError("draw_image only supports OffscreenCanvas and ipywidget.Image as images at the moment")

        if dw is not None and dh is not None:
            self._ctx.drawImage(drawable_image, dx, dy, dw, dh)
        else:
            self._ctx.drawImage(drawable_image, dx, dy)    
    
    def put_image_data(self, image_data, x=0,y=0):
        n_dim = image_data.ndim
        width = image_data.shape[0]
        height = image_data.shape[1]
        if n_dim == 2:
            # grayscale image
            # convert to RGBA
            image_data = np.stack((image_data,)*3, axis=-1)
            image_data = np.concatenate((image_data, np.full(image_data.shape[:2] + (1,), 255)), axis=-1)

            
        elif n_dim == 3 and image_data.shape[-1] == 1:
            # single channel image (grayscale)
            # convert to RGBA
            image_data = np.concatenate((image_data, np.full(image_data.shape[:2] + (1,), 255)), axis=-1)

        elif n_dim == 3: 
            # RGB image
            if image_data.shape[-1] == 3:
                # add alpha channel
                image_data = np.concatenate((image_data, np.full(image_data.shape[:2] + (1,), 255)), axis=-1)
            elif image_data.shape[-1] == 4:
                # already RGBA
                pass
            else:
                raise ValueError("Image data must be 2D or 3D with 3 or 4 channels")

        image_data = np.require(image_data, requirements='C', dtype=np.uint8)

        # create a js array view (this will be of the type Uint8)
        js_arr = pyjs.buffer_to_js_typed_array(image_data.ravel(), view=True)
        # convert to Uint8ClampedArray without copying the data
        js_arr = pyjs.js.Uint8ClampedArray.new(js_arr.buffer, js_arr.byteOffset, js_arr.length)

        # create settings to ensure the pixel format is correct
        settings = pyjs.js_object()
        settings.pixelFormat = "rgba-unorm8"

        image = pyjs.js.ImageData.new(js_arr, width, height, settings)

        # put_image_data on the offscreen canvas
        self._ctx.putImageData(image, x, y)

    # BATCH API

    # Canvas.stroke_lines()
    # Canvas.stroke_styled_line_segments()
    # Canvas.stroke_line_segments()

    def _fill_buffer_with_scalars(self, index, value):
        # is number ? 
        if isinstance(value, Number):
            self._ensure_size(index, 1)
            self._buffers[index][0] = value
            return 1
        else: # assume iterable
            value = np.require(value, requirements='C', dtype=np.float32)
            n_values = int(value.shape[0])
            self._ensure_size(index, n_values)
            self._buffers[index][:n_values] = value
            return n_values
    
    def _fill_buffer_with_colors(self, index, color):
        arr = np.require(color, requirements='C', dtype=np.float32).flatten()
        self._ensure_size(index, len(arr))
        self._buffers[index][:len(arr)] = arr
        return len(arr) / 3





    def fill_styled_circles(self, x, y, radius, color, alpha=1):
        self._buffers[5][0:5] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
            self._fill_buffer_with_colors(3, color),
            self._fill_buffer_with_scalars(4, alpha),
        ]   
        self._ctx.fillStyledCircles(*self._js_buffers[:6])

    def stroke_styled_circles(self, x, y, radius, color, alpha=1):
        self._buffers[5][0:5] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
            self._fill_buffer_with_colors(3, color),
            self._fill_buffer_with_scalars(4, alpha),
        ]   
        self._ctx.strokeStyledCircles(*self._js_buffers[:6])
    
    def fill_circles(self, x, y, radius):
        self._buffers[3][0:3] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
        ]
        self._ctx.fillCircles(*self._js_buffers[:4])
    
    def stroke_circles(self, x, y, radius):
        self._buffers[3][0:3] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
        ]
        self._ctx.strokeCircles(*self._js_buffers[:4])
    
    def fill_rects(self, x, y, width, height):
        self._buffers[4][0:4] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, width),
            self._fill_buffer_with_scalars(3, height),
        ]
        self._ctx.fillRects(*self._js_buffers[:5])
    
    def stroke_rects(self, x, y, width, height):
        self._buffers[4][0:4] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, width),
            self._fill_buffer_with_scalars(3, height),
        ]
        self._ctx.strokeRects(*self._js_buffers[:5])
    
    def fill_styled_rects(self, x, y, width, height, color, alpha=1):
        self._buffers[6][0:6] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, width),
            self._fill_buffer_with_scalars(3, height),
            self._fill_buffer_with_colors(4, color),
            self._fill_buffer_with_scalars(5, alpha),
        ]
        self._ctx.fillStyledRects(*self._js_buffers[:7])
    
    def stroke_styled_rects(self, x, y, width, height, color, alpha=1):
        self._buffers[6][0:6] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, width),
            self._fill_buffer_with_scalars(3, height),
            self._fill_buffer_with_colors(4, color),
            self._fill_buffer_with_scalars(5, alpha),
        ]
        self._ctx.strokeStyledRects(*self._js_buffers[:7])
    
    # Canvas.fill_arcs()
    # Canvas.stroke_arcs()
    # Canvas.fill_styled_arcs()
    # Canvas.stroke_styled_arcs()

    def fill_arcs(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        self._buffers[5][0:5] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
            self._fill_buffer_with_scalars(3, start_angle),
            self._fill_buffer_with_scalars(4, end_angle),
        ]
        self._ctx.fillArcs(*self._js_buffers[:6], anticlockwise)
    
    def stroke_arcs(self, x, y, radius, start_angle, end_angle, anticlockwise=False):
        self._buffers[5][0:5] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
            self._fill_buffer_with_scalars(3, start_angle),
            self._fill_buffer_with_scalars(4, end_angle),
        ]
        self._ctx.strokeArcs(*self._js_buffers[:6], anticlockwise)
    
    def fill_styled_arcs(self, x, y, radius, start_angle, end_angle, color, alpha=1, anticlockwise=False):
        self._buffers[7][0:7] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
            self._fill_buffer_with_scalars(3, start_angle),
            self._fill_buffer_with_scalars(4, end_angle),
            self._fill_buffer_with_colors(5, color),
            self._fill_buffer_with_scalars(6, alpha),
        ]
        self._ctx.fillStyledArcs(*self._js_buffers[:8], anticlockwise)
    
    def stroke_styled_arcs(self, x, y, radius, start_angle, end_angle, color, alpha=1, anticlockwise=False):
        self._buffers[7][0:7] = [
            self._fill_buffer_with_scalars(0, x),
            self._fill_buffer_with_scalars(1, y),
            self._fill_buffer_with_scalars(2, radius),
            self._fill_buffer_with_scalars(3, start_angle),
            self._fill_buffer_with_scalars(4, end_angle),
            self._fill_buffer_with_colors(5, color),
            self._fill_buffer_with_scalars(6, alpha),
        ]
        self._ctx.strokeStyledArcs(*self._js_buffers[:8], anticlockwise)

    # for polygons / line segments with potentially different number of points per polygon / line segment
    def _prepare_multipoint(self, points, points_per_item=None):
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

            return flat_points, points_per_item, num_polygons
        else:
            raise RuntimeError("points must be a list of numpy arrays or a numpy array with shape (n,2)")

    def fill_polygons(self, points, points_per_polygon=None):
        flat_points, points_per_item, num_items = self._prepare_multipoint(points, points_per_polygon)
        self._buffers[2][0:2] = [
            self._fill_buffer_with_scalars(0, flat_points),
            self._fill_buffer_with_scalars(1, points_per_item),
        ]
        self._ctx.fillPolygons(num_items, *self._js_buffers[:3])
    
    def stroke_polygons(self, points, points_per_polygon=None):
        flat_points, points_per_item, num_items = self._prepare_multipoint(points, points_per_polygon)
        self._buffers[2][0:2] = [
            self._fill_buffer_with_scalars(0, flat_points),
            self._fill_buffer_with_scalars(1, points_per_item)
        ]
        self._ctx.strokePolygons(num_items, *self._js_buffers[:3])

    def fill_styled_polygons(self, points, color, alpha=1, points_per_polygon=None): 
        flat_points, points_per_item, num_items = self._prepare_multipoint(points, points_per_polygon)
        self._buffers[4][0:4] = [
            self._fill_buffer_with_scalars(0, flat_points),
            self._fill_buffer_with_scalars(1, points_per_item),
            self._fill_buffer_with_colors(2,  color),
            self._fill_buffer_with_scalars(3, alpha),
        ]
        self._ctx.fillStyledPolygons(num_items, *self._js_buffers[:5])
    
    def stroke_styled_polygons(self, points, color, alpha=1, points_per_polygon=None):
        flat_points, points_per_item, num_items = self._prepare_multipoint(points, points_per_polygon)
        self._buffers[4][0:4] = [
            self._fill_buffer_with_scalars(0, flat_points.shape[0]),
            self._fill_buffer_with_scalars(1, points_per_item.shape[0]),
            self._fill_buffer_with_colors(2,  color),
            self._fill_buffer_with_scalars(3, alpha),
        ]
        self._ctx.strokeStyledPolygons(num_items, *self._js_buffers[:5])

    # stroke_line_segments
    def stroke_line_segments(self, points, points_per_segment=None):
        flat_points, points_per_item, num_items = self._prepare_multipoint(points, points_per_segment)
        self._buffers[2][0:2] = [
            self._fill_buffer_with_scalars(0, flat_points),
            self._fill_buffer_with_scalars(1, points_per_item)
        ]
        self._ctx.strokeLineSegments(num_items, *self._js_buffers[:3])
    
    def stroke_styled_line_segments(self, points, color, alpha=1, points_per_segment=None):
        flat_points, points_per_item, num_items = self._prepare_multipoint(points, points_per_segment)
        self._buffers[4][0:4] = [
            self._fill_buffer_with_scalars(0, flat_points),
            self._fill_buffer_with_scalars(1, points_per_item),
            self._fill_buffer_with_colors(2, color),
            self._fill_buffer_with_scalars(3, alpha),
        ]
        self._ctx.strokeStyledLineSegments(num_items, *self._js_buffers[:5])



def _make_prop(js_name):
    @property
    def prop(self):
        return getattr(self._ctx, js_name)
    @prop.setter
    def prop(self, value):
        setattr(self._ctx, js_name, value)

    return prop


def _extend_canvas():

    # add properties to the Canvas class
    py_to_js_name = {
        'fill_style': 'fillStyle',
        'stroke_style': 'strokeStyle',
        'global_alpha': 'globalAlpha',
        'font': 'font',
        'text_align': 'textAlign',
        'text_baseline': 'textBaseline',
        'direction': 'direction',
        'global_composite_operation': 'globalCompositeOperation',
        'shadow_offset_x': 'shadowOffsetX',
        'shadow_offset_y': 'shadowOffsetY',
        'shadow_blur': 'shadowBlur',
        'shadow_color': 'shadowColor',
        'line_width': 'lineWidth',
        'line_cap': 'lineCap',
        'line_join': 'lineJoin',
        'miter_limit': 'miterLimit',
        'filter': 'filter',
        'image_smoothing_enabled': 'imageSmoothingEnabled',
        'line_dash_offset': 'lineDashOffset'
    }
    for py_name, js_name in py_to_js_name.items():
        prop = _make_prop(js_name)
        setattr(OffscreenCanvas, py_name, prop)


_extend_canvas()
del _extend_canvas



