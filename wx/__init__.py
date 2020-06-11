__path__ = __import__("pkgutil").extend_path(__path__, __name__)
import os
for p in __path__[1:]:
    if p[0] == '.':
        continue
    try:
        with open(os.path.join(p, "__init__" + os.extsep + "py")) as fp:
            exec(fp.read())
    except IOError:
        pass
    del fp
del p
del os
