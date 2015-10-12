import sphinx_rtd_theme

# -- General configuration -----------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'bravado'
copyright = u'2013, Digium, Inc.; 2014-2015, Yelp, Inc'

exclude_patterns = []

pygments_style = 'sphinx'


# -- Options for HTML output ---------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']

htmlhelp_basename = 'bravado-pydoc'


intersphinx_mapping = {
    'http://docs.python.org/': None
}
