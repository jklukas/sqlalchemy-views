import re

import pytest
import sqlalchemy as sa
from sqlalchemy import Table
from sqlalchemy.dialects import postgresql
from packaging.version import Version

from sqlalchemy_views import CreateView, DropView

sqla_version = Version(sa.__version__)

t1 = Table('t1', sa.MetaData(),
           sa.Column('col1', sa.Integer(), primary_key=True),
           sa.Column('col2', sa.Integer()))


def clean(query):
    return re.sub(r'\s+', ' ', query).strip()


def compile_query(query, **kwargs):
    compile_kwargs = {'literal_binds': True}
    compiled = query.compile(compile_kwargs=compile_kwargs, **kwargs)
    return str(compiled)


@pytest.mark.parametrize("schema,schema_map,expected_result", [
    (None, None, "CREATE VIEW myview AS SELECT t1.col1, t1.col2 FROM t1"),
    ('myschema', None, "CREATE VIEW myschema.myview AS SELECT myschema.t1.col1, myschema.t1.col2 FROM myschema.t1"),
    ])
def test_basic_view(schema, schema_map, expected_result):
    t1 = Table('t1', sa.MetaData(schema=schema),
               sa.Column('col1', sa.Integer(), primary_key=True),
               sa.Column('col2', sa.Integer()))
    selectable = sa.sql.select(t1)
    view = Table('myview', sa.MetaData(schema=schema))
    create_view = CreateView(view, selectable)
    actual = compile_query(create_view, schema_translate_map=schema_map)
    assert clean(expected_result) == clean(actual)


def test_view_replace():
    expected_result = """
    CREATE OR REPLACE VIEW myview AS SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select(t1)
    view = Table('myview', sa.MetaData())
    create_view = CreateView(view, selectable, or_replace=True)
    assert clean(expected_result) == clean(compile_query(create_view))


def test_view_with_column_names():
    expected_result = """
    CREATE VIEW myview (col3, col4) AS SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select(t1)
    view = Table('myview', sa.MetaData(),
                 sa.Column('col3', sa.Integer(), primary_key=True),
                 sa.Column('col4', sa.Integer()))
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))

def test_view_with_literals():
    expected_result = """
    CREATE VIEW myview (col3) AS SELECT 0 AS anon_1
    """
    selectable = sa.sql.select(sa.literal(0))
    view = Table('myview', sa.MetaData(),
                 sa.Column('col3', sa.Integer()))
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))

def test_view_with_delimited_identifiers():
    expected_result = """
    CREATE VIEW "my nice view!" ("col#1", "select") AS
      SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select(t1)
    view = Table('my nice view!', sa.MetaData(),
                 sa.Column('col#1', sa.Integer(), primary_key=True),
                 sa.Column('select', sa.Integer()))
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))


def test_view_with_options():
    expected_result = "CREATE VIEW myview WITH (check_option=local) AS SELECT t1.col1, t1.col2 FROM t1"
    t1 = Table('t1', sa.MetaData(),
               sa.Column('col1', sa.Integer(), primary_key=True),
               sa.Column('col2', sa.Integer()))
    selectable = sa.sql.select(t1)
    view = Table('myview', sa.MetaData())
    create_view = CreateView(view, selectable, options=dict(check_option='local'))
    actual = compile_query(create_view)
    assert clean(expected_result) == clean(actual)

def test_view_with_compiled_select():
    expected_result = """
    CREATE VIEW myview AS SELECT DISTINCT ON (t1.col2) t1.col1, t1.col2 FROM t1
    """
    selectable = (
        sa.sql.select(t1).distinct(t1.c.col2).compile(dialect=postgresql.dialect())
    )
    view = Table("myview", sa.MetaData())
    create_view = CreateView(view, selectable)
    assert clean(expected_result) == clean(compile_query(create_view))


@pytest.mark.skipif(sqla_version < Version('1.4.0'),
                    reason="Only for SQLAlchemy >= 1.4.0")
def test_view_with_on_parameter_is_not_none():
    expected_result = """
    CREATE OR REPLACE VIEW myview AS SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select(t1)
    view = Table('myview', sa.MetaData())
    with pytest.raises(TypeError):
        create_view = CreateView(
            view, selectable, on=True)  # on is not None


@pytest.mark.skipif(sqla_version < Version('2.0.0'),
                    reason="Only for SQLAlchemy >= 2.0.0")
def test_view_with_bind_parameter_is_not_none():
    expected_result = """
    CREATE OR REPLACE VIEW myview AS SELECT t1.col1, t1.col2 FROM t1
    """
    selectable = sa.sql.select(t1)
    view = Table('myview', sa.MetaData())
    with pytest.raises(TypeError):
        create_view = CreateView(
            view, selectable, bind=True)  # bind is not None


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


@pytest.mark.skipif(sqla_version < Version('1.4.0'),
                    reason="Only for SQLAlchemy >= 1.4.0")
def test_drop_with_on_parameter_is_not_none():
    expected_result = """
    DROP VIEW myview
    """
    view = Table('myview', sa.MetaData())
    with pytest.raises(TypeError):
        DropView(view, on=True)  # on is not None


@pytest.mark.skipif(sqla_version < Version('2.0.0'),
                    reason="Only for SQLAlchemy >= 2.0.0")
def test_drop_with_bind_parameter_is_not_none():
    expected_result = """
    DROP VIEW myview
    """
    view = Table('myview', sa.MetaData())
    with pytest.raises(TypeError):
        DropView(view, bind=True)  # bind is not None
