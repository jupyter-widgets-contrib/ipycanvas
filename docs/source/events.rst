Interactions
============

Using built-in events
---------------------

The following built-in mouse events are supported: ``mouse_down``, ``mouse_move``, ``mouse_up`` and ``mouse_out``.

.. code:: Python

    def handle_mouse_move(x, y):
        # Do something
        pass

    canvas.on_mouse_move(handle_mouse_move)

    def handle_mouse_down(x, y):
        # Do something else
        pass

    canvas.on_mouse_down(handle_mouse_down)

.. note::
    Please open an issue or a Pull Request if you want more events to be supported by ipycanvas

Using ipyevents
---------------

If built-in events are not enough for your use case, you can use `ipyevents <https://github.com/mwcraig/ipyevents>`_ which provides mouse and keyboard events.

GamePad support
---------------

If you have a GamePad, you can use the game `Controller <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html#Controller>`_ widget from ipywidgets to get events from it.
