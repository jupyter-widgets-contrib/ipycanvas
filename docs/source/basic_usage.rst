Basic usage
===========

Create Canvas
-------------

You can provide the width and height of the ``Canvas`` in pixels in the constructor.

.. code-block:: python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200)
    canvas

You can also create a multi-layer canvas. This is useful when you have a background
that does not need to update much while other objects moves a lot on the screen.

.. code-block:: python

    from ipycanvas import MultiCanvas

    # Create a multi-layer canvas with 4 layers
    multi_canvas = MultiCanvas(4, width=200, height=200)
    multi_canvas[0]  #  Access first layer (background)
    multi_canvas[3]  #  Access last layer (foreground)
    multi_canvas

.. note::
    Because the ``Canvas`` is an interactive widget (see https://ipywidgets.readthedocs.io/en/stable/) you can:

    - display it multiple times in the Notebook
    - observe some of its attributes and call functions when they change
    - link some of its attributes to other widget attributes

Resize Canvas
-------------

The ``Canvas`` and ``MultiCanvas`` have two sizes: the size of the color buffer in pixels, and the actual size
displayed on the screen.

Color buffer size
^^^^^^^^^^^^^^^^^

The color buffer size can dynamically be updated through the ``width`` and ``height`` properties (value in pixels), note that this will clear the canvas.

.. code-block:: python

    canvas.width = 300
    canvas.height = 600

Screen size
^^^^^^^^^^^

The size on the screen can be updated through the ``layout`` property, which comes from ipywidgets (see https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Styling.html#The-layout-attribute). The ``layout`` property is an object which contains CSS properties for the canvas.

The default value for the ``width`` and ``height`` of the layout is "auto", this means the canvas will take the same screen size as the actual color buffer size: a ``Canvas`` of
size ``800x600`` will take ``800x600`` pixels on the screen.

.. code-block:: python

    canvas.layout.width = "auto"
    canvas.layout.height = "auto"

In order to get a "responsive" ``Canvas`` which takes as much space as available while still respecting the aspect ratio, you will need to set the ``width``
property to ``100%``, the ``height`` will automatically get computed:

.. code-block:: python

    canvas.layout.width = "100%"
    canvas.layout.height = "auto"

One can also set the screen size value in pixels:

.. code-block:: python

    canvas.layout.width = "200px"
    canvas.layout.height = "500px"

Clear Canvas
------------

The ``Canvas`` and ``MultiCanvas`` classes have a ``clear`` method which allows to clear the entire canvas.

.. code-block:: python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200)

    # Perform some drawings...

    canvas.clear()

Optimizing drawings
-------------------

By default, the Python ``Canvas`` object sends all the drawings commands like ``fill_rect``
and ``arc`` one by one through the widgets communication layer. This communication is limited
to 1000 commands/s and it can be extremely slow to send commands one after the other.
You can increase this limit via internal Jupyter `parameters <https://github.com/martinRenou/ipycanvas/issues/102>`_,
however this is not recommended as it can lead to instability. Instead we provide a ``hold_canvas``
context manager which allows you to hold all the commands and send them in a single batch at the end. For
optimal performance you should try to use ``hold_canvas`` as much as possible.

.. code-block:: python

    from ipycanvas import Canvas, hold_canvas

    canvas = Canvas(width=200, height=200)

    with hold_canvas():
        # Perform drawings...
        pass
