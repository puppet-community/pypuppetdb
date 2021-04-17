# -*- coding: utf-8 -*-
from datetime import datetime

import pkg_resources
import sys
import os

import sphinx_rtd_theme

pypuppetdb_root = os.path.dirname(os.path.abspath("."))
sys.path.insert(0, pypuppetdb_root)

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

project = "pypuppetdb"
copyright = "2013-%s, Vox Pupuli" % datetime.now().year
version = pkg_resources.get_distribution(project).version
release = version

language = "en"

exclude_patterns = ["_build"]

pygments_style = "sphinx"

# -- Options for HTML output --------------------------------------------------

html_theme = "sphinx_rtd_theme"

html_static_path = []

htmlhelp_basename = "pypuppetdbdoc"

# -- Options for LaTeX output -------------------------------------------------

latex_documents = [
    (
        "index",
        "pypuppetdb.tex",
        u"pypuppetdb Documentation",
        u"Vox Pupuli",
        "manual",
    ),
]


# -- Options for manual page output -------------------------------------------

man_pages = [
    (
        "index",
        "pypuppetdb",
        u"pypuppetdb Documentation",
        [u"Daniele Sluijters"],
        1,
    )
]

# -- Options for Texinfo output -----------------------------------------------

texinfo_documents = [
    (
        "index",
        "pypuppetdb",
        u"pypuppetdb Documentation",
        u"Daniele Sluijters",
        "pypuppetdb",
        "Library to work with the PuppetDB REST API.",
        "Miscellaneous",
    ),
]
