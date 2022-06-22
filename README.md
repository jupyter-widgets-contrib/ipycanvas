<p align="center"><img width="300" src="docs/images/ipycanvas_logo.svg"></p>
<h1 align="center">ipycanvas</h1>
<h2 align="center"> Interactive Canvas in Jupyter </h1>

[![Documentation](http://readthedocs.org/projects/ipycanvas/badge/?version=latest)](https://ipycanvas.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/martinRenou/ipycanvas/stable?urlpath=lab%2Ftree%2Fexamples)
[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge-launch.svg)](https://ipycanvas.readthedocs.io/en/latest/lite/lab)
[![Downloads](https://pepy.tech/badge/ipycanvas)](https://pepy.tech/project/ipycanvas)
[![Join the chat at https://gitter.im/martinRenou/ipycanvas](https://badges.gitter.im/martinRenou/ipycanvas.svg)](https://gitter.im/martinRenou/ipycanvas?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

ipycanvas is a lightweight, fast and stable library exposing the [browser's Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) to IPython.
It allows you to draw simple primitives directly from Python like text, lines, polygons, arcs, images etc. This simple toolset allows you to draw literally anything!

## Try it online!

You can try it online by clicking on this badge:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/martinRenou/ipycanvas/stable?urlpath=lab%2Ftree%2Fexamples)

## Documentation

You can read the documentation following this link: https://ipycanvas.readthedocs.io

## Questions?

If you have any question, or if you want to share what you do with ipycanvas, [start a new discussion on Github](https://github.com/martinRenou/ipycanvas/discussions/new)!

Or join the gitter channel: [![Join the chat at https://gitter.im/martinRenou/ipycanvas](https://badges.gitter.im/martinRenou/ipycanvas.svg)](https://gitter.im/martinRenou/ipycanvas?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Installation

You can install using `pip`:

```bash
pip install ipycanvas orjson
```

Or using `conda`:

```bash
conda install -c conda-forge ipycanvas
```

And if you use jupyterlab <= 2:

```bash
conda install -c conda-forge yarn
jupyter labextension install @jupyter-widgets/jupyterlab-manager ipycanvas
```

A development installation guide, can be found [here](https://ipycanvas.readthedocs.io/en/latest/installation.html#development-installation)

## Examples

### Create John Conway's Game Of Life

![John Conway's Game Of Life](docs/images/ipycanvas_gameoflife.png)

### Give a "hand-drawn" style to your drawings using the RoughCanvas

![RoughCanvas](docs/images/ipycanvas_rough.png)

### Draw Particles from IPython

![Particles](docs/images/ipycanvas_particles.png)

### Custom Sprites

![Sprites](docs/images/ipycanvas_sprites.png)

### Draw data directly from a NumPy array

![NumPy](docs/images/ipycanvas_binary.png)

### Create your own plotting library **fully** in Python

![Plotting](docs/images/ipycanvas_scatter.png)
