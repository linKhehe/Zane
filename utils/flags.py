class Flags:

    def __init__(self, *args):
        self.passed_flags = args

    @property
    def to_dict(self):
        ret = {"long flags": {}, "short flags": {}}
        for flag in self.passed_flags:
            assert isinstance(flag, str)
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
