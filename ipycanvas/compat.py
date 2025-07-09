# compatibility layer for offcscreen canvas and regular canvas
import sys
import os
from IPython.display import display


IPYCANVAS_DISABLE_OFFSCREEN_CANVAS =  bool(int(os.environ.get('IPYCANVAS_DISABLE_OFFSCREEN_CANVAS', '0')))


if sys.platform.startswith("emscripten") and not IPYCANVAS_DISABLE_OFFSCREEN_CANVAS:
    from .offscreen_canvas.offscreen_canvas import OffscreenCanvas as Canvas
    print("using offscreen canvas")
else:
    print("using regular canvas as offscreen canvas is disabled or not supported")
    from .canvas import Canvas as CanvasBase

    class Canvas(CanvasBase):
        """Compatibility layer for offscreen canvas and regular canvas."""
        
        def __init__(self, *args, **kwargs):
            print("initializing regular canvas")
            super().__init__(*args, **kwargs)
           
        def initialize():
            pass
        
        async def async_initialize(self):
            pass
        
        async def display(self):
            """Display the canvas in the notebook."""
            display(self)









