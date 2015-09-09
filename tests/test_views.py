import re

import sqlalchemy as sa
from sqlalchemy import Table

from sqlalchemy_views import CreateView, DropView


t1 = Table('t1', sa.MetaData(),
           sa.Column('col1', sa.Integer(), primary_key=True),
           sa.Column('col2', sa.Integer()))


def clean(query):
    return re.sub(r'\s+', ' ', query).strip()


def compile_query(query):
    return str(query.compile(
        compile_kwargs={'literal_binds': True})
    )


def test_basic_view():
    expected_result = """
    CREATE VIEW myview AS SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select([t1])
    view = Table('myview', sa.MetaData())
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))


def test_view_with_column_names():
    expected_result = """
    CREATE VIEW myview (col3, col4) AS SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select([t1])
    view = Table('myview', sa.MetaData(),
                 sa.Column('col3', sa.Integer(), primary_key=True),
                 sa.Column('col4', sa.Integer()))
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))


def test_view_with_delimited_identifiers():
    expected_result = """
    CREATE VIEW "my nice view!" ("col#1", "select") AS
      SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select([t1])
    view = Table('my nice view!', sa.MetaData(),
                 sa.Column('col#1', sa.Integer(), primary_key=True),
                 sa.Column('select', sa.Integer()))
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))


def test_drop_basic_view():
    expected_result = """
    DROP VIEW myview
    """
    view = Table('myview', sa.MetaData())
    drop_view = DropView(view)
    assert clean(expected_result) == clean(compile_query(drop_view))


def test_drop_cascade():
    expected_result = """
    DROP VIEW myview CASCADE
    """
    view = Table('myview', sa.MetaData())
    drop_view = DropView(view, cascade=True)
    assert clean(expected_result) == clean(compile_query(drop_view))


def test_drop_if_exists():
    expected_result = """
    DROP VIEW IF EXISTS myview
    """
    view = Table('myview', sa.MetaData())
    drop_view = DropView(view, if_exists=True)
    assert clean(expected_result) == clean(compile_query(drop_view))


def test_drop_with_delimited_identifier():
    expected_result = """
    DROP VIEW IF EXISTS "my nice view!"
    """
    view = Table('my nice view!', sa.MetaData())
    drop_view = DropView(view, if_exists=True)
    assert clean(expected_result) == clean(compile_query(drop_view))
