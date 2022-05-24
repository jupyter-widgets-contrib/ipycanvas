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

JupyterLab extension
--------------------

If you have JupyterLab, you will also need to install the JupyterLab extension. In order to install the JupyterLab extension,
you will need ``npm`` to be installed. You can easily install ``npm`` with conda:

.. code:: bash

    conda install -c conda-forge nodejs

Then you can install the JupyterLab extension:

.. code:: bash

    jupyter labextension install @jupyter-widgets/jupyterlab-manager ipycanvas

Development installation
------------------------

For a development installation (requires npm):

.. code:: bash

    git clone https://github.com/martinRenou/ipycanvas.git
    cd ipycanvas
    pip install -e .

    # If you are developing on the classic Jupyter Notebook
    jupyter nbextension install --py --symlink --sys-prefix ipycanvas
    jupyter nbextension enable --py --sys-prefix ipycanvas

    # If you are developing on JupyterLab
    jupyter labextension develop . --overwrite
    jlpm run build

If you use JupyterLab to develop then you can watch the source directory and run JupyterLab at the same time in different
terminals to watch for changes in the extension's source and automatically rebuild the extension.

.. code:: bash

    # Watch the source directory in one terminal, automatically rebuilding when needed
    jlpm run watch
    # Run JupyterLab in another terminal
    jupyter lab
