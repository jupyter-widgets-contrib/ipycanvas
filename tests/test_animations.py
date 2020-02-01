import pytest

from ipycanvas.animation import py2js, Py2JSSyntaxError


def test_nameconstant():
    code = 'False'
    assert py2js(code) == 'false'

    code = 'True'
    assert py2js(code) == 'true'

    code = 'None'
    assert py2js(code) == 'null'


def test_num():
    code = '36'
    assert py2js(code) == '36'


def test_str():
    code = '\'white\''
    assert py2js(code) == '\'white\''


def test_tuple():
    code = '(True, 3, \'hello\')'
    assert py2js(code) == '[true, 3, \'hello\']'

    code = '((True, 3, \'hello\'), 3)'
    assert py2js(code) == '[[true, 3, \'hello\'], 3]'


def test_list():
    code = '[True, 3, \'hello\']'
    assert py2js(code) == '[true, 3, \'hello\']'


def test_dict():
    code = '{\'hello\': 3, \'there\': 4}'
    assert py2js(code) == '{\'hello\': 3, \'there\': 4}'

    code = '{\'hello\': 3, \'there\': 4}'
    assert py2js(code) == '{\'hello\': 3, \'there\': 4}'


def test_unary():
    code = 'not value'
    assert py2js(code) == '!(value)'

    code = '-value'
    assert py2js(code) == '-value'

    code = '+value'
    assert py2js(code) == '+value'


def test_binary():
    code = 'value or 3'
    assert py2js(code) == '(value || 3)'

    code = 'value and 3'
    assert py2js(code) == '(value && 3)'

    code = 'value + 3'
    assert py2js(code) == '(value + 3)'

    code = 'value**3'
    assert py2js(code) == '(Math.pow(value, 3))'

    # Unsupported operator
    code = 'value & x'
    with pytest.raises(Py2JSSyntaxError):
        py2js(code)


def test_ternary():
    code = '3 if value else 4'
    assert py2js(code) == '(value ? 3 : 4)'


def test_compare():
    code = '3 < value <= 4'
    assert py2js(code) == '(3 < value <= 4)'

    # code = 'value in (\'ford\', \'chevrolet\')'
    # assert py2js(code) == '(indexof([\'ford\', \'chevrolet\'], value) != -1)'

    # code = '\'chevrolet\' in value'
    # assert py2js(code) == '(indexof(value, \'chevrolet\') != -1)'

    # code = '\'chevrolet\' not in value'
    # assert py2js(code) == '(indexof(value, \'chevrolet\') == -1)'
