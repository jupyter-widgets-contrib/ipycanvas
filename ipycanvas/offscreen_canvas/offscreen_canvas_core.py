from ipywidgets import DOMWidget
from traitlets import Int
from .._frontend import module_name, module_version

from traitlets import Unicode
import random
import string
import numpy as np
import pyjs
import asyncio


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

    width = Int(300).tag(sync=True)
    height = Int(150).tag(sync=True)
    _name = Unicode('_canvas_0').tag(sync=True)


    def __init__(self, *args, **kwargs):

        self._canvas = None  # will be set when the canvas is displayed

        _name = _rand_name()
        self._reciver_name = f"_canvas_reciver_{_name}"
        self._canvas_name = f"_canvas_{_name}"

        # helper js function to check if the canvas is ready
        self._check_if_ready = pyjs.js.Function(f"""return "{self._canvas_name}" in globalThis""") 

   


        self.arr_mouse_state = np.array([0, 0, 0, 0], dtype=np.uint32)  # [is_inside, is_down, x, y]

        
        self._js_reciver = pyjs.js.globalThis.Function("arr","""return {
            arr_mouse_state : arr,
            on_mouse_events: function(event, x, y) {

                if (event === "mouseenter") {
                    this.arr_mouse_state[0] = 1;  // is_inside
                    this.arr_mouse_state[1] = 0;  // is_down

                    if (this.on_mouse_enter) {
                        this.on_mouse_enter(x, y);
                    }

                } else if (event === "mouseleave") {
                    this.arr_mouse_state[0] = 0;  // is_inside
                    this.arr_mouse_state[1] = 0;  // is_down

                    if (this.on_mouse_leave) {
                        this.on_mouse_leave(x, y);
                    }

                } else if (event === "mousedown") {
                    this.arr_mouse_state[1] = 1;  // is_down
                    if (this.on_mouse_down) {
                        this.on_mouse_down(x, y);
                    }

                } else if (event === "mouseup") {
                    this.arr_mouse_state[1] = 0;  // is_down
                    if (this.on_mouse_up) {
                        this.on_mouse_up(x, y);
                    }
                }
                else if (event === "mousemove") {
                    if (this.on_mouse_move) {
                        this.on_mouse_move(x, y);
                    }
                }
                // always update the mouse position
                this.arr_mouse_state[2] = x;  // x position
                this.arr_mouse_state[3] = y;  // y position
            },
        }""")(pyjs.buffer_to_js_typed_array(self.arr_mouse_state, view=True))

        pyjs.js.globalThis[self._reciver_name] =  self._js_reciver

        super().__init__(_name=_name, *args, **kwargs)


    def __del__(self):
        super().__del__()

        """Cleanup the canvas when the object is deleted."""
        pyjs.js.Function("reciver","reciver_name","""
            if(recive._cleanup_mouse_enter) {
                reciver._cleanup_mouse_enter.delete();
            }
            if(reciver._cleanup_mouse_leave) {
                reciver._cleanup_mouse_leave.delete();
            }
            if(reciver._cleanup_mouse_down) {
                reciver._cleanup_mouse_down.delete();
            }
            if(reciver._cleanup_mouse_up) {
                reciver._cleanup_mouse_up.delete();
            }
            if(reciver._cleanup_mouse_move) {
                reciver._cleanup_mouse_move.delete();
            }
            delete globalThis[reciver_name];
        """)(self._js_reciver, self._reciver_name)



    def _on_mouse_event(self, event_name, callback):
        """Helper function to set mouse event callbacks."""


        if isinstance(callback, pyjs.JsValue):
            self._js_reciver[f"on_{event_name}"] = callback
        else:
            js_callback, cleanup = pyjs.create_callable(callback)
            self._js_reciver[f"on_{event_name}"] = js_callback
            setattr(self._js_reciver, f"_cleanup_{event_name}", cleanup)
    
    def on_mouse_enter(self, callback):
        self._on_mouse_event("mouse_enter", callback)
    
    def on_mouse_leave(self, callback):
        self._on_mouse_event("mouse_leave", callback)

    def on_mouse_down(self, callback):
        self._on_mouse_event("mouse_down", callback)
    
    def on_mouse_up(self, callback):
        self._on_mouse_event("mouse_up", callback)
    
    def on_mouse_move(self, callback):
        self._on_mouse_event("mouse_move", callback)


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

