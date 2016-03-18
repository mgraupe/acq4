#!/usr/bin/python
"""
Rebuild the Ui files
Note: If the system complains about not finding PyQt4 from pyuic, and you are using
anaconda, change the script in ~/anaconda/bin/pyuic4 to start with python2.7, not pythonw2.7
"""
import os, sys
uic = 'pyuic4'
sys.argv.pop(0)
if len(sys.argv) > 1 and sys.argv[1] == '--pyside':
    sys.argv.pop(0)
    uic = 'pyside-uic'

paths = sys.argv
if len(paths) == 0:
    paths = ['.']

uifiles = []
for root in paths:
    if os.path.isdir(root):
        for path, sd, files in os.walk(root):
            if os.path.join('acq4', 'pyqtgraph') in path:
                continue
            for f in files:
                if f.endswith('.ui'):
                    uifiles.append(os.path.join(path, f))
    elif os.path.isfile(root):
        if root.endswith('.ui'):
            uifiles.append(root)
        else:
            raise Exception('Not a .ui file: %s' % root)
    else:
        raise Exception('Not a file or directory: %s' % root)
    
for ui in uifiles:
    py = os.path.splitext(ui)[0] + '.py'
    if not os.path.exists(py) or os.stat(py).st_mtime < os.stat(ui).st_mtime:
        os.system('%s %s > %s' % (uic, ui, py))
        print py
