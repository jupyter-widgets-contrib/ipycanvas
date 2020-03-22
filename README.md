<p align="center"><img width="300" src="docs/source/images/ipycanvas_logo.svg"></p>
<h1 align="center">ipycanvas</h1>
<h2 align="center"> Interactive Canvas in Jupyter </h1>

[![Documentation](http://readthedocs.org/projects/ipycanvas/badge/?version=latest)](https://ipycanvas.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/martinRenou/ipycanvas/stable?filepath=examples)
[![Build Status](https://travis-ci.org/martinRenou/ipycanvas.svg?branch=master)](https://travis-ci.org/martinRenou/ipycanvas)
[![Downloads](https://pepy.tech/badge/ipycanvas)](https://pepy.tech/project/ipycanvas)

ipycanvas is a lightweight, fast and stable library exposing the [browser's Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) to IPython.
It allows you to draw simple primitives directly from Python like text, lines, polygons, arcs, images etc. This simple toolset allows you to draw literally anything!

## Try it online!

You can try it online by clicking on this badge:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/martinRenou/ipycanvas/stable?filepath=examples)

## Documentation

You can read the documentation following this link: https://ipycanvas.readthedocs.io

## Installation

You can install using `pip`:

```bash
pip install ipycanvas
```

Or using `conda`:

```bash
conda install -c conda-forge ipycanvas
```

And if you use jupyterlab:

```bash
conda install -c conda-forge nodejs
jupyter labextension install @jupyter-widgets/jupyterlab-manager ipycanvas
```

 An development installation guide, can be found [here](https://ipycanvas.readthedocs.io/en/latest/installation.html#development-installation)

## Examples

### Create John Conway's Game Of Life
![John Conway's Game Of Life](docs/source/images/ipycanvas_gameoflife.png)

### Draw Particles from IPython
![Particles](docs/source/images/ipycanvas_particles.png)

### Custom Sprites
![Sprites](docs/source/images/ipycanvas_sprites.png)

### Draw data directly from a NumPy array
![NumPy](docs/source/images/ipycanvas_binary.png)

### Create your own plotting library **fully** in Python
![Plotting](docs/source/images/ipycanvas_scatter.png)
