# -*- coding: utf-8 -*-
"""The view stuff."""


from sqlalchemy.schema import CreateColumn
from sqlalchemy.sql.ddl import _CreateDropBase
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.engine import Compiled


class CreateView(_CreateDropBase):
    """
    Prepares a CREATE VIEW statement.

    See parameters in :class:`~sqlalchemy.sql.ddl.DDL`.

    Parameters
    ----------
    element: sqlalchemy.Table
        The view to create (sqlalchemy has no View construct)
    selectable: sqalalchemy.Selectable
        A query that evaluates to a table.
        This table defines the columns and rows in the view.
    or_replace: boolean
        If True, this definition will replace an existing definition.
        Otherwise, an exception will be raised if the view exists.
    options: dict
        Specify optional parameters for a view. For Postgresql, it translates
        into 'WITH ( view_option_name [= view_option_value] [, ... ] )'
    """

    __visit_name__ = "create_view"

    def __init__(self, element, selectable, on=None, bind=None,
                 or_replace=False, options=None):
        try:
            super(CreateView, self).__init__(element, on=on, bind=bind)
        except TypeError:
            # Since version 1.4.0 of SQLAlchemy the ** on ** parameter no
            # longer exists. it causes a ** TypeError ** exception
            if on is not None:
                raise TypeError("'on' is not supported on SQLAlchemy 1.4+")

            try:
                super(CreateView, self).__init__(element, bind=bind)
            except TypeError:
                # Since version 2.0.0 of SQLAlchemy the ** bind ** parameter no
                # longer exists. it causes a ** TypeError ** exception
                if on is not None:
                    raise TypeError(
                        "'bind' is not supported on SQLAlchemy 1.4+")

                super(CreateView, self).__init__(element)

        self.columns = [CreateColumn(column) for column in element.columns]
        self.selectable = selectable
        self.or_replace = or_replace
        self.options = options


@compiles(CreateView)
def visit_create_view(create, compiler, **kw):
    view = create.element
    preparer = compiler.preparer
    text = "\nCREATE "
    if create.or_replace:
        text += "OR REPLACE "
    text += "VIEW %s " % preparer.format_table(view)
    if create.columns:
        column_names = [preparer.format_column(col.element)
                        for col in create.columns]
        text += "("
        text += ', '.join(column_names)
        text += ") "
    if create.options:
        ops = []
        for opname, opval in create.options.items():
            ops.append('='.join([str(opname), str(opval)]))

        text += 'WITH (%s) ' % (', '.join(ops))

    compiled_selectable = (
        create.selectable
        if isinstance(create.selectable, Compiled)
        else compiler.sql_compiler.process(create.selectable, literal_binds=True)
    )
    text += "AS %s\n\n" % compiled_selectable
    return text


class DropView(_CreateDropBase):
    """
    Prepares a DROP VIEW statement.

    See parameters in :class:`~sqlalchemy.sql.ddl.DDL`.

    Parameters
    ----------
    element: sqlalchemy.Table
        The view to drop (sqlalchemy has no View construct)
    cascade: boolean
        Also drop any dependent views.
    if_exists: boolean
        Do nothing if the view does not exist.
        An exception will be raised for nonexistent views if not set.
    """

    __visit_name__ = "drop_view"

    def __init__(self, element, on=None, bind=None,
                 cascade=False, if_exists=False):
        try:
            super(DropView, self).__init__(element, on=on, bind=bind)
        except TypeError:
            # Since version 1.4.0 of SQLAlchemy the ** on ** parameter no
            # longer exists. it causes a ** TypeError ** exception
            if on is not None:
                raise TypeError("'on' is not supported on SQLAlchemy 1.4+")

            try:
                super(DropView, self).__init__(element, bind=bind)
            except TypeError:
                # Since version 2.0.0 of SQLAlchemy the ** bind ** parameter no
                # longer exists. it causes a ** TypeError ** exception
                if on is not None:
                    raise TypeError(
                        "'bind' is not supported on SQLAlchemy 1.4+")

                super(DropView, self).__init__(element)

        self.cascade = cascade
        self.if_exists = if_exists


@compiles(DropView)
def compile(drop, compiler, **kw):
    text = "\nDROP VIEW "
    if drop.if_exists:
        text += "IF EXISTS "
    text += compiler.preparer.format_table(drop.element)
    if drop.cascade:
        text += " CASCADE"
    return text
