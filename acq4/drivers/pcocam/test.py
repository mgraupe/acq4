import sys
sys.path.append('..\\..\\..\\')

import pcocam


pco = pcocam.PCODriverClass()
cam = pco.getCamera('pixelfly')
#cam.list_Params(params=None)
cam.close()

