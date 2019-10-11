Drawing shapes
==============

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

There are three methods that draw rectangles on the canvas:

- ``fill_rect(x, y, width, height)``: Draws a filled rectangle.
- ``stroke_rect(x, y, width, height)``: Draws a rectangular outline.
- ``clear_rect(x, y, width, height)``: Clears the specified rectangular area, making it fully transparent.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))

    canvas.fill_rect(25, 25, 100, 100)
    canvas.clear_rect(45, 45, 60, 60)
    canvas.stroke_rect(50, 50, 50, 50)

    canvas

.. image:: images/rect.png

Drawing paths
-------------

A path is a list of points, connected by segments of lines that can be of different shapes, curved or not,
of different width and of different color. A path can be closed. To make shapes using paths, we take some
extra steps:

- First, you create the path with ``begin_path``
- Then you use drawing commands to draw into the path
- Once the path has been created, you can ``stroke`` or ``fill`` the path to render it

Here are the functions used to perform these steps:

- ``begin_path()``: Creates a new path. Once created, future drawing commands are directed into the path and used to build the path up.
- Draw commands like ``line_to`` and ``arc``
- ``close_path()``: Adds a straight line to the path, going to the start of the current path.
- ``stroke()``: Draws the shape by stroking its outline.
- ``fill()``: Draws a solid shape by filling the path's content area.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(100, 100))

    # Draw simple triangle shape
    canvas.begin_path()
    canvas.move_to(75, 50)
    canvas.line_to(100, 75)
    canvas.line_to(100, 25)
    canvas.fill()

    canvas

.. image:: images/triangle.png


Draw commands
`````````````

Here are the available draw commands:

- ``move_to(x, y)``: Moves the pen to the coordinates specified by x and y. This does not actually draw anything.
- ``line_to(x, y)``: Add a straight line to the current path by connecting the path’s last point to the specified (x, y) coordinates.
- ``arc(x, y, radius, start_angle, end_angle, anticlockwise=False)``: Create a circular arc centered at (x, y) with a radius
  of ``radius``. The path starts at ``start_angle`` and ends at ``end_angle`` in radians, and travels in the direction given by
  ``anticlockwise`` (defaulting to clockwise: False).
- ``arc_to(x1, y1, x2, y2, radius)``: Add a circular arc to the current path. Using the given control points (``x1``, ``y1``)
  and (``x2``, ``y2``) and the ``radius``.
- ``quadratic_curve_to(cp1x, cp1y, x, y)``: Add a quadratic Bezier curve to the current path.
  It requires two points: the first one is a control point and the second one is the end point. The starting point is the latest point in the current path, which can be changed using ``move_to()`` before creating the quadratic Bezier curve.
- ``bezier_curve_to(cp1x, cp1y, cp2x, cp2y, x, y)``: Add a cubic Bezier curve to the current path.
  It requires three points: the first two are control points and the third one is the end point. The starting point is the latest point in the current path, which can be changed using ``move_to()`` before creating the Bezier curve.
- ``rect(x, y, width, height)``: Draws a rectangle whose top-left corner is specified by (``x``, ``y``) with the specified ``width`` and ``height``.


Examples
````````

.. code:: Python

    from math import pi

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))

    # Draw smiley face
    canvas.begin_path()
    canvas.arc(75, 75, 50, 0, pi * 2, True) # Outer circle
    canvas.move_to(110, 75)
    canvas.arc(75, 75, 35, 0, pi, False) # Mouth (clockwise)
    canvas.move_to(65, 65)
    canvas.arc(60, 65, 5, 0, pi * 2, True) # Left eye
    canvas.move_to(95, 65)
    canvas.arc(90, 65, 5, 0, pi * 2, True) # Right eye
    canvas.stroke()

    canvas

.. image:: images/smiley.png

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))

    # Cubic curves example
    canvas.begin_path()
    canvas.move_to(75, 40)
    canvas.bezier_curve_to(75, 37, 70, 25, 50, 25)
    canvas.bezier_curve_to(20, 25, 20, 62.5, 20, 62.5)
    canvas.bezier_curve_to(20, 80, 40, 102, 75, 120)
    canvas.bezier_curve_to(110, 102, 130, 80, 130, 62.5)
    canvas.bezier_curve_to(130, 62.5, 130, 25, 100, 25)
    canvas.bezier_curve_to(85, 25, 75, 37, 75, 40)
    canvas.fill()

    canvas

.. image:: images/heart.png
