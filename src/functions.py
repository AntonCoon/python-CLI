import os
import argparse
import re
from abc import ABC
from io import StringIO


class CommandInterface(ABC):
    # Common command interface for available commands
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
    # Implementation of cat command. Just print stream input in stdout
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
    # Implementation of echo command. Print arguments in stdout
    def evaluate(self, *args) -> None:
        args = list(map(str, args))
        print(' '.join(args), file=self.get_out_stream())


class Wc(CommandInterface):
    # Implementation of wc command. Calculate line, word and byte amount
    # and print it in stdout
    def evaluate(self, *args) -> None:
        if args:
            args = list(map(str, args))
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
        else:
            res = {'line': 0, 'word': 0, 'byte': 0}
            line = self.get_inp_stream().readline()
            while line:
                res['line'] += 1
                res['word'] += len(line.split())
                res['byte'] += len(line.encode('utf-8'))
                line = self.get_inp_stream().readline()
            string_result = '  {}  {}  {}\n'.format(
                        res['line'],
                        res['word'],
                        res['byte'])
            print(string_result, file=self.get_out_stream())



class Pwd(CommandInterface):
    # Implementation of wc command, print current working directory in stdout
    def evaluate(self, *args) -> None:
        print(os.getcwd(), file=self.get_out_stream())


class Grep(CommandInterface):
    # Grep command implementation
    def __init__(self):
        super().__init__()

        self.file_content = None

    parser = argparse.ArgumentParser(
        description='Simple grep implementation')

    parser.add_argument('pattern', metavar='PATTERN',
                        type=str, nargs=1)

    parser.add_argument('files', metavar='FILES', type=str,
                        nargs='+')

    parser.add_argument('-i', '--ignore-case',
                        help='ignore case of letters',
                        default=False, action='store_true')

    parser.add_argument('-w', '--whole-words',
                        help='search just whole words',
                        default=False, action='store_true')

    parser.add_argument('-A', '--accumulate',
                        metavar='COUNT', type=int,
                        help='Increase output verbosity.')

    def create_output_string(self, parsed_args, path_to_file=None) -> str:
        # method take parsed arguments and path to file
        # and return output string. In case when path to file by default
        # input stream of class using as input
        def _grep(input_stream: StringIO) -> str:
            # inner
            _flag = 0
            if parsed_args.ignore_case:
                _flag = re.IGNORECASE
            _pattern = parsed_args.pattern[0]
            if parsed_args.whole_words:
                _pattern = '\b{}\b'.format(parsed_args.pattern[0])
            after_line = 0
            if parsed_args.accumulate:
                after_line = parsed_args.accumulate
            result = list()
            line_number = 0
            for line in input_stream:
                line_number += 1
                if re.search(_pattern, line, flags=_flag):
                    result.append(line)
                    break
            for idx, line in enumerate(input_stream):
                if line_number < idx < line_number + after_line:
                    result.append(line)
                if idx > line_number + after_line:
                    break

            return ''.join(result)

        if path_to_file is None:
            return _grep(self.get_inp_stream())
        else:
            with open(path_to_file) as _input_stream:
                return _grep(_input_stream)

    def evaluate(self, *args) -> None:
        args = list(map(str, args))
        parsed_args = Grep.parser.parse_args(args)
        if parsed_args.files:
            for file in parsed_args.files:
                print(self.create_output_string(parsed_args, file),
                      file=self.get_out_stream(), end='')
        else:
            print(self.create_output_string(parsed_args),
                  file=self.get_out_stream(), end='')


class Exit(CommandInterface):
    def evaluate(self, *args) -> None:
        exit()


def external(name):
    # Factory of external command classes
    class NamedExternal(CommandInterface):
        def evaluate(self, *args) -> None:
            args = list(map(str, args))
            os.system(name + ' ' + ' '.join(args))

    return NamedExternal
