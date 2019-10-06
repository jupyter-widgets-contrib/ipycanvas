.. _usage:

Create Canvas
=============

You need to provide the size of the ``Canvas`` (width, height) in the constructor.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))
    canvas

You can also create a multi-layer canvas. This is useful when you have a background
that does not need to update much while other objects moves a lot on the screen.

.. code:: Python

    from ipycanvas import MultiCanvas

    # Create a multi-layer canvas with 4 layers
    multi_canvas = MultiCanvas(4, size=(200, 200))
    multi_canvas[0] #  Access first layer (background)
    multi_canvas[3] #  Access last layer
    multi_canvas

Draw shapes
===========


Clear canvas
============

The ``Canvas`` class has a ``clear`` method which allows to clear the entire canvas.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))

    # Perform some drawings...

    canvas.clear()

Optimizing drawings
===================

By default, the Python ``Canvas`` object sends all the drawings commands like ``fill_rect``
and ``arc`` one by one through the widgets communication layer. This communication is
limited to 1000 commands/s if you did not change internal Jupyter parameters, and it can
be extremely slow to send commands one by one.

We provide a ``hold_canvas`` context manager which allows you to hold all the commands and
send them in a single batch at the end.

``hold_canvas`` must be used without moderation.

.. code:: Python

    from ipycanvas import Canvas, hold_canvas

    canvas = Canvas(size=(200, 200))

    with hold_canvas(canvas):
        # Perform drawings...
