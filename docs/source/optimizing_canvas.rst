Optimizing drawings
===================

By default, the Python ``Canvas`` object sends all the drawings commands like ``fill_rect``
and ``arc`` one by one through the widgets communication layer. This communication is
limited to 1000 commands/s if you did not change internal Jupyter parameters, and it can
be extremely slow to send commands one after the other.

We provide a ``hold_canvas`` context manager which allows you to hold all the commands and
send them in a single batch at the end.

``hold_canvas`` must be used without moderation.

.. code:: Python

    from ipycanvas import Canvas, hold_canvas

    canvas = Canvas(size=(200, 200))

    with hold_canvas(canvas):
        # Perform drawings...
