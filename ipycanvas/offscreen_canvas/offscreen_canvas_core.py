from ipywidgets import DOMWidget
from traitlets import Int
from .._frontend import module_name, module_version

from traitlets import Unicode
import random
import string
import numpy as np
import pyjs
import asyncio
from pathlib import Path
import pyjs


# helper function to execute a javascript file.
def _exec_js_file(filename):
    try:
        with open(filename, "r") as f:
            js_code = f.read()
        
        pyjs.js.Function(js_code)()
    except Exception as e:
        raise RuntimeError(f"Error executing JavaScript file {filename}: {e}") from e

# execute the init.js file to initialize the js environment
def _init_js():
    THIS_DIR = Path(__file__).parent
    _exec_js_file(THIS_DIR/ "js" / "init.js")
_init_js()
del _init_js

# javascript object that contains (helper-) functions
# that are implemented in the init.js file.
_ipycanvas_js = pyjs.js.globalThis["_ipycanvas"]

# we store the canvas under a random name in the globalScope
# to avoid name clashes with other canvases.
def _rand_name():
    """Generate a random name for the canvas."""
    # Generate a random string of length 8
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

# OffscreenCanvasCore contains "offscreen canvas" creating and event handling logic.
# But it **does not create** any drawing context.
# The 2d-drawing context is created in a derived class (ie OffscreenCanvas).
# This class (OffscreenCanvasCore) can also we used as a base class for other canvas types,
# For example a webgl / three.js canvas / or a pixi.js canvas.
class OffscreenCanvasCore(DOMWidget):
    """An offsceen canvas widget."""

    _model_name = Unicode('OffscreenCanvasModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _view_name = Unicode('OffscreenCanvasView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # NOTE: the  _width and _height properties are only used to initialize sizes  
    # in the frontend. Since the canvas is then transfer to the worker thread,
    # we cannot change the size of the canvas anymore.
    _width = Int(300).tag(sync=True)
    _height = Int(150).tag(sync=True)
    _name = Unicode('_canvas_0').tag(sync=True)


    def __init__(self, width=300, height=150, *args, **kwargs):

        # once the canvas is displayed, we will store the javascript canvas object
        # in the _canvas attribute
        self._canvas = None 

        # create a random name for the canvas
        _name = _rand_name()

        # this "receiver" is used to pass events from the main-ui-thread to the worker thread.
        # it is a global object in the worker thread (ie where **this code is running**).
        self._receiver_name = f"_canvas_receiver_{_name}"

        # we store the name of the canvas in the _canvas_name as a global variable
        # in the worker thread (ie where this code is running).
        self._canvas_name = f"_canvas_{_name}"

        # helper function check if we already recived the canvas from the frontend.
        self._check_if_ready = pyjs.js.Function(f"""return "{self._canvas_name}" in globalThis""") 

        # we use this numpy arrray to store the mouse state
        # this is usefull, because we can access that array on the js side as typed array
        # and just write the values to it and read them here without any conversion.
        self.arr_mouse_state = np.array([0, 0, 0, 0], dtype=np.uint32)  # [is_inside, is_down, x, y]


        # in the frontend javascript code ** in the main-ui-thread** we will call a function
        # on a global object **in the worker thread**. (via comlink)
        # this global object is called "receiver" and is created in the worker thread.
        # This is used to pass events from the main-ui-thread to the worker thread.
        # see init.js for the implementation of "receiver_factory".
        self._js_receiver = _ipycanvas_js.receiver_factory(pyjs.buffer_to_js_typed_array(self.arr_mouse_state, view=True))
        pyjs.js.globalThis[self._receiver_name] =  self._js_receiver
        
 
        super().__init__(_name=_name, _width=width, _height=height, *args, **kwargs)


    def __del__(self):
        super().__del__()
        self._js_receiver.cleanup()
        pyjs.js.Function("receiver_name","""delete globalThis[receiver_name];""")(self._receiver_name)

    # getter setter for width and height
    @property
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value):
        if self._canvas is not None:
            raise RuntimeError("OffscreenCanvasCore: Width can only be set before the canvas is displayed.")
        self._width = value
    
    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        if self._canvas is not None:
            raise RuntimeError("OffscreenCanvasCore: Height can only be set before the canvas is displayed.")
        self._height = value


    # helper function to add a callback for an event an event
    def _on_event(self, event_name, callback):

        # for the offscreen canvas, we atm make the simplification that
        # only one callback can be set for each event.
        # This might change in the future, but for now it is sufficient.
        if self._js_receiver.has_property(f"on_{event_name}"):
            raise RuntimeError(f"Event '{event_name}' already has a callback set. Only one callback is allowed per event for the OffscreenCanvasCore.")

        # if the callback is a js function, we can just set it directly.
        if isinstance(callback, pyjs.JsValue):
            self._js_receiver[f"on_{event_name}"] = callback
        
        # if the callback is a python function, we need to create a js callable.
        # since this callback needs to be deleted later, we need to store the cleanup function
        else:
            js_callback, cleanup = pyjs.create_callable(callback)
            self._js_receiver[f"on_{event_name}"] = js_callback
            cleanup_js_fname = f"_cleanup_{event_name}"
            setattr(self._js_receiver, cleanup_js_fname, cleanup)
            self._js_receiver.add_to_cleanup(cleanup_js_fname)


    def on_mouse_enter(self, callback):
        self._on_event("mouse_enter", callback)
    
    def on_mouse_out(self, callback):
        self._on_event("mouse_leave", callback)

    def on_mouse_down(self, callback):
        self._on_event("mouse_down", callback)
    
    def on_mouse_up(self, callback):
        self._on_event("mouse_up", callback)
    
    def on_mouse_move(self, callback):
        self._on_event("mouse_move", callback)

    def on_key_down(self, callback):
        self._on_event("key_down", callback)

    def on_mouse_wheel(self, callback):
        self._on_event("mouse_wheel", callback)

    def on_key_up(self, callback):
        self._on_event("key_up", callback)

    def on_key_press(self, callback):
        self._on_event("key_press", callback)
    
    # touch events:
    # since ordinary canvas does not pass the id to the callbacks, we need
    # to make this the default behavior.
    def on_touch_start(self, callback, pass_id=False):
        if not pass_id:
            def wrapped(x, y, id=None):
                callback(x, y)
            self._on_event("touch_start", wrapped)
        else:
            self._on_event("touch_start", callback)
    def on_touch_end(self, callback, pass_id=False):
        if not pass_id:
            def wrapped(x, y, id=None):
                callback(x, y)
            self._on_event("touch_end", wrapped)
        else:
            self._on_event("touch_end", callback)

    def on_touch_move(self, callback, pass_id=False):
        if not pass_id:
            def wrapped(x, y, id=None):
                callback(x, y)
            self._on_event("touch_move", wrapped)
        else:
            self._on_event("touch_move", callback)

    def on_touch_cancel(self, callback, pass_id=False):
        if not pass_id:
            def wrapped(x, y, id=None):
                callback(x, y)
            self._on_event("touch_cancel", wrapped)
        else:
            self._on_event("touch_cancel", callback)
    

    def initialize(self):
        """ Initialize the canvas after it has been displayed.

            After the canvas has been displayed, we need to call this method to initialize the canvas.
            This method can only be used when the display method has been called in a **different cell**.

            # Cell1:
            ```python
            canvas = OffscreenCanvasCore(width=800, height=600)
            display(canvas)
            ```

            # Cell2:
            ```python
            canvas.initialize()
            # Now you can use the canvas
            # ...
            ```

            For more information, see the `async_initialize` method.
        """
        if not self._check_if_ready():
            raise RuntimeError(f"Canvas {self._canvas_name} is not ready. Call await canvas.adisplay() to display the canvas.") 
        self._canvas = pyjs.js.globalThis[self._canvas_name]
    
    async def async_initialize(self):
        """If we want to use the canvas in the same cell where it 
            was created **and displayed** we need to call this async function.
            While this sounds a bit counterintuitive, it is necessary because the
            offscreen canvas is created as regular canvas in the main-thread,
            and transfered to and recieved by the worker-thread. This transfering mechanism (in particular the
            receiving part) would be blocked by the cell execution.
            To get a chance to  receive the canvas in the worker-thread (ie where
            the kernel is running), we need to do run some asyc code (with some sleeping in between)

            ```python
            canvas = OffscreenCanvasCore(width=800, height=600)
            display(canvas)
            await canvas.async_initialize()
            # canvas is now ready to use
            # ...
        """

        
        c = 0
        while not  self._check_if_ready():
            await asyncio.sleep(0.1)
            c += 1
            if c >= 20:
                raise RuntimeError(f"Canvas {self._canvas_name} was not created in time.")
        
        self._canvas = pyjs.js.globalThis[self._canvas_name]

    def get_canvas(self):
        """Get the offscreen canvas javascript objectt."""
        if self._canvas is None:
            raise RuntimeError("Canvas is not displayed yet.")
        return self._canvas

    # mouse state
    def mouse_is_down(self):
        """Check if the mouse is currently pressed down."""
        return self.arr_mouse_state[1] == 1
    def mouse_is_inside(self):
        """Check if the mouse is currently inside the canvas."""
        return self.arr_mouse_state[0] == 1
    def mouse_position(self):
        """Get the current mouse position as a tuple (x, y)."""
        return (self.arr_mouse_state[2], self.arr_mouse_state[3])

