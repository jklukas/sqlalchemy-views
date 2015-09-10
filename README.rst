View Manipulation for SQLAlchemy
================================

Adds `CreateTable` and `DropView` constructs to SQLAlchemy.

For example:

    >>> from sqlalchemy import Table, MetaData
    >>> from sqlalchemy.sql import text
    >>> from sqlalchemy_views import CreateView
    >>> view = Table('my_view', MetaData())
    >>> definition = text("SELECT * FROM my_table")
    >>> create_view = CreateView(view, definition)
    >>> print(str(create_view.compile()).strip())
    CREATE VIEW my_view AS SELECT * FROM my_table

Note that the SQLAlchemy ``Table`` object is used to represent
both tables and views.


Acknowledgements
----------------

Some design ideas taken from the
`SQLAlchemy Usage Recipe for views <https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views>`_.

Package structure is based on
`python-project-template <https://github.com/seanfisk/python-project-template>`_.
