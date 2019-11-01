Basic usage
===========

Create Canvas
-------------

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

.. note::
    Because the ``Canvas`` is an interactive widget (see https://ipywidgets.readthedocs.io/en/stable/) you can:

    - display it multiple times in the Notebook
    - observe some of its attributes and call functions when they change
    - link some of its attributes to other widget attributes

Clear Canvas
------------

The ``Canvas`` and ``MultiCanvas`` classes have a ``clear`` method which allows to clear the entire canvas.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))

    # Perform some drawings...

    canvas.clear()

Save Canvas to a file
---------------------

You can dump the current ``Canvas`` or ``MultiCanvas`` image using the ``to_file`` method. You first need to specify that you want the image data to be synchronized between the front-end and the back-end setting the ``sync_image_data`` attribute to ``True``.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200), sync_image_data=True)

    # Perform some drawings...

    canvas.to_file('my_file.png')

Note that this won't work if executed in the same Notebook cell. Because the Canvas won't have drawn anything yet. If you want to put all your code in the same Notebook cell, you need to define a callback function that will be called when the Canvas is ready to be dumped to an image file.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200), sync_image_data=True)

    # Perform some drawings...

    def save_to_file(*args, **kwargs):
        canvas.to_file('my_file.png')

    # Listen to changes on the ``image_data`` trait and call ``save_to_file`` when it changes.
    canvas.observe(save_to_file, 'image_data')

Optimizing drawings
-------------------

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
