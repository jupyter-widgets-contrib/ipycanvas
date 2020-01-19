Advanced usage
==============

ipycanvas in Voilà
------------------

The ``Canvas`` is a stateless widget, in that the actual state of the ``Canvas`` (pixel colors, transformation state, etc) is not saved nor synchronized between the Python kernel and the client page. This means that whenever a new client connects to the kernel, it will get a blank canvas and you would need to replay all your drawings.

This is an ipycanvas limitation, but it's also a way to keep it fast (not having to synchronize everything).

This limitation results in ipycanvas not working with `Voilà <https://github.com/voila-dashboards/voila>`_ out of the box. Because the Voilà page connects to the kernel only when the entire Notebook has been executed, all the drawings may already have happened and the canvas end up being blank when it's created.

A way to work around this is to perform your drawings in a callback that gets called when the client is ready to receive drawings, using the ``on_client_ready`` method:

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=100, height=50)

    def perform_drawings():
        canvas.font = '32px serif'
        canvas.fill_text('Voilà!', 10, 32)

    canvas.on_client_ready(perform_drawings)

    canvas
