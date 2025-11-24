ipycanvas: Interactive Canvas in Jupyter
========================================

.. image:: images/ipycanvas_logo.svg
  :height: 300px
  :width: 300px
  :align: center

Try it online
-------------

You can try ipycanvas, without the need of installing anything on your computer, using `Notebook.link <https://notebook.link>`_ by clicking on this badge:

.. image:: https://img.shields.io/badge/notebook-link-e2d610?logo=jupyter&logoColor=white
   :target: https://notebook.link/github/jupyter-widgets-contrib/ipycanvas/tree/main/lab/

Or you can run try it here:

.. replite::
   :kernel: xpython
   :height: 600px

    from math import pi

    from ipycanvas import Canvas

    canvas = Canvas(width=1600, height=1200, layout=dict(width="100%"))

    canvas.fill_style = "#8ee05e"
    canvas.fill_rect(0, 0, canvas.width, canvas.height)

    canvas.fill_style = "#f5f533"
    canvas.fill_circle(canvas.width / 2.0, canvas.height / 2.0, 500)

    canvas.stroke_style = "black"
    canvas.line_width = 30
    canvas.stroke_circle(canvas.width / 2.0, canvas.height / 2.0, 500)

    canvas.fill_style = "black"
    canvas.fill_circle(canvas.width / 2.7, canvas.height / 3.0, 100)  # Right eye
    canvas.stroke_arc(canvas.width / 2.0, canvas.height / 2.0, 400, 0, pi, False)  # Mouth
    canvas.stroke_arc(
        canvas.width - canvas.width / 2.7, canvas.height / 2.7, 100, 0, pi, True
    )  # Left eye

    canvas


Questions?
----------

If you have any question, or if you want to share what you do with ipycanvas, come `start a new discussion on Github <https://github.com/jupyter-widgets-contrib/ipycanvas/discussions/new>`_!

Index
-----

.. toctree::
    :caption: Installation
    :maxdepth: 2

    installation

.. toctree::
    :caption: Usage
    :maxdepth: 2

    usage

.. toctree::
    :caption: API Reference

    api
