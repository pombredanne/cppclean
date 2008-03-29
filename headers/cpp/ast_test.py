#!/usr/bin/env python
#
# Copyright 2008 Neal Norwitz
# Portions Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""AST test."""

__author__ = 'nnorwitz@google.com (Neal Norwitz)'


from test import test_support
import unittest

from cpp import ast
from cpp import tokenize


def _InstallGenericEqual(cls, attrs):
    """Add an __eq__ method to |cls| so objects can be compared for tests.

    Args:
      cls: Python class to add __eq__ method to
      attrs: string - space separated of attribute names to compare
    """
    attrs = attrs.split()
    def __eq__(self, other):
        if not isinstance(other, cls):
            return False
        for a in attrs:
            if getattr(self, a) != getattr(other, a):
                return False
        return True
    cls.__eq__ = __eq__


def _InstallEqualMethods():
    """Install __eq__ methods on the appropriate objects used for testing."""
    _InstallGenericEqual(ast.Class, 'name bases templated_types namespace')
_InstallEqualMethods()


def MakeBuilder(code_string):
    """Convenience function to make an AstBuilder from a code snippet.."""
    tokens = tokenize.GetTokens(code_string + '\n')
    return ast.AstBuilder(tokens, '<test>')


def Class(name, start=0, end=0, bases=None, body=None, templated_types=None,
          namespace=None):
    if namespace is None:
        namespace = []
    return ast.Class(start, end, name, bases, templated_types, body, namespace)


class _SequenceToParametersTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_GetVarTokensUpToTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_SkipIf0BlocksTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_GetMatchingCharTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilderGetNameTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_GetNestedTypesTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_GetTemplatedTypesTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_ConvertBaseTokensToAstTest(unittest.TestCase):

    def testSimple(self):
        builder = MakeBuilder('Bar')
        result = builder._ConvertBaseTokensToAST(list(builder.tokens))
        self.assertEqual(1, len(result))
        self.assertEqual(Class('Bar'), result[0])

    def testTemplate(self):
        builder = MakeBuilder('Bar<Foo>')
        result = builder._ConvertBaseTokensToAST(list(builder.tokens))
        self.assertEqual(1, len(result))
        self.assertEqual(Class('Bar', templated_types=[Class('Foo')]),
                         result[0])

    def testTemplateWithMultipleArgs(self):
        builder = MakeBuilder('Bar<Foo, Blah, Bling>')
        result = builder._ConvertBaseTokensToAST(list(builder.tokens))
        self.assertEqual(1, len(result))
        types = [Class('Foo'), Class('Blah'), Class('Bling')]
        self.assertEqual(Class('Bar', templated_types=types), result[0])

    def testTemplateWithMultipleTemplateArgsStart(self):
        builder = MakeBuilder('Bar<Foo<x>, Blah, Bling>')
        result = builder._ConvertBaseTokensToAST(list(builder.tokens))
        self.assertEqual(1, len(result))
        types = [Class('Foo', templated_types=[Class('x')]),
                 Class('Blah'),
                 Class('Bling')]
        self.assertEqual(types[0], result[0].templated_types[0])
        self.assertEqual(types[1], result[0].templated_types[1])
        self.assertEqual(types[2], result[0].templated_types[2])
        self.assertEqual(Class('Bar', templated_types=types), result[0])

    def testTemplateWithMultipleTemplateArgsMid(self):
        builder = MakeBuilder('Bar<Foo, Blah<x>, Bling>')
        result = builder._ConvertBaseTokensToAST(list(builder.tokens))
        self.assertEqual(1, len(result))
        types = [Class('Foo'),
                 Class('Blah', templated_types=[Class('x')]),
                 Class('Bling')]
        self.assertEqual(Class('Bar', templated_types=types), result[0])

    def testTemplateWithMultipleTemplateArgsEnd(self):
        builder = MakeBuilder('Bar<Foo, Blah, Bling<x> >')
        result = builder._ConvertBaseTokensToAST(list(builder.tokens))
        self.assertEqual(1, len(result))
        types = [Class('Foo'),
                 Class('Blah'),
                 Class('Bling', templated_types=[Class('x')])]
        self.assertEqual(Class('Bar', templated_types=types), result[0])


class AstBuilder_GetBasesTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilder_GetClassTest(unittest.TestCase):
    pass  # TODO(nnorwitz): implement.


class AstBuilderIntegrationTest(unittest.TestCase):
    """Unlike the other test cases in this file, this test case is
    meant to be an integration test.  It doesn't test any individual
    method.  It tests whole code blocks.
    """

    # TODO(nnorwitz): add lots more tests.

    def testClass_ForwardDeclaration(self):
        nodes = list(MakeBuilder('class Foo;').Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', body=None), nodes[0])

    def testClass_EmptyBody(self):
        nodes = list(MakeBuilder('class Foo {};').Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', body=[]), nodes[0])

    def testClass_InNamespaceSingle(self):
        nodes = list(MakeBuilder('namespace N { class Foo; }').Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', namespace=['N']), nodes[0])

    def testClass_InNamespaceMultiple(self):
        code = 'namespace A { namespace B { namespace C { class Foo; }}}'
        nodes = list(MakeBuilder(code).Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', namespace=['A', 'B', 'C']), nodes[0])

    def testClass_InAnonymousNamespaceSingle(self):
        nodes = list(MakeBuilder('namespace { class Foo; }').Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', namespace=[None]), nodes[0])

    def testClass_InAnonymousNamespaceMultiple(self):
        code = 'namespace A { namespace { namespace B { class Foo; }}}'
        nodes = list(MakeBuilder(code).Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', namespace=['A', None, 'B']), nodes[0])

    def testClass_NoAnonymousNamespace(self):
        nodes = list(MakeBuilder('class Foo;').Generate())
        self.assertEqual(1, len(nodes))
        self.assertEqual(Class('Foo', namespace=[]), nodes[0])


def test_main():
    tests = [t for t in globals().values()
             if isinstance(t, type) and issubclass(t, unittest.TestCase)]
    test_support.run_unittest(*tests)


if __name__ == '__main__':
    test_main()
