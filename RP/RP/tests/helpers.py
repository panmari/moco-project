import os.path

def relative(p):
    return os.path.join(os.path.dirname(__file__), p)
