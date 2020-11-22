Animations
==========

Animation loop
--------------

The "slow" approach
+++++++++++++++++++

You can make an animation loop using a simple ``for-loop`` in Python and using the ``sleep`` function from the standard ``time`` module.
It is essential that you use the ``hold_canvas`` context manager in order to improve the performances of your animation.

A simple animation loop will look like the following:

.. code:: Python

    from time import sleep

    from ipycanvas import Canvas, hold_canvas

    canvas = Canvas()
    display(canvas)

    # Number of steps in your animation
    steps_number = 200

    for i in range(steps_number):
        with hold_canvas(canvas):
            # Clear the old animation step
            canvas.clear()

            # Perfom all your drawings here
            # ...
            # ...

        # Animation frequency ~50Hz = 1./50. seconds
        sleep(0.02)


You can also make an infinite animation using a ``while`` loop:

.. code:: Python

    from time import sleep

    from ipycanvas import Canvas, hold_canvas

    canvas = Canvas()
    display(canvas)

    while(True):
        with hold_canvas(canvas):
            # Clear the old animation step
            canvas.clear()

            # Perfom all your drawings here
            # ...
            # ...

        # Animation frequency ~50Hz = 1./50. seconds
        sleep(0.02)


Making an animation with ``from time import sleep`` should be fast enough in most cases.
If you draw lots of shapes in your animation loop, you can decrease the animation frequency by sleeping a bit longer: *e.g.* ``sleep(0.033)`` for a ~30Hz animation.
You should also make use of the vectorized versions of the methods ``fill_rect``, ``fill_circle`` etc if you use them a lot, see :ref:`drawing_shapes`.

This approach might be slow if there is latency between the server and the Jupyter client, and if the server and the client are not the same machine (on MyBinder for example).
In that case, the next approach is preferable.


The "fast" approach
+++++++++++++++++++

Because it's more complicated, this approach is only recommended if the "slow" approach is not fast enough in your case, or if the server is not on the same machine as the client.

Unlike the slow approach, we will use the ``sleep`` method of your canvas instead of using the ``time`` module.
The ``sleep`` method will ask your canvas to sleep for a certain amount of time, unlike the ``time`` module, the canvas's ``sleep`` method takes a duration in millisecond.

Using this approach, it is recommended to wrap the entire animation in the ``hold_canvas`` context. This way, you will send the entire animation as a single message
to the Jupyter client, and the animation will run entirely without any communication with the server.

.. code:: Python

    from time import sleep

    from ipycanvas import Canvas, hold_canvas

    canvas = Canvas()
    display(canvas)

    # Number of steps in your animation
    steps_number = 200

    # Note how `hold_canvas` now wraps the entire for-loop
    with hold_canvas(canvas):
        for i in range(steps_number):
            # Clear the old animation step
            canvas.clear()

            # Perfom all your drawings here
            # ...
            # ...

            # Animation frequency ~50Hz = 1000./50. milliseconds
            canvas.sleep(20)


You cannot make an infinite animation using this approach.