import sys
sys.path.append('..\\..\\..\\')

import pcocam


pco = pcocam.PCODriverClass()
cam = pco.getCamera('pixelfly')
cam.close()
