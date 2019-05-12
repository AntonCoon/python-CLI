import unittest
import os
import sys
from collections import defaultdict
from typing import Any, DefaultDict
from src import functions, parser
from io import StringIO


# Functions tests
class CatTest(unittest.TestCase):

    def test(self):
        cat = functions.Cat()
        test_stream = StringIO()
        cat.set_out_stream(test_stream)
        cat.evaluate('test_files/test_1.txt')
        self.assertEqual(test_stream.getvalue(), 'simple test')


class EchoTest(unittest.TestCase):

    def test(self):
        echo = functions.Echo()
        test_stream_out = StringIO()
        echo.set_out_stream(test_stream_out)
        echo.evaluate('test', 1, 2, 2.93)
        test_stream = echo.get_out_stream()
        self.assertEqual(test_stream.getvalue(), 'test 1 2 2.93\n')


class WcTest(unittest.TestCase):

    def test(self):
        wc = functions.Wc()
        test_stream_out = StringIO()
        wc.set_out_stream(test_stream_out)
        wc.evaluate('test_files/test_1.txt')
        test_stream = wc.get_out_stream()
        self.assertEqual(
            test_stream.getvalue(),
            '  1  2  11  test_files/test_1.txt\n\n')


class PwdTest(unittest.TestCase):

    def test(self):
        pwd = functions.Pwd()
        test_stream_out = StringIO()
        pwd.set_out_stream(test_stream_out)
        pwd.evaluate()
        test_stream = pwd.get_out_stream()
        self.assertEqual(test_stream.getvalue(), os.getcwd()+'\n')


# parser tests
class PublicParser(parser.Parser):
    def split_by_tokens(self, command: str) -> list:
        self._Parser__split_by_tokens(command)
        return self._Parser__rez

    def substitute_inside_2apostrophe(self) -> list:
        self._Parser__substitute_inside_2apostrophe()
        return self._Parser__rez

    def join_inside_single_apostrophe(self) -> list:
        self._Parser__join_inside_single_apostrophe()
        return self._Parser__rez

    def get_rez(self):
        return self._Parser__rez


class ParserTestSplit(unittest.TestCase):
    def test(self):
        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        _parser = PublicParser(namespace)
        self.assertEqual(
            _parser.split_by_tokens('wc test_1.txt | echo'),
            ['wc', ' ', 'test_1.txt', ' ', '|', ' ', 'echo'])


class ParserTestSubstitute(unittest.TestCase):
    def test(self):
        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        _parser = PublicParser(namespace)

        self.assertEqual(_parser.substitute_on_segment(
            ['wc', '\"', '$', 'test_1', '\"'], namespace),
            ['wc', '"', '', '"']
        )


class ParserTestSubstituteInside2Apostrophe(unittest.TestCase):
    def test(self):
        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        namespace['test'] = 'test_1.txt'
        _parser = PublicParser(namespace)

        _parser.split_by_tokens('wc \"$test\" | echo')
        self.assertEqual(
            _parser.substitute_inside_2apostrophe(),
            ['wc', ' ', '"', 'test_1.txt', '"', ' ', '|', ' ', 'echo'])


class ParserTestJoin(unittest.TestCase):
    def test(self):
        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        _parser = PublicParser(namespace)

        _parser.split_by_tokens('echo \'one two\'')
        _parser.substitute_inside_2apostrophe()
        self.assertEqual(
            _parser.join_inside_single_apostrophe(),
            ['echo', ' ', 'one two', "'"]
        )


class ParserTestParse(unittest.TestCase):
    def test(self):
        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        _parser = PublicParser(namespace)
        _parser.parse('echo one two')
        self.assertEqual(_parser.get_rez(), ['echo', 'one', 'two'])

        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        namespace['test'] = 'test_files/test_1.txt'
        _parser = PublicParser(namespace)
        _parser.parse('echo \"$test two\"')
        self.assertEqual(
            _parser.get_rez(),
            ['echo', 'test_files/test_1.txt', 'two']
        )

        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        _parser = PublicParser(namespace)
        _parser.parse('echo \"$test two\"')
        self.assertEqual(
            _parser.get_rez(),
            ['echo', 'two']
        )

        namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
        _parser = PublicParser(namespace)
        _parser.parse('echo \'test two\'')
        self.assertEqual(
            _parser.get_rez(),
            ['echo', 'test two']
        )


if __name__ == '__main__':
    unittest.main()
