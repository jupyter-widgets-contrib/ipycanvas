#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

import sys
import inspect
import types

import gast as ast


OPERATOR_MAPPING = {
    ast.Eq: '==', ast.NotEq: '!=',
    ast.Lt: '<', ast.LtE: '<=',
    ast.Gt: '>', ast.GtE: '>=',
    ast.Is: '===', ast.IsNot: '!==',
    ast.Add: '+', ast.Sub: '-',
    ast.Mult: '*', ast.Div: '/',
    ast.Mod: '%'
}


class Py2JSSyntaxError(SyntaxError):
    def __init__(self, message):
        error_msg = message + ', note that only a subset of Python is supported'
        super(Py2JSSyntaxError, self).__init__(error_msg)


class Py2JSNameError(NameError):
    def __init__(self, message):
        error_msg = message + ', note that only a subset of Python is supported'
        super(Py2JSNameError, self).__init__(error_msg)


class Py2JSVisitor(ast.NodeVisitor):
    """Visitor that turns a Node into JavaScript code."""

    def generic_visit(self, node):
        """Throwing an error by default."""
        raise Py2JSSyntaxError('Unsupported {} node'.format(node.__class__.__name__))

    def visit_Expr(self, node):
        """Turn a Python expression into JavaScript code."""
        return self.visit(node.value)

    def visit_NameConstant(self, node):
        """Turn a Python nameconstant expression into JavaScript code."""
        if node.value is False:
            return 'false'
        if node.value is True:
            return 'true'
        if node.value is None:
            return 'null'
        raise Py2JSNameError('name \'{}\' is not defined'.format(str(node.value)))

    def visit_Constant(self, node):
        """Turn a Python constant expression into JavaScript code."""
        if node.value is False:
            return 'false'
        if node.value is True:
            return 'true'
        if node.value is None:
            return 'null'
        return repr(node.value)

    def visit_Num(self, node):
        """Turn a Python num expression into JavaScript code."""
        return repr(node.n)

    def visit_Str(self, node):
        """Turn a Python str expression into JavaScript code."""
        return repr(node.s)

    def _visit_list_impl(self, node):
        """Turn a Python list expression into JavaScript code."""
        return '[{}]'.format(', '.join(self.visit(elt) for elt in node.elts))

    def visit_Tuple(self, node):
        """Turn a Python tuple expression into JavaScript code."""
        return self._visit_list_impl(node)

    def visit_List(self, node):
        """Turn a Python list expression into JavaScript code."""
        return self._visit_list_impl(node)

    def visit_Dict(self, node):
        """Turn a Python dict expression into JavaScript code."""
        return '{{{}}}'.format(
            ', '.join([
                '{}: {}'.format(self.visit(node.keys[idx]), self.visit(node.values[idx]))
                for idx in range(len(node.keys))
            ])
        )

    def visit_UnaryOp(self, node):
        """Turn a Python unaryop expression into JavaScript code."""
        if isinstance(node.op, ast.Not):
            return '!({})'.format(self.visit(node.operand))
        if isinstance(node.op, ast.USub):
            return '-{}'.format(self.visit(node.operand))
        if isinstance(node.op, ast.UAdd):
            return '+{}'.format(self.visit(node.operand))

        raise Py2JSSyntaxError('Unsupported {} operator'.format(node.op.__class__.__name__))

    def visit_BoolOp(self, node):
        """Turn a Python boolop expression into JavaScript code."""
        return '({} {} {})'.format(
            self.visit(node.values[0]),
            '||' if isinstance(node.op, ast.Or) else '&&',
            self.visit(node.values[1])
        )

    def _visit_binop_impl(self, left_node, op, right_node):
        left = left_node if isinstance(left_node, str) else self.visit(left_node)
        right = self.visit(right_node)

        # Use Array.indexof or String.indexof depending on the right type
        # if isinstance(op, ast.In):
        #     return 'indexof({}, {}) != -1'.format(right, left)
        # if isinstance(op, ast.NotIn):
        #     return 'indexof({}, {}) == -1'.format(right, left)
        if isinstance(op, ast.Pow):
            return 'Math.pow({}, {})'.format(left, right)

        operator = OPERATOR_MAPPING.get(op.__class__)

        if operator is None:
            raise Py2JSSyntaxError('Unsupported {} operator'.format(op.__class__.__name__))

        return '{} {} {}'.format(left, operator, right)

    def visit_BinOp(self, node):
        """Turn a Python binop expression into JavaScript code."""
        return '({})'.format(self._visit_binop_impl(node.left, node.op, node.right))

    def visit_If(self, node):
        """Turn a Python if expression into JavaScript code."""
        return 'if ({}) {{\n{}\n}} else {{\n{}\n}}\n'.format(
            self.visit(node.test),
            '\n'.join(['{};'.format(self.visit(subnode)) for subnode in node.body]),
            '\n'.join(['{};'.format(self.visit(subnode)) for subnode in node.orelse])
        )

    def visit_IfExp(self, node):
        """Turn a Python ternary operator into JavaScript code."""
        return '({} ? {} : {})'.format(
            self.visit(node.test),
            self.visit(node.body),
            self.visit(node.orelse)
        )

    def visit_Compare(self, node):
        """Turn a Python compare expression into JavaScript code."""
        left_operand = node.left

        for idx in range(len(node.comparators)):
            left_operand = self._visit_binop_impl(left_operand, node.ops[idx], node.comparators[idx])

        return '({})'.format(left_operand)

    def visit_Name(self, node):
        """Turn a Python name expression into JavaScript code."""
        return node.id

    def visit_Call(self, node):
        """Turn a Python call expression into JavaScript code."""
        args = ', '.join([self.visit(arg) for arg in node.args])

        return '{func_name}({args})'.format(func_name=self.visit(node.func), args=args)

    def visit_Assign(self, node):
        """Turn a Python assignment expression into JavaScript code."""
        # TODO Put var in front of the target if not in the scope yet, and if it's a Name?
        targets = ' = '.join(self.visit(target) for target in node.targets)
        return '{} = {}'.format(targets, self.visit(node.value))

    def visit_Attribute(self, node):
        """Turn a Python attribute expression into JavaScript code."""
        return '{}.{}'.format(self.visit(node.value), node.attr)


def py2js(value):
    """Convert Python code or Python function to JavaScript code."""
    if isinstance(value, str):
        parsed = ast.parse(value, '<string>', 'exec')

        return ';\n'.join([Py2JSVisitor().visit(node) for node in parsed.body])

    if isinstance(value, (types.FunctionType, types.MethodType)):
        if getattr(value, '__name__', '') in ('', '<lambda>'):
            raise RuntimeError('Anonymous functions not supported')

        value = inspect.getsource(value)

        module = ast.parse(value, '<string>', 'exec')

        func = module.body[0]

        return ';\n'.join([Py2JSVisitor().visit(node) for node in func.body])

    raise RuntimeError('py2js only supports a code string or function as input')
