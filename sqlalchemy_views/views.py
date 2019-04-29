# -*- coding: utf-8 -*-
"""The view stuff."""


from sqlalchemy.schema import CreateColumn
from sqlalchemy.sql.ddl import _CreateDropBase
from sqlalchemy.ext.compiler import compiles


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
    """

    __visit_name__ = "create_view"

    def __init__(self, element, selectable, on=None, bind=None,
                 or_replace=False):
        super(CreateView, self).__init__(element, on=on, bind=bind)
        self.columns = [CreateColumn(column) for column in element.columns]
        self.selectable = selectable
        self.or_replace = or_replace


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
    text += "AS %s\n\n" % compiler.sql_compiler.process(create.selectable, literal_binds=True)
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
        super(DropView, self).__init__(element, on=on, bind=bind)
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
