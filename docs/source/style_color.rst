Styles and colors
=================

Colors
------

The ``Canvas`` has two color parameters, one for the strokes, and one for the surfaces.
You can also change the global transparency.

- ``stroke_style``: (valid HTML color) The color for rectangles and paths stroke. Default to 'black'.
- ``fill_style``: (valid HTML color) The color for filling rectangles and paths. Default to 'black'.
- ``global_alpha``: (float) Transparency level. Default to 1.0.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(200, 200))

    canvas.fill_style = 'red'
    canvas.stroke_style = 'blue'

    canvas.fill_rect(25, 25, 100, 100)
    canvas.clear_rect(45, 45, 60, 60)
    canvas.stroke_rect(50, 50, 50, 50)

    canvas

.. image:: images/colored_rect.png

Lines styles
------------

- ``line_width``: (float) Sets the width of lines drawn in the future, must be a positive number. Default to 1.0.
- ``line_cap``: (str) Sets the appearance of the ends of lines, possible values are 'butt', 'round' and 'square'. Default to 'butt'.
- ``line_join``: (str) Sets the appearance of the “corners” where lines meet, possible values are 'round', 'bevel' and 'miter'. Default to 'miter'
- ``miter_limit``: (float) Establishes a limit on the miter when two lines join at a sharp angle, to let you control how thick the junction becomes. Default to 10..
- ``get_line_dash()``: Return the current line dash pattern array containing an even number of non-negative numbers.
- ``set_line_dash(segments)``: Set the current line dash pattern.
- ``line_dash_offset``: (float) Specifies where to start a dash array on a line. Default is 0..

Line width
``````````

Sets the width of lines drawn in the future.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(400, 280))
    canvas.scale(2)

    for i in range(10):
        width = 1 + i
        x = 5 + i * 20
        canvas.line_width = width

        canvas.fill_text(str(width), x - 5, 15)

        canvas.begin_path()
        canvas.move_to(x, 20)
        canvas.line_to(x, 140)
        canvas.stroke()
    canvas

.. image:: images/line_width.png

Line cap
````````

Sets the appearance of the ends of lines.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(320, 360))

    # Possible line_cap values
    line_caps = ['butt', 'round', 'square']

    canvas.scale(2)

    # Draw guides
    canvas.stroke_style = '#09f'
    canvas.begin_path()
    canvas.move_to(10, 30)
    canvas.line_to(140, 30)
    canvas.move_to(10, 140)
    canvas.line_to(140, 140)
    canvas.stroke()

    # Draw lines
    canvas.stroke_style = 'black'
    canvas.font = '15px serif'

    for i in range(len(line_caps)):
        line_cap = line_caps[i]
        x = 25 + i * 50

        canvas.fill_text(line_cap, x - 15, 15)
        canvas.line_width = 15
        canvas.line_cap = line_cap
        canvas.begin_path()
        canvas.move_to(x, 30)
        canvas.line_to(x, 140)
        canvas.stroke()

    canvas

.. image:: images/line_cap.png

Line join
`````````

Sets the appearance of the "corners" where lines meet.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(320, 360))

    # Possible line_join values
    line_joins = ['round', 'bevel', 'miter']

    min_y = 40
    max_y = 80
    spacing = 45

    canvas.line_width = 10
    canvas.scale(2)
    for i in range(len(line_joins)):
        line_join = line_joins[i]

        y1 = min_y + i * spacing
        y2 = max_y + i * spacing

        canvas.line_join = line_join

        canvas.fill_text(line_join, 60, y1 - 10)

        canvas.begin_path()
        canvas.move_to(-5, y1)
        canvas.line_to(35, y2)
        canvas.line_to(75, y1)
        canvas.line_to(115, y2)
        canvas.line_to(155, y1)
        canvas.stroke()

    canvas

.. image:: images/line_join.png

Line dash
`````````

Sets the current line dash pattern.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(size=(400, 280))
    canvas.scale(2)

    line_dashes = [
        [5, 10],
        [10, 5],
        [5, 10, 20],
        [10, 20],
        [20, 10],
        [20, 20]
    ]

    canvas.line_width = 2

    for i in range(len(line_dashes)):
        x = 5 + i * 20

        canvas.set_line_dash(line_dashes[i])
        canvas.begin_path()
        canvas.move_to(x, 0)
        canvas.line_to(x, 140)
        canvas.stroke()
    canvas

.. image:: images/line_dash.png
