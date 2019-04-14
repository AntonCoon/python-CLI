import os
from abc import ABC
from io import StringIO


class CommandInterface(ABC):
    def __init__(self):
        self.__inp_stream = None
        self.__out_stream = None

    def evaluate(self, *args) -> None:
        pass

    def set_inp_stream(self, stream: StringIO) -> None:
        self.__inp_stream = stream

    def set_out_stream(self, stream: StringIO) -> None:
        self.__out_stream = stream

    def get_inp_stream(self) -> StringIO:
        return self.__inp_stream

    def get_out_stream(self) -> StringIO:
        return self.__out_stream


class Cat(CommandInterface):
    def evaluate(self, *args) -> None:
        if args:
            path = args[0]
            with open(path, 'r') as input_file:
                for line in input_file:
                    self.get_out_stream().write(line)
        else:
            line = self.get_inp_stream().readline()
            while line:
                print(line, file=self.get_out_stream())
                line = self.get_inp_stream().readline()


class Echo(CommandInterface):
    def evaluate(self, *args) -> None:
        print(' '.join(args), file=self.get_out_stream())


class Wc(CommandInterface):
    def evaluate(self, *args) -> None:
        result = []
        for path in args:
            result.append({'line': 0, 'word': 0, 'byte': 0, 'file': path})
            with open(path, 'r') as f:
                for line in f:
                    result[-1]['line'] += 1
                    result[-1]['word'] += len(line.split())
            with open(path, 'rb') as f:
                for line in f:
                    result[-1]['byte'] += len(line)
        string_result = ''
        for res in result:
            string_result += \
                '  {}  {}  {}  {}\n'.format(
                    res['line'],
                    res['word'],
                    res['byte'],
                    res['file'])

        print(string_result, file=self.get_out_stream())


class Pwd(CommandInterface):
    def evaluate(self, *args) -> None:
        print(os.getcwd(), file=self.get_out_stream())


class External(CommandInterface):
    def evaluate(self, *args) -> None:
        print('external', file=self.get_out_stream())
