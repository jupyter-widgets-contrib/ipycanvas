
# ipycanvas

[![Build Status](https://travis-ci.org/martinRenou/ipycanvas.svg?branch=master)](https://travis-ci.org/martinRenou/ipycanvas)
[![codecov](https://codecov.io/gh/martinRenou/ipycanvas/branch/master/graph/badge.svg)](https://codecov.io/gh/martinRenou/ipycanvas)


Interactive widgets library exposing the browser's Canvas API

## Installation

You can install using `pip`:

```bash
pip install ipycanvas
```

Or if you use jupyterlab:

```bash
pip install ipycanvas
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] ipycanvas
```
