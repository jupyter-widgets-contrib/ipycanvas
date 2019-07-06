
# ipycanvas

Interactive widgets library exposing the browser's Canvas API

## Installation from sources

You can install using `pip`:

```bash
git clone https://github.com/martinRenou/ipycanvas
cd ipycanvas
pip install .
```

Or if you use jupyterlab:

```bash
git clone https://github.com/martinRenou/ipycanvas
cd ipycanvas
pip install .
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install .
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] ipycanvas
```
