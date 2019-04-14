from enum import Enum
from collections import defaultdict
from sys import stdin, stdout
from io import StringIO
from typing import Any, DefaultDict


class Token(Enum):
    # tokens
    FAIL = '0'
    PIPE = '|'
    SUBSTITUTION = '$'
    APOSTROPHE = '\''
    DOUBLE_APOSTROPHE = '\"'
    ASSIGNMENT = '='
    SPACE = ' '
    SEMICOLON = ';'
    COLON = ':'
    # commands
    CAT = 'cat'
    ECHO = 'echo'
    WC = 'wc'
    PWD = 'pwd'

    @staticmethod
    def find(symbol: str):
        for name, member in Token.__members__.items():
            if member.value == symbol:
                return member
        return Token.FAIL

    @classmethod
    def val(cls) -> str:
        return cls.value


class ApostropheException(Exception):
    def __init___(self):
        super().__init__('Invalid apostrophe count')


class EmptyParserResult(Exception):
    def __init__(self):
        super().__init__('Run method parse before get_parsed')


class Parser(object):
    def __init__(self, namespace: defaultdict):
        self.__namespace = namespace
        self.__rez = None

    def __split_by_tokens(self, command: str) -> None:
        # split command by tokens
        __rez = []
        buf = ''
        for symbol in command:
            if Token.find(symbol) is Token.FAIL:
                buf += symbol
            else:
                __rez.append(buf)
                __rez.append(symbol)
                buf = ''
        __rez.append(buf)
        self.__rez = [e for e in __rez if e]

    @staticmethod
    def substitute_on_segment(segment: list, namespace: defaultdict) -> list:
        for idx, element in enumerate(segment):
            if Token.find(element) is Token.SUBSTITUTION:
                segment[idx + 1] = namespace[segment[idx + 1]]
        return [e for e in segment if Token.find(e) is not Token.APOSTROPHE and
                Token.find(e) is not Token.SUBSTITUTION]

    def __substitute_inside_2apostrophe(self) -> None:
        positions = [pos for pos, elem in enumerate(self.__rez)
                     if Token.find(elem) is Token.DOUBLE_APOSTROPHE]
        if len(positions) % 2 != 0:
            raise ApostropheException
        positions = [0] + positions + [len(self.__rez)]

        substituted = []
        for idx, (start, end) in enumerate(zip(positions[:-1], positions[1:])):
            if idx % 2 == 0:
                substituted += self.__rez[start: end]
            else:
                substituted += Parser.substitute_on_segment(
                    self.__rez[start: end], self.__namespace)

        self.__rez = substituted

    def __join_inside_single_apostrophe(self) -> None:
        positions = [pos for pos, elem in enumerate(self.__rez)
                     if Token.find(elem) is Token.APOSTROPHE]
        if len(positions) % 2 != 0:
            raise ApostropheException

        positions = [0] + positions + [len(self.__rez)]
        joined = []
        for idx, (start, end) in enumerate(zip(positions[:-1], positions[1:])):
            if idx % 2 == 0:
                joined += self.__rez[start: end]
            else:
                joined += [''.join(self.__rez[start + 1: end])]

        self.__rez = [e for e in joined if
                      not Token.find(e) is Token.SUBSTITUTION]

    def parse(self, command: str) -> None:
        self.__split_by_tokens(command)
        self.__substitute_inside_2apostrophe()
        self.__join_inside_single_apostrophe()
        # clear all apostrophe and empty or space
        self.__rez = [e for e in self.__rez if e and
                      not Token.find(e) is Token.APOSTROPHE and
                      not Token.find(e) is Token.DOUBLE_APOSTROPHE and
                      not Token.find(e) is Token.SPACE]

    def get_parsed(self) -> list:
        if self.__rez is None:
            raise EmptyParserResult
        return self.__rez

    def get_namespace(self):
        return self.__namespace


class Core(object):
    def __init__(self, parser: Parser, commands: DefaultDict[str, Any]):
        self.__commands = commands
        self.__parsed_command = parser.get_parsed()
        self.__namespace = parser.get_namespace()
        self.__inp_stream = stdin
        self.__out_stream = stdout

    def get_namespace(self):
        return self.__namespace

    def __make_assignments(self) -> bool:
        arg_num = len(self.__parsed_command)
        if arg_num == 3 and Token.find(self.__parsed_command[0]) is Token.FAIL:
            var = self.__parsed_command[0]
            self.__namespace[var] = self.__parsed_command[2]
            return True

    def __commands_and_args(self) -> list:
        divided_by_pipe = [[]]
        for elem in self.__parsed_command:
            if Token.find(elem) is Token.PIPE:
                divided_by_pipe.append([])
            else:
                divided_by_pipe[-1].append(elem)
        return [(arr[0], tuple(arr[1:])) for arr in divided_by_pipe]

    def test(self):
        return self.__commands_and_args()

    def evaluate_all(self) -> None:

        if self.__make_assignments():
            return

        cmd_arg = self.__commands_and_args()
        out_stream = StringIO()
        inp_stream = self.__inp_stream
        for pair in cmd_arg:
            command_name, args = pair
            command_class = self.__commands[command_name]()
            command_class.set_inp_stream(inp_stream)
            command_class.set_out_stream(out_stream)
            command_class.evaluate(*args)
            inp_stream = out_stream
            out_stream.seek(0, 0)
            out_stream = StringIO()
        print(inp_stream.getvalue(), file=self.__out_stream, end='')
