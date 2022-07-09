Interactions
============

Built-in mouse events
---------------------

The following built-in mouse events are supported: ``mouse_down``, ``mouse_move``, ``mouse_up`` and ``mouse_out``. You can define Python callback functions that will be called whenever those mouse events occur, using the ``on_mouse_down``, ``on_mouse_move``, ``on_mouse_up`` and ``on_mouse_out`` methods.

Those methods take a callback function as single argument, this callback function must take two positional arguments that are the ``x`` and ``y`` pixel coordinates where the mouse was during the event.

.. code-block:: python

    from ipywidgets import Output

    out = Output()


    @out.capture()
    def handle_mouse_move(x, y):
        print("Mouse move event:", x, y)


    canvas.on_mouse_move(handle_mouse_move)


    @out.capture()
    def handle_mouse_down(x, y):
        print("Mouse down event:", x, y)


    canvas.on_mouse_down(handle_mouse_down)

    display(out)

Built-in touch events
---------------------

The following built-in touch events are supported: ``touch_start``, ``touch_end``, ``touch_move`` and ``touch_cancel``. You can define Python callback functions that will be called whenever those touch events occur, using the ``on_touch_start``, ``on_touch_end``, ``on_touch_move`` and ``on_touch_cancel`` methods.

Those methods take a callback function as single argument, this callback function must take one positional argument which is the list of tuples representing the ``(x, y)`` pixel coordinates where the fingers are located on the canvas.

.. code-block:: python

    import math
    out = Output()
    
    @out.capture()
    def handle_touch_move(fingers_locations):
        # Draw circles where fingers are located
        for finger_location in fingers_locations:
            canvas.fill_arc(finger_location[0], finger_location[1], 6, 0, 2 * math.pi)

    canvas.on_touch_move(handle_touch_move)
    display(out)

.. note::
    Please open an issue or a Pull Request if you want more events to be supported by ipycanvas

Keyboard events
---------------

.. code-block:: python

    from ipywidgets import Output

    out = Output()


    @out.capture()
    def on_keyboard_event(key, shift_key, ctrl_key, meta_key):
        print("Keyboard event:", key, shift_key, ctrl_key, meta_key)


    canvas.on_key_down(on_keyboard_event)

    display(out)

ipyevents
---------

If built-in events are not enough for your use case, you can use `ipyevents <https://github.com/mwcraig/ipyevents>`_ which provides mouse and keyboard events.

GamePad support
---------------

If you have a GamePad, you can use the game `Controller <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html#Controller>`_ widget from ipywidgets to get events from it.
