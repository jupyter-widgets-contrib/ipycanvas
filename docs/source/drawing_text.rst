Drawing text
============

There are two methods that draw text on the canvas:

- ``fill_text(text, x, y, max_width=None)``: Fills a given ``text`` at the given (``x``, ``y``) position. Optionally with a maximum width to draw.
- ``stroke_text(text, x, y, max_width=None)``: Strokes a given ``text`` at the given (``x``, ``y``) position. Optionally with a maximum width to draw.

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=400, height=50)

    canvas.font = '32px serif'
    canvas.fill_text('Drawing from Python is cool!', 10, 32)
    canvas

.. image:: images/fill_text.png

.. code:: Python

    from ipycanvas import Canvas

    canvas = Canvas(width=400, height=50)

    canvas.font = '32px serif'
    canvas.stroke_text('Hello There!', 10, 32)
    canvas

.. image:: images/stroke_text.png

Styles and colors
-----------------

You can change the text style by changing the following ``Canvas`` attributes:

- ``font``: (str) The current text style being used when drawing text. This string uses the same syntax as the CSS font property. The default font is ``"12px sans-serif"``.
- ``text_align``: (str) Text alignment setting. Possible values: ``"start"``, ``"end"``, ``"left"``, ``"right"`` or ``"center"``. The default value is ``"start"``.
- ``text_baseline``: (str) Baseline alignment setting. Possible values: ``"top"``, ``"hanging"``, ``"middle"``, ``"alphabetic"``, ``"ideographic"``, ``"bottom"``. The default value is ``"alphabetic"``.
- ``direction``: (str) Directionality. Possible values: ``"ltr"``, ``"rtl"``, ``"inherit"``. The default value is ``"inherit"``.

.. note::
    You can still use ``fill_style``, ``stroke_style``, ``shadow_color`` etc for coloring text and applying shadows.
