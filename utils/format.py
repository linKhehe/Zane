import datetime

import humanize


def humanized_time_since(date: datetime.datetime)
    now = datetime.datetime.now()
    seconds_since = (now - date).total_seconds()

    ret = humanize.naturaltime(seconds_since)

    return ret

def humanized_date(date: datetime.datetime):
    return humanize.naturaldate(date)

