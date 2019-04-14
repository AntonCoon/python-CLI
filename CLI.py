from src import functions, parser
from collections import defaultdict
from typing import Any, DefaultDict


if __name__ == '__main__':
    global_namespace = defaultdict()
    commands: DefaultDict[str, Any] = defaultdict(lambda: functions.External)
    commands['cat'] = functions.Cat
    commands['echo'] = functions.Echo
    commands['wc'] = functions.Wc
    commands['pwd'] = functions.Pwd
    while True:
        cmd = input('>>')
        _parser = parser.Parser(global_namespace)
        _parser.parse(cmd)
        core = parser.Core(_parser, commands)
        core.evaluate_all()
        global_namespace = core.get_namespace()
