.. _drawing_shapes:

Drawing simple shapes
=====================

.. note::
    Note that because we are exposing the Web Canvas API, you can find more tutorials and documentation following this link: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

    There are some API differences though:

    - The Canvas widget is directly exposing the `CanvasRenderingContext2D <https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D>`_ API
    - All the API is written in *snake_case* instead of *camelCase*, so for example ``canvas.fillStyle = 'red'`` in JavaScript becomes ``canvas.fill_style = 'red'`` in Python

Before we can start drawing, we need to talk about the canvas grid. The origin of this grid is positioned in the
top left corner at coordinate (0,0). All elements are placed relative to this origin. So the position of the top
left corner of the blue square becomes x pixels from the left and y pixels from the top, at coordinate (x,y).

.. image:: images/grid.png

Drawing rectangles
------------------

There are four methods that draw rectangles on the canvas:

- ``fill_rect(x, y, width, height=None)``: Draws a filled rectangle. If ``height`` is None, it is set to the same value as ``width``.
- ``stroke_rect(x, y, width, height=None)``: Draws a rectangular outline. If ``height`` is None, it is set to the same value as ``width``.
- ``fill_rects(x, y, width, height=None)``: Draws filled rectangles. Where ``x``, ``y``, ``width`` and ``height`` are either integers, lists of integers or NumPy arrays. If ``height`` is None, it is set to the same value as ``width``.
- ``stroke_rects(x, y, width, height=None)``: Draws rectangular outlines. Where ``x``, ``y``, ``width`` and ``height`` are either integers, lists of integers or NumPy arrays. If ``height`` is None, it is set to the same value as ``width``.

You can also clear a certain canvas rectangle area:

- ``clear_rect(x, y, width, height=None)``: Clears the specified rectangular area, making it fully transparent. If ``height`` is None, it is set to the same value as ``width``.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200)

    canvas.fill_rect(25, 25, 100, 100)
    canvas.clear_rect(45, 45, 60, 60)
    canvas.stroke_rect(50, 50, 50, 50)

    canvas

.. image:: images/rect.png

``fill_rects`` and ``stroke_rects`` are blazingly fast ways of drawing up to a million rectangles at once:

.. code:: Python

    import numpy as np

    from ipycanvas import Canvas

    n_particles = 100_000

    x = np.array(np.random.rayleigh(250, n_particles), dtype=np.int32)
    y = np.array(np.random.rayleigh(250, n_particles), dtype=np.int32)
    size = np.random.randint(1, 3, n_particles)

    canvas = Canvas(width=800, height=500)

    canvas.fill_style = 'green'
    canvas.fill_rects(x, y, size)

    canvas

.. image:: images/rects.png

Drawing arcs and circles
------------------------

There are methods that draw arcs/circles on the canvas:

- ``fill_arc(x, y, radius, start_angle, end_angle, anticlockwise=False)``: Draw a filled arc centered at ``(x, y)`` with a radius of ``radius``.
- ``stroke_arc(x, y, radius, start_angle, end_angle, anticlockwise=False)``: Draw an arc outline centered at ``(x, y)`` with a radius of ``radius``.
- ``fill_arcs(x, y, radius, start_angle, end_angle, anticlockwise=False)``: Draw filled arcs centered at ``(x, y)`` with a radius of ``radius``. Where ``x``, ``y``, ``radius`` and other arguments are NumPy arrays, lists or scalar values.
- ``stroke_arcs(x, y, radius, start_angle, end_angle, anticlockwise=False)``: Draw an arc outlines centered at ``(x, y)`` with a radius of ``radius``. Where ``x``, ``y``, ``radius`` and other arguments are NumPy arrays, lists or scalar values.

- ``fill_circle(x, y, radius)``: Draw a filled circle centered at ``(x, y)`` with a radius of ``radius``.
- ``stroke_circle(x, y, radius)``: Draw an circle outline centered at ``(x, y)`` with a radius of ``radius``.
- ``fill_circles(x, y, radius)``: Draw filled circles centered at ``(x, y)`` with a radius of ``radius``. Where ``x``, ``y``, ``radius`` are NumPy arrays, lists or scalar values.
- ``stroke_circles(x, y, radius)``: Draw a circle outlines centered at ``(x, y)`` with a radius of ``radius``. Where ``x``, ``y``, ``radius`` are NumPy arrays, lists or scalar values.


.. code:: Python

    from math import pi

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200)

    canvas.fill_style = 'red'
    canvas.stroke_style = 'blue'

    canvas.fill_arc(60, 60, 50, 0, pi)
    canvas.stroke_circle(60, 60, 40)

    canvas

.. image:: images/arc.png

Drawing lines
-------------

There is one command for drawing a straight line from one point to another:

- ``stroke_line(x1, y1, x2, y2)``: Draw a line from ``(x1, y1)`` to ``(x2, y2)``.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=200, height=200)

    canvas.stroke_style = 'blue'
    canvas.stroke_line(0, 0, 150, 150)

    canvas.stroke_style = 'red'
    canvas.stroke_line(200, 0, 0, 200)

    canvas.stroke_style = 'green'
    canvas.stroke_line(150, 150, 0, 200)

    canvas

.. image:: images/lines.png


Vectorized methods
------------------

Some methods like ``fill_rect`` and ``fill_circle`` have a vectorized counterpart: ``fill_rects`` and ``fill_cicles``. It is essential
to use those methods when you want to draw the same shape multiple times with the same style.

For example, it is way faster to run:

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=300, height=300)

    canvas.global_alpha = 0.01

    size = [i for i in range(300)]
    position = [300 - i for i in range(300)]

    canvas.fill_rects(position, position, size)

    canvas

instead of running:

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=300, height=300)

    canvas.global_alpha = 0.01

    for i in range(300):
        size = i
        position = 300 - i

        canvas.fill_rect(position, position, size)

    canvas