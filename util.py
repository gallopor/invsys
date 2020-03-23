import time
import datetime
from contextlib import contextmanager


def uniform_code(code, isindex=False):
    code = str(code).zfill(6)
    if isindex:
        return code
    else:
        if code[0] == '6':
            return code + '.SH'
        else:
            return code + '.SZ'


def utc2date(utc):
    dt_utc = datetime.datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%fZ')
    # return dt_utc.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d')
    return dt_utc.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)


def typetrans(val):
    if val is None:
        return None
    else:
        int(val)


# 检查代码消耗时间块
@contextmanager
def timing(title, name):
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print('%s,%s,%s' % (title, name, end - start))


