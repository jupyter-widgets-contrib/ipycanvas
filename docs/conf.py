# -*- coding: utf-8 -*-
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "jupyterlite_sphinx"]

jupyterlite_dir = "."
jupyterlite_silence = False

jupyterlite_contents = [
   "*.ipynb",
    "sprites/*.png",
]

master_doc = "index"
source_suffix = ".rst"

# General information about the project.
project = "ipycanvas"
author = "Martin Renou"

exclude_patterns = []
highlight_language = "python"
pygments_style = "sphinx"

# Output file base name for HTML help builder.
html_logo = "./images/ipycanvas_logo.svg"
html_favicon = "./images/ipycanvas_logo.ico"
html_theme = "pydata_sphinx_theme"
htmlhelp_basename = "ipycanvasdoc"

html_theme_options = dict(
    github_url="https://github.com/jupyter-widgets-contrib/ipycanvas"
)

html_static_path = ["_static"]

html_css_files = ["custom.css"]

autodoc_member_order = "bysource"