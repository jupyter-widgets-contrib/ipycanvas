import pyjs
import time
import sys

from .canvas import hold_canvas as hold_classic_canvas

if sys.platform.startswith("emscripten"):
    import pyjs
    from .offscreen_canvas.offscreen_canvas_core import OffscreenCanvasCore

    def call_repeated(func, fps=0):
        pyjs.set_main_loop_callback(func, fps)


    def set_render_loop(canvas, func, fps=0):
        if isinstance(canvas, OffscreenCanvasCore):
            def wrapped_func(dt):
                try:
                    func(dt)
                except Exception as e:
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
                        print(f"Error in requestAnimationFrame callback: {e}", file=sys.stderr)
                        pyjs.cancel_main_loop()
            pyjs.set_main_loop_callback(wrapped_func, fps)

        # return a lambda which can be used to cancel the loop
        return lambda: pyjs.cancel_main_loop()
else:
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
        """Call a function repeatedly at a given frame rate."""
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
        def wrapped_func(dt):
            with hold_classic_canvas():
                func(dt)
        return call_repeated(wrapped_func, fps)