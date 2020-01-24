# -*- coding: utf-8 -*-
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']

master_doc = 'index'
source_suffix = '.rst'

# General information about the project.
project = 'ipycanvas'
author = 'Martin Renou'

exclude_patterns = []
highlight_language = 'python'
pygments_style = 'sphinx'

# Output file base name for HTML help builder.
html_logo = "./images/ipycanvas_logo.svg"
html_favicon = "./images/ipycanvas_logo.ico"
html_theme = "pandas_sphinx_theme"
htmlhelp_basename = 'ipycanvasdoc'

html_theme_options = dict(
    github_url='https://github.com/martinRenou/ipycanvas'
)

html_js_files = [
    'goatcounter.js'
]

html_css_files = [
    'custom.css'
]

autodoc_member_order = 'bysource'
