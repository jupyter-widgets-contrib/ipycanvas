Interactions
============

Using built-in events
---------------------

There are currently two built-in mouse events: ``click`` and ``mouse_move``.

.. code:: Python

    def handle_mouse_move(x, y):
        # Do something
        pass

    canvas.on_mouse_move(handle_mouse_move)

    def handle_click(x, y):
        # Do something else
        pass

    canvas.on_click(handle_click)

.. note::
    Please open an issue or a Pull Request if you want more events to be supported by ipycanvas

Using ipyevents
---------------

If built-in events are not enough for your use case, you can use `ipyevents <https://github.com/mwcraig/ipyevents>`_ which provides mouse and keyboard events.

GamePad support
---------------

If you have a GamePad, you can use the game `Controller <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html#Controller>`_ widget from ipywidgets to get events from it.
