from src import functions, parser
from collections import defaultdict
from typing import Any, DefaultDict


class KeyDefaultDict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


if __name__ == '__main__':
    global_namespace: DefaultDict[str, Any] = defaultdict(lambda: '')
    commands: DefaultDict[str, Any] = KeyDefaultDict(
        lambda name: functions.external(name))
    commands['cat'] = functions.Cat
    commands['echo'] = functions.Echo
    commands['wc'] = functions.Wc
    commands['pwd'] = functions.Pwd
    commands['exit'] = functions.Exit
    while True:
        cmd = input('>>')
        _parser = parser.Parser(global_namespace)
        _parser.parse(cmd)
        core = parser.Core(_parser, commands)
        core.evaluate_all()
        global_namespace = core.get_namespace()
