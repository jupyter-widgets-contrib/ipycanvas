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


def _exec_js_file(filename):
    try:
        with open(filename, "r") as f:
            js_code = f.read()
        
        pyjs.js.Function(js_code)()
    except Exception as e:
        raise RuntimeError(f"Error executing JavaScript file {filename}: {e}") from e


def _init_js():
    THIS_DIR = Path(__file__).parent
    _exec_js_file(THIS_DIR/ "js" / "init.js")
_init_js()
del _init_js


# javascript object that contains (helper-) functions
# that are implemented \
_ipycanvas_js = pyjs.js.globalThis["_ipycanvas"]



def _rand_name():
    """Generate a random name for the canvas."""
    # Generate a random string of length 8
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class OffscreenCanvasCore(DOMWidget):
    """An offsceen canvas widget."""

    _model_name = Unicode('OffscreenCanvasModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _view_name = Unicode('OffscreenCanvasView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    _width = Int(300).tag(sync=True)
    _height = Int(150).tag(sync=True)
    _name = Unicode('_canvas_0').tag(sync=True)


    def __init__(self, width=300, height=150, *args, **kwargs):

        self._canvas = None  # will be set when the canvas is displayed

        _name = _rand_name()
        self._receiver_name = f"_canvas_receiver_{_name}"
        self._canvas_name = f"_canvas_{_name}"

        # helper js function to check if the canvas is ready
        self._check_if_ready = pyjs.js.Function(f"""return "{self._canvas_name}" in globalThis""") 

   
        self.arr_mouse_state = np.array([0, 0, 0, 0], dtype=np.uint32)  # [is_inside, is_down, x, y]


        # in the frontend javascript code ** in the main-ui-thread** we will call a function
        # on a global object **in the worker thread**. (via comlink)
        # this global object is called "receiver" and is created in the worker thread.
        # This is used to pass events from the main-ui-thread to the worker thread.
        self._js_receiver = _ipycanvas_js.receiver_factory(pyjs.buffer_to_js_typed_array(self.arr_mouse_state, view=True))
        pyjs.js.globalThis[self._receiver_name] =  self._js_receiver

        # for the offscreen canvas we allow only **one** callback per event
        # this is different to the normal canvas, where we allow multiple callbacks.
        # we throw an error if the user tries to set multiple callbacks for the same event.
 
        super().__init__(_name=_name, _width=width, _height=height, *args, **kwargs)


    def __del__(self):
        super().__del__()
        self._js_receiver.cleanup()
        pyjs.js.Function("receiver_name","""delete globalThis[receiver_name];""")(self._receiver_name)

    # getter setter for width and height
    @property
    def width(self):
        if self._canvas is None:
            return self._width
        return self._canvas.width
    
    @width.setter
    def width(self, value):
        assert self._canvas is not None, "Canvas is not displayed yet."
        self._canvas.width = value
        self._width = value
    
    @property
    def height(self):
        if self._canvas is None:
            return self._height
        return self._canvas.height
    
    @height.setter
    def height(self, value):
        assert self._canvas is not None, "Canvas is not displayed yet."
        self._canvas.height = value
        self._height = value


    def _on_event(self, event_name, callback):
        if self._js_receiver.has_property(f"on_{event_name}"):
            raise RuntimeError(f"Event '{event_name}' already has a callback set. Only one callback is allowed per event for the OffscreenCanvasCore.")


        if isinstance(callback, pyjs.JsValue):
            self._js_receiver[f"on_{event_name}"] = callback
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
        if not self._check_if_ready():
            raise RuntimeError(f"Canvas {self._canvas_name} is not ready. Call await canvas.adisplay() to display the canvas.") 
        self._canvas = pyjs.js.globalThis[self._canvas_name]
    
    async def async_initialize(self):
        c = 0
        while not  self._check_if_ready():
            await asyncio.sleep(0.1)
            c += 1
            if c >= 20:
                raise RuntimeError(f"Canvas {self._canvas_name} was not created in time.")
        
        self._canvas = pyjs.js.globalThis[self._canvas_name]

    def get_canvas(self):
        """Get the offscreen canvas element."""
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

