Canvas state
============

- ``save()``: Saves the entire state of the canvas.
- ``restore()``: Restores the most recently saved canvas state.

Canvas states are stored on a stack. Every time the ``save()`` method is called, the current drawing state is pushed onto the stack. A drawing state consists of:

- The transformations that have been applied (i.e. translate, rotate and scale – see next section).
- The current values of the following attributes: ``stroke_style``, ``fill_style``, ``global_alpha``, ``line_width``, ``line_cap``, ``line_join``, ``miter_limit``, ``line_dash_offset``, ``global_composite_operation``, ``font``, ``text_align``, ``text_baseline``, ``direction``.

You can call the ``save()`` method as many times as you like. Each time the ``restore()`` method is called, the last saved state is popped off the stack and all saved settings are restored.
