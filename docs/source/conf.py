# -*- coding: utf-8 -*-
import sphinx_rtd_theme

extensions = [
    'sphinx_rtd_theme',
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
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
htmlhelp_basename = 'ipycanvasdoc'

html_theme_options = dict(
    style_nav_header_background='#0d6a0a'
)

autodoc_member_order = 'bysource'
