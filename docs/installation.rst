.. _installation:

Installation
============

Using pip
---------

.. code:: bash

    pip install ipycanvas

Using conda
-----------

.. code:: bash

    conda install -c conda-forge ipycanvas

Development installation
------------------------

For a development installation (requires npm and jupyterlab):

.. code:: bash

    git clone https://github.com/jupyter-widgets-contrib/ipycanvas.git
    cd ipycanvas
    pip install -e .

    # Installing the JupyterLab extension
    jupyter labextension develop . --overwrite
    jlpm run build

If you use JupyterLab to develop then you can watch the source directory and run JupyterLab at the same time in different
terminals to watch for changes in the extension's source and automatically rebuild the extension.

.. code:: bash

    # Watch the source directory in one terminal, automatically rebuilding when needed
    jlpm run watch
    # Run JupyterLab in another terminal
    jupyter lab
