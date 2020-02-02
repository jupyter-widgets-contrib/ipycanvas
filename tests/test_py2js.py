from textwrap import dedent

import pytest

from ipycanvas.py2js import py2js, Py2JSSyntaxError


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


def test_if():
    code = dedent("""
        if t < 0.3:
            canvas.fill_rect(0, 0, 20, 20)
        else:
            canvas.fill_rect(20, 20, 20, 20)
        """)
    assert py2js(code) == """if ((t < 0.3)) {
canvas.fill_rect(0, 0, 20, 20);
} else {
canvas.fill_rect(20, 20, 20, 20);
}
"""


def test_call():
    code = 'canvas.fill_rect(20, 32, compute_size(t), compute_size(t))'
    assert py2js(code) == 'canvas.fill_rect(20, 32, compute_size(t), compute_size(t))'


def test_subscript():
    code = "data['test'] = 36"
    assert py2js(code) == "data['test'] = 36"

    code = "data[0] = 35"
    assert py2js(code) == "data[0] = 35"


def test_compare():
    code = '3 < value <= 4'
    assert py2js(code) == '(3 < value <= 4)'

    # code = 'value in (\'ford\', \'chevrolet\')'
    # assert py2js(code) == '(indexof([\'ford\', \'chevrolet\'], value) != -1)'

    # code = '\'chevrolet\' in value'
    # assert py2js(code) == '(indexof(value, \'chevrolet\') != -1)'

    # code = '\'chevrolet\' not in value'
    # assert py2js(code) == '(indexof(value, \'chevrolet\') == -1)'


def test_assign():
    code = "canvas.fill_style = 'red'"
    assert py2js(code) == "canvas.fill_style = 'red'"
