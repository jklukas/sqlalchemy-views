View Manipulation for SQLAlchemy
================================

Adds `CreateTable` and `DropView` constructs to SQLAlchemy.


Usage
-----

Examples:

    >>> from sqlalchemy import Table, MetaData
    >>> from sqlalchemy.sql import text
    >>> from sqlalchemy_views import CreateView, DropView

    >>> view = Table('my_view', MetaData())
    >>> definition = text("SELECT * FROM my_table")
    >>> create_view = CreateView(view, definition)
    >>> print(str(create_view.compile()).strip())
    CREATE VIEW my_view AS SELECT * FROM my_table

    >>> create_view = CreateView(view, definition, or_replace=True)
    >>> print(str(create_view.compile()).strip())
    CREATE OR REPLACE VIEW my_view AS SELECT * FROM my_table

    >>> drop_view = DropView(view)
    >>> print(str(drop_view.compile()).strip())
    DROP VIEW my_view

    >>> drop_view = DropView(view, if_exists=True, cascade=True)
    >>> print(str(drop_view.compile()).strip())
    DROP VIEW IF EXISTS my_view CASCADE

Note that the SQLAlchemy ``Table`` object is used to represent
both tables and views. To introspect a view, create a ``Table``
with ``autoload=True``, and then use SQLAlchemy's
``get_view_definition`` method to generate the second
argument to ``CreateView``.


Installation
------------

``sqlalchemy-views`` is available on PyPI and can be installed via ``pip`` ::

    pip install sqalalchemy-views


Limitations
-----------

Various SQL dialects have developed custom
`CREATE VIEW` and `DROP VIEW` syntax.
This project aims to provide the core set of functionality
shared by most database engines.


Acknowledgements
----------------

Some design ideas taken from the
`SQLAlchemy Usage Recipe for views <https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views>`_.

Package structure is based on
`python-project-template <https://github.com/seanfisk/python-project-template>`_.
