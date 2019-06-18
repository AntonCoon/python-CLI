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
    def find(symbol: str) -> Enum:
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
    # Class with methods needed for pars string commands to array of strings
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
        # make each substitution on segment
        for idx, element in enumerate(segment):
            if Token.find(element) is Token.SUBSTITUTION:
                segment[idx + 1] = namespace[segment[idx + 1]]
        return [e for e in segment if Token.find(e) and
                Token.find(e) is not Token.SUBSTITUTION]

    def __substitute_inside_2apostrophe(self) -> None:
        # split list of commands by double apostrophe and make substitution
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
        # join all arguments inside single apostrophe
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

    def __substitute_outside_apostrophe(self) -> None:
        self.__rez = Parser.substitute_on_segment(self.__rez, self.__namespace)

    def __join_all_not_separated(self) -> None:
        accomulated = ['']
        if len(self.__rez) < 2:
            return
        for idx, element in enumerate(self.__rez):
            if Token.find(element) is Token.FAIL and Token.find(self.__rez[idx - 1]) is Token.FAIL:
                accomulated[-1] += element
            else:
                accomulated += [element]
        self.__rez = [e for e in accomulated if e]

    def parse(self, command: str) -> None:
        self.__split_by_tokens(command)
        self.__substitute_inside_2apostrophe()
        self.__substitute_outside_apostrophe()
        self.__join_inside_single_apostrophe()
        # join all tokens which not separated by space
        self.__join_all_not_separated()
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
    # class which responsible for evaluate each command.It take parser and
    # evaluate each command.If commands split by pipe then stream with output
    # of previous command passed to next command
    def __init__(self, parser: Parser, commands: DefaultDict[str, Any]):
        self.__commands = commands
        self.__parsed_command = parser.get_parsed()
        self.__namespace = parser.get_namespace()
        self.__inp_stream = stdin
        self.__out_stream = stdout

    def get_namespace(self):
        return self.__namespace

    def __make_assignments(self) -> bool:
        if len(self.__parsed_command) < 3:
            return False
        # make assignment if it's possible
        arg_num = len(self.__parsed_command)
        token_ = Token.find(self.__parsed_command[1])
        if arg_num == 3 and token_ is Token.ASSIGNMENT:
            var = self.__parsed_command[0]
            self.__namespace[var] = self.__parsed_command[2]
            return True

    def __commands_and_args(self) -> list:
        # transform command array to array of tuples of commands and it's
        # arguments
        divided_by_pipe = [[]]
        for elem in self.__parsed_command:
            if Token.find(elem) is Token.PIPE:
                divided_by_pipe.append([])
            else:
                divided_by_pipe[-1].append(elem)
        return [(arr[0], tuple(arr[1:])) for arr in divided_by_pipe]

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
