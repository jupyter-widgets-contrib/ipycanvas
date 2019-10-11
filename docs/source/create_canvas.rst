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

.. note::
    Because the ``Canvas`` is an interactive widget (see https://ipywidgets.readthedocs.io/en/stable/) you can:

    - display it multiple times in the Notebook
    - observe some of its attributes and call functions when they change
    - link some of its attributes to other widget attributes
