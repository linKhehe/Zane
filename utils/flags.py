import re


def parse_flags(flags):
    true = ['on', 'yes', 'y', 'true']
    false = ['off', 'no', 'n', 'false']
    _f = {}
    for flag in flags:
        find = re.findall(r"--?([^=\s]+)=?(\S+)?", flag)
        if not find or len(find) != 1:
            continue
        name, value = find[0]
        if not value:
            _f.setdefault(name, True)
        else:
            if value.isdigit():
                value = int(value)
            else:
                value = True if value.lower() in true else False if value.lower() in false else value
            _f.setdefault(name, value)
