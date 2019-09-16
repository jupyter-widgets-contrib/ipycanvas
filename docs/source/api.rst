API Reference
=============

Note that because we are exposing the Web Canvas API, you can find more tutorials and documentation following this link: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

There are some API differences though:

- The Canvas widget is directly exposing the `CanvasRenderingContext2D <https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D>`_ API
- All the API is written in *snake_case* instead of *camelCase*, so for example ``canvas.fillStyle = 'red'`` in JavaScript becomes ``canvas.fill_style = 'red'`` in Python
- The Canvas widget exposes a ``clear`` method, ``canvas.clear()`` is a shortcut for ``canvas.clear_rect(0, 0, canvas.size[0], canvas.size[1])``
- We provide a `hold_canvas` context manager if you want to perform lots of commands at once
- The Web canvas putImageData method does not support transparency and the current transformation state, our ``Canvas.put_image_data`` does support them!


.. automodule:: ipycanvas.canvas
   :members:
