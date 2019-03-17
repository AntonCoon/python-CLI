from enum import Enum


class Token(Enum):
    # tokens
    FAIL = '0'
    PIPE = '|'
    SUBSTITUTION = '$'
    APOSTROPHE = '\''
    DOUBLE_APOSTROPHE = '\"'
    ASSIGNMENT = '='
    SPACE = ' '
    COMMA = ','
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
    def val(cls):
        return cls.value


class Parser(object):
    def __init__(self, namespace):
        self.namespace = namespace
        self.rez = []
        self.sub = []
        self.substituted = []
        self.is_correct = True
        self.output = []

    def parse(self, command):
        command = ' '.join(command.split())
        rez = []
        buf = ''
        for symbol in command:
            if Token.find(symbol) is Token.FAIL:
                buf += symbol
            else:
                if buf:
                    rez.append(buf)
                rez.append(symbol)
                buf = ''
            if Token.find(buf) is not Token.FAIL:
                if buf:
                    rez.append(buf)
                rez.append(buf)
                buf = ''
        if buf:
            rez.append(buf)
        self.rez = rez

    @staticmethod
    def substitute_on_segment(start, end, whole, namespace):
        # Make substitution on segment from
        # start position to end in the whole
        # array
        segment = []
        flag_continue = False
        for inner_index in range(start, end):
            if flag_continue:
                flag_continue = False
                continue
            element = whole[inner_index]
            if Token.find(element) == Token.SUBSTITUTION:
                var = whole[inner_index + 1]
                flag_continue = True
                if var in namespace:
                    segment.append(namespace[var])
                else:
                    segment.append('')
                inner_index += 1
            else:
                segment.append(element)
        return segment

    def substitute(self):
        if not self.rez:
            pass

        double_apostrophe_indexes = [
            idx for idx, elem in enumerate(self.rez)
            if Token.find(elem) is Token.DOUBLE_APOSTROPHE]
        self.is_correct = len(double_apostrophe_indexes) % 2 == 0

        # make substitution
        sub_1 = []
        if double_apostrophe_indexes:
            prev = 0
            for index in range(len(double_apostrophe_indexes) // 2):
                start = double_apostrophe_indexes[2 * index]
                end = double_apostrophe_indexes[2 * index + 1]
                sub_1 += self.rez[prev: start]
                prev = end
                sub_1 += Parser.substitute_on_segment(
                    start, end,
                    self.rez,
                    self.namespace
                )
            sub_1 += self.rez[prev:]
        else:
            sub_1 = self.rez[:]
        print(sub_1)

        apostrophe_indexes = [
            idx for idx, elem in enumerate(sub_1)
            if Token.find(elem) is Token.APOSTROPHE]
        self.is_correct = self.is_correct and len(apostrophe_indexes) % 2 == 0

        sub_2 = []
        if apostrophe_indexes:
            # merge all in single apostrophe
            prev = 0
            for index in range(len(apostrophe_indexes) // 2):
                start = apostrophe_indexes[2 * index]
                end = apostrophe_indexes[2 * index + 1]
                sub_2 += sub_1[prev: start]
                prev = end
                sub_2 += [''.join(sub_1[start: end])]
            sub_2 += sub_1[prev:]
        else:
            sub_2 = sub_1[:]

        self.sub = Parser.substitute_on_segment(
            0, len(sub_2), sub_2, self.namespace)

    def make_clear_output(self):
        skip_it = {
            Token.DOUBLE_APOSTROPHE,
            Token.SPACE,
            Token.APOSTROPHE
        }
        for elem in self.sub:
            if Token.find(elem) in skip_it or not elem:
                continue
            self.output.append(elem)


class Core(object):
    def __init__(self, parser):
        self.cmd = parser.output
        self.namespace = parser.namespace
        self.spltted = []

    def split_by_pipe(self):
        result = [[]]
        for element in self.cmd:
            if Token.find(element) is Token.PIPE:
                result.append([])
            else:
                result[-1].append(element)
        self.splitted = result


cmd = 'echo \'$Hello, world!\' | wc'
answer = 'echo \'$Hello, world!\' | wc'
nmsps = {'Hello': 'lol', 'zero': '0'}
_pars = Parser(nmsps)
_pars.parse(cmd)
_pars.substitute()
_pars.make_clear_output()
print(nmsps)
print(cmd)
print(''.join(_pars.sub))
print(answer)
print(_pars.output)

core = Core(_pars)
core.split_by_pipe()
print(core.splitted)
