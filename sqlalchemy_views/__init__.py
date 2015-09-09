# -*- coding: utf-8 -*-
"""Adds CreateView and related functionality to SQLAlchemy"""

from sqlalchemy_views import metadata
from sqlalchemy_views.views import CreateView, DropView  # noqa

__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright
