def parse_flags(flags):
    ret = {"long flags": {}, "short flags": {}}
    for flag in flags:
        if flag.startswith('--'):
            flag = flag.replace("--", "")
            if "=" in flag:
                ret['long flags'].update({flag: flag.split("=")[1]})
            else:
                ret['long flags'].update({flag: True})
        if flag.startswith('-'):
            flag = flag.replace("-", "")
            if "=" in flag:
                ret['short flags'].update({flag: flag.split("=")[1]})
            else:
                ret['short flags'].update({flag: True})
    return ret
