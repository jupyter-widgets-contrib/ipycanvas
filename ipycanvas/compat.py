# compatibility layer for offcscreen canvas and regular canvas
import sys
import os
from IPython.display import display

# this is very usefull for testing compatibility with offscreen canvas
IPYCANVAS_DISABLE_OFFSCREEN_CANVAS =  bool(int(os.environ.get('IPYCANVAS_DISABLE_OFFSCREEN_CANVAS', '0')))

import sys
is_emscripten = sys.platform.startswith("emscripten")

# has pyjs
has_pyjs = True
try:
    import pyjs
except ImportError:
    has_pyjs = False

if (is_emscripten and has_pyjs) and not IPYCANVAS_DISABLE_OFFSCREEN_CANVAS:
    from .offscreen_canvas.offscreen_canvas import OffscreenCanvas as Canvas
else:
    from .canvas import Canvas as CanvasBase

    class Canvas(CanvasBase):
        """Compatibility layer for offscreen canvas and regular canvas."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
           
        def initialize():
            """
                After the canvas has been displayed, we need to call this method to initialize the canvas.
                This method can only be used when the display method has been called in a **different cell**.

                # Cell1:
                ```python
                from ipycanvas.compat import Canvas
                from IPython.display import display
                canvas = Canvas(width=800, height=600)
                display(canvas)
                ```

                # Cell2:
                ```python
                canvas.initialize()
                ```

                For more information, see the `async_initialize` method.

            """
        
        async def async_initialize(self):
            """
        
                If we want to use the canvas in the same cell where it 
                was created **and displayed** we need to call this async function.
                While this sounds a bit counterintuitive, it is necessary because the
                offscreen canvas is created as regular canvas in the main-thread,
                and transfered to and recieved by the worker-thread. This transfering mechanism (in particular the
                receiving part) would be blocked by the cell execution.
                To get a chance to  receive the canvas in the worker-thread (ie where
                the kernel is running), we need to do run some asyc code (with some sleeping in between)
                Note that for an ordinary canvas, `async_initialize` is a no-op.

            from ipycanvas.compat import Canvas
            from IPython.display import display
            canvas = Canvas(width=800, height=600)
            display(canvas)
            await canvas.async_initialize()

            # canvas is now ready to use
            canvas.fill_style = 'red'


            """
        
        async def display(self):
            """ shorthand for displaying the canvas and then initializing it.
            See `async_initialize` for more information.
            """

            display(self)
