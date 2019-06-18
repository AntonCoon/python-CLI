from src import functions, parser
from collections import defaultdict
from typing import Any, DefaultDict


class KeyDefaultDict(defaultdict):
    # Default dict version with parametric default factory
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
    # main loop
    while True:
        cmd = input('>>')
        _parser = parser.Parser(global_namespace)
        try:
            _parser.parse(cmd)
        except Exception as e:
            print('parsing error', e)
        core = parser.Core(_parser, commands)
        try:
            core.evaluate_all()
        except Exception as e:
            print('evaluation error', e)

        global_namespace = core.get_namespace()
