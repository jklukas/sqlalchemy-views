# -*- coding: utf-8 -*-
"""The view stuff."""


from sqlalchemy.schema import CreateColumn
from sqlalchemy.sql.ddl import _CreateDropBase
from sqlalchemy.ext.compiler import compiles


class CreateView(_CreateDropBase):
    """
    Prepares a Redshift CREATE VIEW statement.

    See parameters in :class:`~sqlalchemy.sql.ddl.DDL`.

    Parameters
    ----------
    element: sqlalchemy.Table
        The view to create (sqlalchemy has no View construct)
    selectable: sqalalchemy.Selectable
        A query that evaluates to a table.
        This table defines the columns and rows in the view.
    replace: boolean
        If the view already exists and `replace` is `True`,
        the existing view will be replaced. Otherwise, Redshift
        will raise an exception.
    """

    __visit_name__ = "create_view"

    def __init__(self, element, selectable, on=None, bind=None,
                 replace=False):
        super(CreateView, self).__init__(element, on=on, bind=bind)
        self.columns = [CreateColumn(column) for column in element.columns]
        self.selectable = selectable


@compiles(CreateView)
def visit_create_view(create, compiler, **kw):
    view = create.element
    preparer = compiler.dialect.identifier_preparer
    text = "\nCREATE VIEW %s " % preparer.format_table(view)
    if create.columns:
        column_names = [preparer.format_column(col.element)
                        for col in create.columns]
        text += "("
        text += ', '.join(column_names)
        text += ") "
    text += "AS %s\n\n" % compiler.sql_compiler.process(create.selectable)
    return text


class DropView(_CreateDropBase):
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
