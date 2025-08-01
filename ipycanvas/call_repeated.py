"""
    this module provides a way to call a function repeatedly at a given frame rate.
    It is used to set a render loop for the canvas.
    It works with both offscreen canvas and regular canvas.

    When we are in a emscripten/wasm/lite environment, we can
    make use of the browsers requestAnimationFrame function.
    In a regular python environment, we use asyncio to call the function repeatedly
    as a task (we need to make it a task st. its not blocking the kernel,
    because otherwise we could not recieve events from the frontend).
"""

import time
import sys
from .canvas import hold_canvas as hold_classic_canvas

import sys
is_emscripten = sys.platform.startswith("emscripten")

# has pyjs
has_pyjs = True
try:
    import pyjs
except ImportError:
    has_pyjs = False

    
# if we are in a emscripten/wasm/lite environment, we can use the pyjs module
if has_pyjs and is_emscripten:
    import pyjs
    from .offscreen_canvas.offscreen_canvas_core import OffscreenCanvasCore

    # call a function repeatedly at a given frame rate
    # when fps is 0, requestAnimationFrame is used
    def call_repeated(func, fps=0):
        """Call a function repeatedly at a given frame rate.
        If fps is 0, requestAnimationFrame is used.

        Args:
            func: The function to call repeatedly.
            fps: The frame rate to call the function at. If 0, requestAnimationFrame
        """
        pyjs.set_main_loop_callback(func, fps)

    # set a render loop for the canvas
    # this is used to call the function repeatedly at a given frame rate
    # if the canvas is **not** an offscreen canvas, we use the hold_canvas context manager
    # st. we we only send one message to the frontend per frame
    def set_render_loop(canvas, func, fps=0):
        """Set a render loop for the canvas.
        This is used to call the function repeatedly at a given frame rate.
        If the canvas is **not** an offscreen canvas, we use the hold_canvas context
        manager st. we only send one message to the frontend per frame.

        Args:
            canvas: The canvas to set the render loop for.
            func: The function to call repeatedly.
            fps: The frame rate to call the function at. If 0, requestAnimationFrame
        """
        if isinstance(canvas, OffscreenCanvasCore):
            def wrapped_func(dt):
                try:
                    func(dt)
                except Exception as e:
                    # the best we can do there is catch the error and print it to the error stream
                    print(f"Error in requestAnimationFrame callback: {e}", file=sys.stderr)
                    pyjs.cancel_main_loop()
            pyjs.set_main_loop_callback(wrapped_func, 0)
        else:
            # For regular canvas we wrap eveything in a "hold_canvas" function
            def wrapped_func(dt):
                with hold_classic_canvas():
                    try:
                        func(dt)
                    except Exception as e:
                        # the best we can do there is catch the error and print it to the error stream
                        print(f"Error in requestAnimationFrame callback: {e}", file=sys.stderr)
                        pyjs.cancel_main_loop()
            pyjs.set_main_loop_callback(wrapped_func, fps)

        # return a lambda which can be used to cancel the loop
        return lambda: pyjs.cancel_main_loop()
else:
    import asyncio
    async def _call_repeated(func, fps):
        try:

            interval = 1 / fps
            last_start_time = time.time()

            while True:
                start_time = time.time()
                dt = start_time - last_start_time
                last_start_time = start_time
                try:
                    func(dt)
                except Exception as e:
                    print(f"Error in repeated function call: {e}", file=sys.stderr)
                    break


                elapsed_time = time.time() - start_time
                sleep_time = max(0, interval - elapsed_time)
                await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            # If the task is cancelled, we just exit the loop
            pass
                
    
    def call_repeated(func, fps):
        """Call a function repeatedly at a given frame rate.
        Since we map an fps to requestAnimationFrame, for the 
        emscripten/lite environment, we use 60hz as default when fps is 0.

        Args:
            func: The function to call repeatedly.
            fps: The frame rate to call the function at. If 0, requestAnimationFrame
        """
        if fps == 0:
            # this is a special case, because for lite 
            # this mean "use requestAnimationFrame"
            # so here we just assume this means 60hz
            fps = 60

        loop = asyncio.get_event_loop()
        task = loop.create_task(_call_repeated(func, fps))

        # Return a lambda that can be used to cancel the loop
        return lambda: task.cancel()
        
    def set_render_loop(canvas, func, fps=0):
        """Set a render loop for the canvas.
        This is used to call the function repeatedly at a given frame rate.
        We use the hold_canvas context manager so we only send one message to the frontend per frame.

        Args:
            canvas: The canvas to set the render loop for.
            func: The function to call repeatedly.
            fps: The frame rate to call the function at. If 0, requestAnimationFrame
        """
        def wrapped_func(dt):
            with hold_classic_canvas():
                func(dt)
        return call_repeated(wrapped_func, fps)