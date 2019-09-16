.. _installation:

Using pip
=========

.. code:: bash

    pip install ipycanvas
    jupyter nbextension enable --py --sys-prefix ipycanvas  # can be skipped for notebook 5.3 and above

Using conda
===========

.. code:: bash

    conda install -c conda-forge ipycanvas

JupyterLab extension
====================

If you have JupyterLab, you will also need to install the JupyterLab extension:

.. code:: bash

    jupyter labextension install @jupyter-widgets/jupyterlab-manager ipycanvas

Development installation
========================

For a development installation (requires npm):

.. code:: bash

    git clone https://github.com/martinRenou/ipycanvas.git
    cd ipycanvas
    pip install -e .
    jupyter nbextension install --py --symlink --sys-prefix ipycanvas
    jupyter nbextension enable --py --sys-prefix ipycanvas
    jupyter labextension install @jupyter-widgets/jupyterlab-manager .  # If you are developing on JupyterLab
