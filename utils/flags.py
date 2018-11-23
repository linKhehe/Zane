def parse_flags(flags):
    ret = {}
    for flag in flags:
        if flag.startswith('--'):
            flag = flag.replace("--", "")
            if "=" in flag:
                ret.update({flag.split("=")[0]: flag.split("=")[1]})
            else:
                ret.update({flag: True})
        if flag.startswith('-'):
            flag = flag.replace("-", "")
            if "=" in flag:
                ret.update({flag.split("=")[0]: flag.split("=")[1]})
            else:
                ret.update({flag: True})
    return ret
