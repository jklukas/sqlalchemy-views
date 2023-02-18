View Manipulation for SQLAlchemy
================================

Adds ``CreateView`` and ``DropView`` constructs to SQLAlchemy.

Status
------

Current version is 0.3.2; releases are infrequent as the code here is small and based on stable pieces of the SQLAlchemy API, so there has been minimal maintenance required so far to keep compatibility with new SQLAlchemy or python versions.

This package is working with latest Python and SQLAlchemy (1.0+ and 2.0) as of early 2023.

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

    >>> create_view = CreateView(view, definition, options={'check_option': 'local'})
    >>> print(str(create_view.compile()).strip())
    CREATE VIEW my_view WITH (check_option=local) AS SELECT * FROM my_table

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

    pip install sqlalchemy-views


Limitations
-----------

Various SQL dialects have developed custom
``CREATE VIEW`` and ``DROP VIEW`` syntax.
This project aims to provide the core set of functionality
shared by most database engines.


Acknowledgements
----------------

Some design ideas taken from the
`SQLAlchemy Usage Recipe for views <https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views>`_.

Package structure is based on
`python-project-template <https://github.com/seanfisk/python-project-template>`_.

And thank you to the various
`contributors <https://github.com/jklukas/sqlalchemy-views/graphs/contributors>`_!
