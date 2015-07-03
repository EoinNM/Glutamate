__author__ = 'kanaan'

import string
valid_chars = '-_.() %s%s' %(string.ascii_letters, string.digits)


def mkdir_path(path):
    import os
    import errno
    import string
    import subprocess

    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
