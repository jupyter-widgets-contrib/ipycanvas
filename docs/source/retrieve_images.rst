Retrieve Canvas image
=====================

There are two methods for retrieving the canvas image:

- ``to_file(filename)``: Dumps the image data to a PNG file.
- ``get_image_data(x=0, y=0, width=None, height=None)``: Get the image data as a NumPy array for a sub-portion of the Canvas.

By default, and in order to keep ipycanvas fast, the image state of the Canvas is not synchronized between the TypeScript front-end and the Python back-end. If you want to retrieve the image data from the Canvas, you first need to explicitly specify that you want the image to be synchronized by setting ``sync_image_data`` to ``True`` before doing any drawing, you can set ``sync_image_data`` back to ``False`` once you're done.

Save Canvas to a file
---------------------

You can dump the current ``Canvas`` or ``MultiCanvas`` image to a PNG file using the ``to_file`` method.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200, sync_image_data=True)

    # Perform some drawings...

    canvas.to_file('my_file.png')

Note that this won't work if executed in the same Notebook cell. Because the Canvas won't have drawn anything yet. If you want to put all your code in the same Notebook cell, you need to define a callback function that will be called when the Canvas is ready to be dumped to an image file.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200, sync_image_data=True)

    # Perform some drawings...

    def save_to_file(*args, **kwargs):
        canvas.to_file('my_file.png')

    # Listen to changes on the ``image_data`` trait and call ``save_to_file`` when it changes.
    canvas.observe(save_to_file, 'image_data')

Get image data as a NumPy array
-------------------------------

You can get the image data of the ``Canvas`` or ``MultiCanvas`` using the ``get_image_data`` method.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200, sync_image_data=True)

    # Perform some drawings...

    arr1 = canvas.get_image_data()                # Get the entire Canvas as a NumPy array
    arr2 = canvas.get_image_data(50, 10, 40, 60)  # Get the subpart defined by the rectangle at position (x=50, y=10) and of size (width=40, height=60)

Note that this won't work if executed in the same Notebook cell. Because the Canvas won't have drawn anything yet. If you want to put all your code in the same Notebook cell, you need to define a callback function that will be called when the Canvas has image data.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200, sync_image_data=True)

    # Perform some drawings...

    def get_array(*args, **kwargs):
        arr = canvas.get_image_data()
        # Do something with arr

    # Listen to changes on the ``image_data`` trait and call ``get_array`` when it changes.
    canvas.observe(get_array, 'image_data')
