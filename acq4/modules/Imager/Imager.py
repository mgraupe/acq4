# -*- coding: utf-8 -*-
#
# Imager.py: A module for Acq4
# This module is meant to act as a "camera" using laser scanning
# to obtain images and store them in the same format as used by the
# Camera Module. Images are obtained by scanning a laser (usually
# Ti:Sapphire, but it could be something else), using the existing
# mirror calibrations, over a sample. The light is detected with
# a photomultiplier, amplified/filtered, and sampled with the A/D.
# 
# The Module offers the ability to select the region to be scanned
# using the existing camera image and an ROI, adjustment of the scan
# rate, pixel size (within reason), overscan, scanning mode (bidirectional
# versus sawtooth/flyback sweeps), and the ability to take videos
# single images, and timed images. 
# the image position is coordinated with the entire system, so that 
# later reconstructions can be performed against either the Camera or
# the laser scanned image. 
#
# 2012-2013 Paul B. Manis, Ph.D. and Luke Campagnola
# UNC Chapel Hill
# Distributed under MIT/X11 license. See license.txt for more infomation.
#
import time
import copy
import pprint
import os
from PyQt4 import QtGui, QtCore
import numpy as np
from collections import OrderedDict

from acq4.modules.Module import Module
import acq4.pyqtgraph as pg
import acq4.pyqtgraph.dockarea
import acq4.Manager as Manager
import acq4.util.InterfaceCombo as InterfaceCombo
from acq4.devices.Microscope import Microscope
from acq4.devices.Scanner.scan_program import ScanProgram
from acq4.devices.Scanner.scan_program.rect import RectScan
from acq4.modules.Camera import CameraModuleInterface
from acq4.pyqtgraph import parametertree as PT
from acq4.util import metaarray as MA
from acq4.util.Mutex import Mutex
from acq4.util import imaging
from acq4.util.Thread import Thread
from acq4.util.debug import printExc
from .imagerTemplate import Ui_Form


# Create some useful configurations for the user.
VideoModes = OrderedDict([
    ('1024x1', 
      OrderedDict([
        ('Scan Control', {
            'Sample Rate':900e3,
            'Average': 1,
            'Downsample': 1,
            'Image Width': 1024,
            'Image Height': 1024,
            'Overscan':400e-6,
            'Blank Screen': False,
            'Bidirectional': True,
         }),
        ('Image Control', {
            'Decomb': 169e-6,
         }),
       ])
    ),
    ('512x1', 
      OrderedDict([
        ('Scan Control', {
            'Sample Rate':450e3,
            'Average': 1,
            'Downsample': 1,
            'Image Width': 512,
            'Image Height': 512,
            'Overscan':400e-6,
            'Blank Screen': False,
            'Bidirectional': True,
         }),
        ('Image Control', {
            'Decomb': 170e-6,
         }),
       ])
    ),
    ('256x1', 
      OrderedDict([
        ('Scan Control', {
            'Sample Rate':224e3,
            'Average': 1,
            'Downsample': 1,
            'Image Width': 256,
            'Image Height': 256,
            'Overscan':300e-6,
            'Blank Screen': False,
            'Bidirectional': True,
         }),
        ('Image Control', {
            'Decomb': 170e-6, 
         }),
       ])
    ),
    ('128x1', 
      OrderedDict([
        ('Scan Control', {
            'Sample Rate':112e3,
            'Average': 1,
            'Downsample': 1,
            'Image Width': 128,
            'Image Height': 128,
            'Overscan':300e-6,
            'Blank Screen': False,
            'Bidirectional': True,
         }),
        ('Image Control', {
            'Decomb': 174e-6,
         }),
       ])
    ),
])

FrameModes = VideoModes



class ImagerWindow(QtGui.QMainWindow):
    """
    Create the window we will use for the Imager Module.
    This is only done this way so that we can catch the window
    close event (with "X").
    """
    def __init__(self, module):
        self.hasQuit = False
        self.module = module ## handle to the rest of the module class
   
        ## Create the main window
        win = QtGui.QMainWindow.__init__(self)
        return win
    
    def closeEvent(self, ev):
        self.module.quit()



class Black(QtGui.QWidget):
    """ make a black rectangle to fill screen when "blanking" 

    Also draws a Cancel button that emits sigCancelClicked when clicked."""

    sigCancelClicked = QtCore.Signal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.cancelRect = None
        self.cancelPressed = False

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        brush = pg.mkBrush(0.0)
        p.fillRect(self.rect(), brush)

        center = self.rect().center()
        r = QtCore.QPoint(70, 30)
        self.cancelRect = QtCore.QRect(center-r, center+r)
        p.setPen(pg.mkPen(150, 0, 0))
        f = p.font()
        f.setPointSize(18)
        p.setFont(f)
        if self.cancelPressed:
            p.fillRect(self.cancelRect, pg.mkBrush(80, 0, 0))
        p.drawRect(self.cancelRect)
        p.drawText(self.cancelRect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, "Cancel")
        p.end()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.cancelRect.contains(ev.pos()):
            ev.accept()
            self.cancelPressed = True
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            if self.cancelRect.contains(ev.pos()) and self.cancelPressed:
                self.sigCancelClicked.emit()
            self.cancelPressed = False
            self.update()

     

class ScreenBlanker(QtCore.QObject):
    """
    Cover all screens with black.
    This is so that extraneous light does not leak into the 
    detector during acquisition.
    """
    sigCancelClicked = QtCore.Signal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.cancelled = False
        self.widgets = []
        d = QtGui.QApplication.desktop()
        for i in range(d.screenCount()): # look for all screens
            w = Black()
            w.hide()
            w.sigCancelClicked.connect(self.cancelClicked)
            self.widgets.append(w)
            sg = d.screenGeometry(i) # get the screen size
            w.move(sg.x(), sg.y()) # put the widget there

    def blank(self):
        self.cancelled = False
        for w in self.widgets:
            w.showFullScreen()
            w.show()
        QtGui.QApplication.processEvents() # make it so

    def unblank(self):
        for w in self.widgets:
            w.hide()
        
    def __enter__(self):
        self.blank()
        return self

    def __exit__(self, *args):
        self.unblank()

    def cancelClicked(self):
        """Called when a cancel button is clicked.
        """
        self.cancelled = True
        self.unblank()
        self.sigCancelClicked.emit()

        
class RegionCtrl(pg.ROI):
    """
    Create an ROI "Region Control" with handles, with specified size
    and color. 
    Note: Setting the ROI position here is advised, but it seems
    that when adding the ROI to the camera window with the Qt call
    window().addItem, the position is lost, and will have to be
    reset in the ROI.
    """
    def __init__(self, pos, size, roiColor = 'r'):
        pg.ROI.__init__(self, pos, size=size, pen=roiColor)
        self.addScaleHandle([0,0], [1,1])
        self.addScaleHandle([1,1], [0,0])
        self.addScaleHandle([0,1], [1,0])
        self.addScaleHandle([1,0], [0,1])
        self.setZValue(1200)


class TileControl(pg.ROI):
    """
    Create an ROI for the Tile Regions. Note that the color is RED, 
    """    
    def __init__(self, pos, size, roiColor = 'r'):
        pg.ROI.__init__(self, pos, size=size, pen=roiColor)
        self.addScaleHandle([0,0], [1,1])
        self.addScaleHandle([1,1], [0,0])
        self.setZValue(1400)


class Imager(Module):
    def __init__(self, manager, name, config):
        Module.__init__(self, manager, name, config) 
        self.win = ImagerWindow(self) # make the main window - mostly to catch window close event...
        self.win.show()
        self.win.setWindowTitle('Multiphoton Imager V 1.01')

        self.w1 = QtGui.QSplitter() # divide l, r
        self.w1.setOrientation(QtCore.Qt.Horizontal)
        self.win.setCentralWidget(self.w1) # w1 is the "main window" splitter

        self.dockarea = pg.dockarea.DockArea()
        self.w1.addWidget(self.dockarea)

        self.w2s = QtGui.QWidget()
        self.w2sl = QtGui.QVBoxLayout()
        self.w2s.setLayout(self.w2sl)
        self.w2sl.setContentsMargins(0, 0, 0, 0)
        self.w2sl.setSpacing(0)
        self.ctrlWidget = QtGui.QWidget()
        self.ui = Ui_Form()
        self.ui.setupUi(self.ctrlWidget)  # put the ui on the top 
        self.w2sl.addWidget(self.ctrlWidget)

        # create the parameter tree for controlling device behavior
        self.tree = PT.ParameterTree()
        self.w2sl.addWidget(self.tree)

        # takes care of displaying image data, 
        # contrast & background subtraction user interfaces
        self.imagingCtrl = imaging.ImagingCtrl()
        self.frameDisplay = self.imagingCtrl.frameDisplay
        self.imageItem = self.frameDisplay.imageItem()

        # create docks for imaging, contrast, and background subtraction
        recDock = pg.dockarea.Dock(name="Acquisition Control", widget=self.imagingCtrl, size=(250, 10), autoOrientation=False)
        scanDock = pg.dockarea.Dock(name="Device Control", widget=self.w2s, size=(250, 800), autoOrientation=False)
        dispDock = pg.dockarea.Dock(name="Display Control", widget=self.frameDisplay.contrastWidget(), size=(250, 800), autoOrientation=False)
        bgDock = pg.dockarea.Dock(name="Background Subtraction", widget=self.frameDisplay.backgroundWidget(), size=(250, 10), autoOrientation=False)
        self.dockarea.addDock(recDock)
        self.dockarea.addDock(dispDock, 'right', recDock)
        self.dockarea.addDock(scanDock, 'bottom', recDock)
        self.dockarea.addDock(bgDock, 'bottom', dispDock)

        self.stateFile = os.path.join('modules', name+'_ui.cfg')
        uiState = Manager.getManager().readConfigFile(self.stateFile)
        if 'geometry' in uiState:
            geom = QtCore.QRect(*uiState['geometry'])
            self.win.setGeometry(geom)
        else:
            self.win.resize(500, 900)
        if 'window' in uiState:
            ws = QtCore.QByteArray.fromPercentEncoding(uiState['window'])
            self.win.restoreState(ws)
        

        # TODO: resurrect this for situations when the camera module can't be used
        # self.view = ImagerView()
        # self.w1.addWidget(self.view)   # add the view to the right of w1     

        self.blanker = ScreenBlanker()
        self.blanker.sigCancelClicked.connect(self.blankerCancelClicked)

        self.abort = False
        self.storedROI = None
        self.currentRoi = None
        self.ignoreRoiChange = False
        self.lastFrame = None
        self.scanVoltageCache = None  # cached scan protocol computed by generateScanProtocol
        
        self.objectiveROImap = {} # this is a dict that we will populate with the name
        # of the objective and the associated ROI object .
        # That way, each objective has a scan region appopriate for its magnification.

        # we assume that you are not going to change the current camera or scope while running
        # ... not just yet anyway.
        # if this is to be allowed on a system, the change must be signaled to this class,
        # and we need to pick up the device in a routine that handles the change.
        try:
            self.cameraModule = self.manager.getModule(config['cameraModule'])
        except:
            self.manager.loadDefinedModule(config['cameraModule'])
            pg.QtGui.QApplication.processEvents()
            self.cameraModule = self.manager.getModule(config['cameraModule'])
        self.laserDev = self.manager.getDevice(config['laser'])
        self.scannerDev = self.manager.getDevice(config['scanner'])

        self.imagingThread = ImagingThread(self.laserDev, self.scannerDev)
        self.imagingThread.sigNewFrame.connect(self.newFrame)
        self.imagingThread.sigVideoStopped.connect(self.videoStopped)
        self.imagingThread.sigAborted.connect(self.imagingAborted)

        # connect user interface to camera module
        self.camModInterface = ImagerCamModInterface(self, self.cameraModule)
        self.cameraModule.window().addInterface(self.name, self.camModInterface)
        
        
        # find first scope device that is parent of scanner
        dev = self.scannerDev
        while dev is not None and not isinstance(dev, Microscope):
            dev = dev.parentDevice()
        self.scopeDev = dev
        if dev is not None:
            self.scopeDev.sigObjectiveChanged.connect(self.objectiveUpdate)
            self.scopeDev.sigGlobalTransformChanged.connect(self.transformChanged)
        
        # config may specify a single detector device (dev, channel) or a list of devices 
        # to select from [(dev1, channel1), ...]
        self.detectors = config.get('detectors', [config.get('detector')])
        
        det = self.manager.getDevice(self.detectors[0][0])
        filt = det.getFilterDevice()
        if filt is not None:
            self.filterDevice =  self.manager.getDevice(filt)
        else:
            self.filterDevice = None
            
        if self.filterDevice is not None:
            self.filterDevice.sigFilterChanged.connect(self.filterUpdate)
        
        self.attenuatorDev = self.manager.getDevice(config['attenuator'][0])
        self.attenuatorChannel = config['attenuator'][1]
        
        self.laserMonitor = QtCore.QTimer()
        self.laserMonitor.timeout.connect(self.updateLaserInfo)
        self.laserMonitor.start(3000)
        
        self.frameDisplay.imageUpdated.connect(self.imageUpdated)
        self.imagingCtrl.sigAcquireFrameClicked.connect(self.acquireFrameClicked)
        self.imagingCtrl.sigStartVideoClicked.connect(self.startVideoClicked)
        self.imagingCtrl.sigStopVideoClicked.connect(self.stopVideoClicked)
        
        fS = config.get('defaultFieldSize', 63.0*120e-6)
        objScale = self.scannerDev.parentDevice().getObjective().scale().x()

        self.fieldSize = fS/objScale #63.0*120e-6 # field size for 63x, will be scaled for others
        
        # Add custom imaging modes
        for mode in FrameModes:
            self.imagingCtrl.addFrameButton(mode)
        for mode in VideoModes:
            self.imagingCtrl.addVideoButton(mode)

        #self.ui.cameraSnapBtn.clicked.connect(self.cameraSnap)
        self.ui.restoreROI.clicked.connect(self.restoreROI)
        self.ui.saveROI.clicked.connect(self.saveROI)
        self.ui.Align_to_Camera.clicked.connect(self.reAlign)
        self.ui.zoomSingleBox.valueChanged.connect(self.zoomRoi)
        self.ui.zoomTenthBox.valueChanged.connect(self.zoomRoi)
        
        self.singleFlip = False

        self.scanProgram = ScanProgram()
        self.scanProgram.addComponent('rect')

        self.param = PT.Parameter(name = 'param', children=[
            dict(name='Scan Control', type='group', children=[
                dict(name='Pockels', type='float', value=0.03, suffix='V', step=0.005, limits=[0, 1.5], siPrefix=True),
                dict(name='Sample Rate', type='int', value=450e3, suffix='Hz', dec=True, minStep=100., step=0.5, limits=[10e3, 50e6], siPrefix=True),
                dict(name='Downsample', type='int', value=1, limits=[1,None]),
                dict(name='Average', type='int', value=1, limits=[1,100]),
                dict(name='Blank Screen', type='bool', value=False),
                dict(name='Image Width', type='int', value=512, readonly=False, limits=[1, None]),
                dict(name='Image Height', type='int', value=512, readonly=False, limits=[1, None]),
                dict(name='Bidirectional', type='bool', value=True),
                dict(name='Overscan', type='float', value=400e-6, suffix='s', siPrefix=True, limits=[0, None], step=10e-6),
                dict(name='Photodetector', type='list', values=self.detectors),
                dict(name='Follow Stage', type='bool', value=True),
            ]),
            dict(name='Scan Properties', type='group', children=[
                dict(name='Frame Time', type='float', value=50e-3, suffix='s', siPrefix=True, readonly=True, dec=True, step=0.5, minStep=100e-6),
                dict(name='Pixel Size', type='float', value=1e-6, suffix='m', siPrefix=True, readonly=True),
                dict(name='Scan Speed', type='float', value=0.00, suffix='m/s', siPrefix=True, readonly=True),
                dict(name='Exposure per Frame', type='float', value=0.00, suffix='s/um^2', siPrefix=True, readonly=True),
                dict(name='Total Exposure', type='float', value=0.00, suffix='s/um^2', siPrefix=True, readonly=True),
                dict(name='Wavelength', type='float', value=700, suffix='nm', readonly=True),
                dict(name='Power', type='float', value=0.00, suffix='W', readonly=True),
                dict(name='Objective', type='str', value='Unknown', readonly=True),
                dict(name='Filter', type='str', value='Unknown', readonly=True),
            ]),
            dict(name='Image Control', type='group', children=[
                dict(name='Decomb', type='float', value=170e-6, suffix='s', siPrefix=True, bounds=[0, 1e-3], step=2e-7, decimals=5, children=[
                    dict(name='Auto', type='action'),
                    dict(name='Subpixel', type='bool', value=False),
                    ]),
                dict(name='Camera Module', type='interface', interfaceTypes=['cameraModule']),
            ]),
        ])
        self.tree.setParameters(self.param, showTop=False)

        # insert an ROI into the camera image that corresponds to our scan area                
        self.objectiveUpdate() # force update of objective information and create appropriate ROI
        self.filterUpdate()
        # check the devices...        
        self.updateParams() # also force update now to make sure all parameters are synchronized
        self.param.child('Scan Control').sigTreeStateChanged.connect(self.updateParams)
        self.param.child('Image Control').sigTreeStateChanged.connect(self.updateDecomb)
        self.param.child('Image Control', 'Decomb', 'Auto').sigActivated.connect(self.autoDecomb)

        self.manager.sigAbortAll.connect(self.abortTask)
        self.cameraModule.window().centerView()
        self.updateImagingProtocol()
        #<<<<<<< HEAD
        
        state = self.currentRoi.getState()
        self.defaultROIsize = state['size']

    def quit(self):
        self.abortTask()
        # if self.imageItem is not None and self.imageItem.scene() is not None:
        #     self.imageItem.scene().removeItem(self.imageItem)
        # for obj,item in self.objectiveROImap.items(): # remove the ROI's for all objectives.
        #     try:
        #         if item.scene() is not None:
        #             item.scene().removeItem(item)
        #     except:
        #         pass
        # if self.tileRoi is not None:
        #     if self.tileRoi.scene() is not None:
        #         self.tileRoi.scene().removeItem(self.tileRoi)
        #     self.tileRoi = None
        geom = self.win.geometry()
        uiState = {'window': str(self.win.saveState().toPercentEncoding()), 'geometry': [geom.x(), geom.y(), geom.width(), geom.height()]}
        Manager.getManager().writeConfigFile(uiState, self.stateFile)
        #=======

    def quit(self):
        self.abortTask()
        #>>>>>>> luke/camera-tracking
        self.camModInterface.quit()
        self.imagingCtrl.quit()
        self.imageItem = None
        Module.quit(self)

    def abortTask(self):
        """Immediately stop all acquisition and close any shutters in use.
        """
        if self.laserDev is not None and self.laserDev.hasShutter:
            self.laserDev.closeShutter()
        self.imagingThread.abort()

    def objectiveUpdate(self, reset=False):
        """ Update the objective information and the associated ROI
        Used to report that the objective has changed in the parameter tree,
        and then reposition the ROI that drives the image region.
        """
        self.param['Scan Properties', 'Objective'] = self.scopeDev.currentObjective.name()
        if reset:
            self.clearROIMap()
        if self.param['Scan Properties', 'Objective'] not in self.objectiveROImap: # add the objective and an ROI
            self.objectiveROImap[self.param['Scan Properties', 'Objective']] = self.createROI()
        for obj, roi in self.objectiveROImap.items():
            if obj == self.param['Scan Properties', 'Objective']:
                self.currentRoi = roi
                roi.show()
                self.roiChanged() # do this now as well so that the parameter tree is correct. 
            else:
                roi.hide()
    def filterUpdate(self, reset=False):
        """ Update the filter information
        Used to report that the filter has changed in the parameter tree,
        """
        if self.filterDevice is not None:
            self.param['Scan Properties', 'Filter'] = self.filterDevice.currentFilter.name()

    def clearROIMap(self):
        for k in self.objectiveROImap.keys():
            roi = self.objectiveROImap[k]
            if roi.scene() is not None:
                roi.scene().removeItem(roi)
        self.objectiveROImap = {}
    
    def transformChanged(self):
        """
        Report that the tranform has changed, which might include the objective, or
        perhaps the stage position, etc. This needs to be obtained to re-align
        the scanner ROI
        """
        prof = pg.debug.Profiler()
        globalTr = self.scannerDev.globalTransform()
        pt1 = globalTr.map(self.currentRoi.scannerCoords[0])
        pt2 = globalTr.map(self.currentRoi.scannerCoords[1])
        diff = pt2 - pt1
        pg.disconnect(self.currentRoi.sigRegionChangeFinished, self.roiChanged)
        try:
            self.currentRoi.setState({'pos': pt1, 'size': diff, 'angle': 0})
        finally:
            self.currentRoi.sigRegionChangeFinished.connect(self.roiChanged)
        self.setScanPosFromRoi()
        self.camModInterface.deviceTransformChanged(pg.SRTTransform3D(globalTr).as2D())
        if self.imagingThread.isRunning():
            self.updateImagingProtocol()

    def getObjectiveColor(self, objective):
        """
        for the current objective, parse a color or use a default. This is a kludge. 
        """
        color = QtGui.QColor("red")
        id = objective.key()[1]
        if id == u'63x0.9':
            color = QtGui.QColor("darkBlue")
        elif id == u'40x0.8':
            color = QtGui.QColor("blue")
        elif id == u'40x0.75':
            color = QtGui.QColor("blue")
        elif id == u'5x0.25':
            color = QtGui.QColor("red")
        elif id == u'4x0.1':
            color = QtGui.QColor("darkRed")
        else:
            color = QtGui.QColor("lightGray")
        return(color)
            
    def createROI(self, roiColor='r'):
        # the initial ROI will be nearly as big as the field, and centered.
        cpos = self.scannerDev.mapToGlobal((0,0)) # get center position in scanner coordinates
        csize = self.scannerDev.mapToGlobal((self.fieldSize, self.fieldSize))
        objScale = self.scannerDev.parentDevice().getObjective().scale().x()
        height = width = self.fieldSize*objScale
        
        csize = pg.Point(width, height)
        cpos = cpos - csize/2.
        
        roiColor = self.getObjectiveColor(self.scopeDev.currentObjective) # pick up an objective color...
        roi = RegionCtrl(cpos, csize, roiColor) # Note that the position actually gets over ridden by the camera additem below..
        self.cameraModule.window().addItem(roi)
        roi.setPos(cpos)
        roi.sigRegionChangeFinished.connect(self.roiChanged)
        return roi
    
    def restoreROI(self):
        if self.storedROI is not None:
            (width, height, x, y) = self.storedROI
            self.currentRoi.setSize([width, height])
            self.currentRoi.setPos([x, y])
            self.roiChanged()
        else:
            cpos = self.cameraModule.ui.view.viewRect().center() # center position, stage coordinates
            csize = pg.Point([x*400 for x in self.cameraModule.ui.view.viewPixelSize()])
            width  = csize[0]*2 # width is x in M
            height = csize[1]*2
            csize = pg.Point(width, height)
            cpos = cpos - csize/2.
            self.currentRoi.setSize([width, height])
            self.currentRoi.setPos(cpos)
            
    def saveROI(self):
        state = self.currentRoi.getState()
        (width, height) = state['size']
        x, y = state['pos']
        self.storedROI = [width, height, x, y]
        
    def roiChanged(self):
        """ read the ROI rectangle width and height and repost
        in the parameter tree """
        if self.ignoreRoiChange:
            return

        self.scanVoltageCache = None  # invalidate cache

        # update scan position
        self.setScanPosFromRoi()

        # update scan shape if needed
        roi = self.currentRoi
        state = roi.getState()
        w, h = state['size']
        rparam = self.scanProgram.components[0].ctrlParameter()
        param = self.param.child('Scan Control')
        self.updateParams()
        rows = int(param['Image Width'] * h / w)
        if param['Image Height'] != rows:
            # update image height; this will cause acq thread protocol to be updated
            with param.treeChangeBlocker():
                param['Image Height'] = rows
        else:
            # ..otherwise we need to request the update here.
            if self.imagingThread.isRunning():
                self.updateImagingProtocol()

        # record position of ROI in Scanner's local coordinate system
        # we can use this later to allow the ROI to track stage movement
        tr = self.scannerDev.inverseGlobalTransform() # maps from global to device local
        pt1 = pg.Point(*state['pos'])
        pt2 = pt1 + pg.Point(*state['size'])
        self.currentRoi.scannerCoords = [
            tr.map(pt1),
            tr.map(pt2),
            ]

    def setScanPosFromRoi(self):
        # Update the position of the scan rectangle from the ROI
        roi = self.currentRoi
        w, h = roi.size()
        
        # get top-left ROI corner in global coordinates
        p0 = roi.mapToView(pg.Point(0,h))
        if p0 is None:
            # could not map point; probably view has been closed.
            return 

        rparam = self.scanProgram.components[0].ctrlParameter()
        rparam.system.p0 = pg.Point(p0)  # top-left
        rparam.system.p1 = pg.Point(roi.mapToView(pg.Point(w,h)))  # rop-right

    def reAlign(self):
        self.objectiveUpdate(reset=True) # try this... 
        self.ui.zoomSingleBox.setValue(0)
        self.ui.zoomTenthBox.setValue(0)
        self.roiChanged()
        #<<<<<<< HEAD
        self.cameraModule.window().centerView()
        
    def zoomRoi(self):
        zoomS = self.ui.zoomSingleBox.value()
        if self.singleFlip:
            self.singleFlip = False
            self.ui.zoomSingleBox.setValue((zoomS+1))
        zoomT = self.ui.zoomTenthBox.value()
        if zoomT == 10:
            self.singleFlip=True
            self.ui.zoomTenthBox.setValue(0)
        zoom = zoomS + zoomT/10.
        state = self.currentRoi.getState()
        cpos = state['pos'] +  state['size']/2. #self.scannerDev.mapToGlobal((0,0)) # get center position in scanner coordinates
        width  = self.defaultROIsize[0]/zoom # width is x in M
        height = self.defaultROIsize[1]/zoom
        csize = pg.Point(width, height)
        cpos = cpos - csize/2.
        self.currentRoi.setSize([width, height])
        self.currentRoi.setPos(cpos)
        #self.roiChanged()
        self.cameraModule.window().centerView(exclusive='Imager')
    # def setTilesROI(self, roiColor = 'r'):
    #     # the initial ROI will be larger than the current field and centered.
    #     if self.tileRoi is not None and self.tileRoiVisible:
    #         self.hideROI(self.tileRoi)
    #         self.tileRoiVisible = False
    #         if self.tileRoi is not None:
    #             return
           
            
    #     state = self.currentRoi.getState()
    #     width, height = state['size']
    #     x, y = state['pos']
        
    #     csize= [width*3.0,  height*3.0]
    #     cpos = [x, y]
    #     self.tileRoi = RegionCtrl(cpos, csize, [255., 0., 0.]) # Note that the position actually gets overridden by the camera additem below..
    #     self.tileRoi.setZValue(11000)
    #     self.cameraModule.window().addItem(self.tileRoi)
    #     self.tileRoi.setPos(cpos)
    #     self.tileRoi.sigRegionChangeFinished.connect(self.tileROIChanged)
    #     self.tileRoiVisible = True
    #     return self.tileRoi
        
    # def tileROIChanged(self):
    #     """ read the TILE ROI rectangle width and height and repost
    #     in the parameter tree """
    #     state = self.tileRoi.getState()
    #     self.tileWidth, self.tileHeight = state['size']
    #     self.tilexPos, self.tileyPos = state['pos']
    #     x0, y0 =  self.tileRoi.pos()
    #     x0 = x0 - self.xPos # align against currrent 2p Image lower left corner
    #     y0 = y0 - self.yPos
    #     self.param['Tiles', 'X0'] = x0 * 1e6
    #     self.param['Tiles', 'Y0'] = y0 * 1e6
    #     self.param['Tiles', 'X1'] = self.tileWidth * 1e6
    #     self.param['Tiles', 'Y1'] = self.tileHeight * 1e6
    #     # record position of ROI in Scanner's local coordinate system
    #     # we can use this later to allow the ROI to track stage movement
    #     tr = self.scannerDev.inverseGlobalTransform() # maps from global to device local
    #     pt1 = pg.Point(self.tilexPos, self.tileyPos)
    #     pt2 = pg.Point(self.tilexPos+self.tileWidth, self.tileyPos+self.tileHeight)
    #     self.tileRoi.scannerCoords = [
    #         tr.map(pt1),
    #         tr.map(pt2),
    #         ]


    def updateParams(self, root=None, changes=()):
        """Parameters have changed; update any dependent parameters and the scan program.
        """
        #check the devices first        
        # use the presets if they are engaged
        # preset = self.param['Preset']
        # self.loadPreset(preset)

        scanControl = self.param.child('Scan Control')

        self.scanVoltageCache = None  # invalidate cache

        sampleRate = scanControl['Sample Rate']
        downsample = scanControl['Downsample']
        # we'll let the rect tell us later how many samples are needed
        self.scanProgram.setSampling(rate=sampleRate, samples=0, downsample=downsample)
        self.scanProgram.setDevices(scanner=self.scannerDev, laser=self.laserDev)

        rect = self.scanProgram.components[0]
        rparams = rect.ctrlParameter()

        for param, change, args in changes:
            if change == 'value' and param is scanControl.child('Image Height'):
                # user explicitly requested image height; change ROI to match.
                try:
                    self.ignoreRoiChange = True
                    w, h = self.currentRoi.size()
                    h2 = w * scanControl['Image Height'] / scanControl['Image Width']
                    self.currentRoi.setSize([w, h2])
                    pos = self.currentRoi.pos()
                    self.currentRoi.setPos([pos[0], pos[1] + h - h2])
                finally:
                    self.ignoreRoiChange = False

        rparams['imageRows'] = scanControl['Image Height']
        rparams['imageRows', 'fixed'] = True
        rparams['imageCols'] = scanControl['Image Width']
        rparams['imageCols', 'fixed'] = True
        rparams['minOverscan'] = scanControl['Overscan']
        rparams['bidirectional'] = True
        rparams['pixelAspectRatio'] = 1.0
        rparams['pixelAspectRatio', 'fixed'] = True
        rparams['numFrames'] = scanControl['Average']
        rparams['numFrames', 'fixed'] = True

        rparams.system.solve()
        nSamples = rparams.system.scanStride[0] * rparams.system.numFrames
        nSamples += int(sampleRate * 200e-6)  # generate some padding for decomb
        self.scanProgram.setSampling(rate=sampleRate, samples=nSamples, downsample=downsample)

        # Update dependent parameters
        scanProp = self.param.child('Scan Properties')
        scanProp['Pixel Size'] = rparams.system.pixelWidth
        scanProp['Frame Time'] = rparams.system.frameDuration

        scanProp['Scan Speed'] = rparams.system.scanSpeed
        scanProp['Exposure per Frame'] = rparams.system.frameExposure
        scanProp['Total Exposure'] = rparams.system.totalExposure

        if rparams.system.checkOverconstraint() is not False:
            raise RuntimeError("Scan calculator is overconstrained (this is a bug).")

        # send new protocol to acq thread if it is running
        if self.imagingThread.isRunning():
            self.updateImagingProtocol()

    def updateImagingProtocol(self):
        # send new protocol to acq thread
        protocol = self.generateProtocol()
        metainfo = self.saveParams()
        system = self.scanProgram.components[0].ctrlParameter().system
        system.solve()
        self.imagingThread.setProtocol(protocol, metainfo, system.copy())

    def updateDecomb(self):
        if self.lastFrame is not None:
            self.lastFrame.setDecomb(self.param['Image Control', 'Decomb'], self.param['Image Control', 'Decomb', 'Subpixel'])
            self.frameDisplay.updateFrame()

    def autoDecomb(self):
        if self.lastFrame is not None:
            self.lastFrame.autoDecomb()
            self.param.child('Image Control', 'Decomb').setValue(self.lastFrame._decomb[0])
            
    def loadModeSettings(self, params, controlType):
        param = self.param.child(controlType)
        with param.treeChangeBlocker():  # accumulate changes, emit once at the end.
            for name, val in params[controlType].items():
                param[name] = val

    def acquireFrameClicked(self, mode):
        """User requested acquisition of a single frame.
        """
        if self.imagingThread.isRunning():
            self.imagingThread.stopVideo()
            self.imagingThread.wait()

        if mode is not None:
            self.loadModeSettings(FrameModes[mode],'Image Control')
            self.loadModeSettings(FrameModes[mode],'Scan Control')
        self.updateImagingProtocol()
        self.takeImage()
        #self.updateDecomb()
        
    def startVideoClicked(self, mode):
        if mode is not None:
            self.loadModeSettings(VideoModes[mode],'Image Control')
            self.loadModeSettings(VideoModes[mode],'Scan Control')
        #self.updateDecomb()
        self.updateImagingProtocol()
        self.imagingCtrl.acquisitionStarted()
        self.imagingThread.startVideo()

    def stopVideoClicked(self):
        self.imagingThread.stopVideo()

    def isRunning(self):
        return self.imagingThread.isRunning()

    def videoStopped(self):
        self.imagingCtrl.acquisitionStopped()

    def imagingAborted(self):
        self.blanker.unblank()

    def blankerCancelClicked(self):
        self.imagingThread.abort()

    def saveParams(self, root=None):
        params = {}
        for grp in ('Scan Control', 'Scan Properties'):
            for ch in self.param.child(grp):
                params[ch.name()] = ch.value()

        return params

    def updateLaserInfo(self):
        if self.laserDev is not None:
            self.param['Scan Properties', 'Wavelength'] = (self.laserDev.getWavelength()*1e9)
            self.param['Scan Properties', 'Power'] = (self.laserDev.outputPower())
        else:
            self.param['Scan Properties', 'Wavelength'] = 0.0
            self.param['Scan Properties', 'Power'] = 0.0

    def openShutter(self, open):
        if self.laserDev is not None and self.laserDev.hasShutter:
            if open:
                self.laserDev.openShutter()
            else:
                self.laserDev.closeShutter()

    def getFocusDepth(self):
        return self.scannerDev.getFocusDepth()

    def setFocusDepth(self, depth):
        return self.scannerDev.setFocusDepth(depth)

    def setFocusHolding(self, hold):
        dev = self.scannerDev.getFocusDevice()
        if hasattr(dev, 'setHolding'):
            dev.setHolding(hold)
        
    def takeImage(self, allowBlanking=True):
        """
        Take an image using the scanning system and PMT, and return with the data.
        """
        # Blank screen and start acquisition
        blank = allowBlanking and self.param['Scan Control', 'Blank Screen'] is True
        if blank:
            self.blanker.blank()

        try:
            self.imagingThread.takeFrame()
        except Exception:
            self.blanker.unblank()

    def newFrame(self, frame):
        """Acquisition thread has generated a new frame.
        """
        self.blanker.unblank()
        self.lastFrame = frame
        self.updateDecomb()
        self.imagingCtrl.newFrame(self.lastFrame)

    def generateProtocol(self):
        # first make sure laser information is updated on the module interface
        self.updateLaserInfo()

        # return cached command if possible
        if self.scanVoltageCache is not None:
            vscan = self.scanVoltageCache
        else:
            # Generate scan voltages
            vscan = self.scanProgram.generateVoltageArray()
            # scanner lags laser too much to make this worthwhile without some timing correction
            # mask = self.scanProgram.generateLaserMask().astype(np.float32)
            self.scanVoltageCache = vscan

        # sample rate, duration, and other meta data
        rect = self.scanProgram.components[0].ctrlParameter()

        scanParams = self.param.child('Scan Control')
        samples = vscan.shape[0]
        sampleRate = scanParams['Sample Rate']
        duration = float(samples) / sampleRate
        program = self.scanProgram.saveState()  # meta-data to annotate protocol

        pcell = np.empty(vscan.shape[0], dtype=np.float64)  # DAQmx requires float64!
        pcell[:] = scanParams['Pockels']
        pcell[-1] = 0

        # Look up device names
        pdDevice, pdChannel = scanParams['Photodetector']
        scanDev = self.scannerDev.name()

        prot = {
            'protocol': {
                'duration': duration,
                },
            'DAQ' : {
                'rate': sampleRate, 
                'numPts': samples,
                'downsample': scanParams['Downsample']
                }, 
            scanDev: {
                'xCommand' : vscan[:, 0],
                'yCommand' : vscan[:, 1],
                'program': program, 
                },
            self.laserDev.name(): {
                'pCell': {'command': pcell},
                'shutterMode': 'open',
                },
            pdDevice: {
                pdChannel: {'record': True},
            },
        }

        return prot

    def imageUpdated(self, frame):
        ## New image is displayed; update image transform
        self.imageItem.setTransform(frame.globalTransform().as2D())

        #<<<<<<< HEAD
    def getBoundary(self):
        """
        Return bounding rect of this imaging device in global coordinates
        """
        globalCoords=False #True
        #print slf.fieldSize
        state = self.currentRoi.getState()
        cpos = state['pos']
        csize = state['size']
        
        objScale = self.scannerDev.parentDevice().getObjective().scale().x()
        
        cpos  = tuple(i/1. for i in cpos)
        csize = tuple(j/1. for j in csize)
        
        bounds = QtGui.QPainterPath()
        bounds.addRect(QtCore.QRectF(cpos[0], cpos[1], *csize))
        if globalCoords:
            return (pg.SRTTransform(self.scannerDev.globalTransform()).map(bounds))
        else:
            return bounds


    # def PMT_Run(self):
    #     """
    #     This routine handles special cases where we want multiple frames to be
    #     automatically collected. The 3 modes implemented are:
    #     Z-stack (currently not used as the stage isn't good enough...)
    #     Tiles - collect a tiled x-y sequence of images as single images.
    #     Timed - collect a series of images as a 2p-stack. 
    #     The parameters for each are set in the paramtree, and the
    #     data collection is initiated with the "Run" button and
    #     can be terminated early with the "stop" button.
    #     """
        
    #     info = {}
    #     frameInfo = None  # will be filled in by takeImage()
    #     self.stopFlag = False
    #     if (self.param['Z-Stack'] and self.param['Timed']) or (self.param['Z-Stack'] and self.param['Tiles']) or self.param['Timed'] and self.param['Tiles']:
    #         return # only one mode at a time... 
    #     self.view.resetFrameCount() # always reset the ROI display in the imager window (different than in camera window) if it is being used
        
    #     if self.param['Z-Stack']: # moving in z for a focus stack
    #         imageFilename = '2pZstack'
    #         info['2pImageType'] = 'Z-Stack'
    #         stage = self.manager.getDevice(self.param['Z-Stack', 'Stage'])
    #         images = []
    #         nSteps = self.param['Z-Stack', 'Steps']
    #         for i in range(nSteps):
    #             img, frameInfo = self.takeImage()
    #             img = img[np.newaxis, ...]
    #             if img is None:
    #                 break
    #             images.append(img)
    #             self.view.setImage(img)
                
    #             if i < nSteps-1:
    #                 ## speed 20 is quite slow; timeouts may occur if we go much slower than that..
    #                 stage.moveBy([0.0, 0.0, self.param['Z-Stack', 'Step Size']], speed=20, block=True)  
    #         imgData = np.concatenate(images, axis=0)
    #         info.update(frameInfo)
    #         if self.param['Store']:
    #             dh = self.manager.getCurrentDir().writeFile(imgData, imageFilename + '.ma', info=info, autoIncrement=True)
        
    #     elif self.param['Tiles']: # moving in x and y to get a tiled image set
    #         info['2pImageType'] = 'Tiles'
    #         dirhandle = self.manager.getCurrentDir()
    #         if self.param['Store']:
    #             dirhandle = dirhandle.mkdir('2PTiles', autoIncrement=True, info=info)
    #         imageFilename = '2pImage'
            
    #         stage = self.manager.getDevice(self.param['Tiles', 'Stage'])
    #         #print dir(stage.mp285)
    #         #print stage.mp285.stat()
    #         #return
    #         self.param['Timed', 'Current Frame'] = 0 # get frame times ...
    #         images = []
    #         originalPos = stage.pos
    #         state = self.currentRoi.getState()
    #         self.width, self.height = state['size']
    #         originalSpeed = 200
    #         mp285speed = 1000

    #         x0 = self.param['Tiles', 'X0'] *1e-6 # convert back to meters
    #         x1 = x0 + self.param['Tiles', 'X1'] *1e-6
    #         y0 = self.param['Tiles', 'Y0'] *1e-6
    #         y1 = y0 + self.param['Tiles', 'Y1'] *1e-6
    #         tileXY = self.param['Tiles', 'StepSize']*1e-6
    #         nXTiles = np.ceil((x1-x0)/tileXY)
    #         nYTiles = np.ceil((y1-y0)/tileXY)
           
    #         # positions are relative......
    #         xpos = np.arange(x0, x0+nXTiles*tileXY, tileXY) +originalPos[0]
    #         ypos = np.arange(y0, y0+nYTiles*tileXY, tileXY) +originalPos[1]
    #         stage.moveTo([xpos[0], ypos[0]],
    #                      speed=mp285speed, fine = True, block=True) # move and wait until complete.  

    #         ypath = 0
    #         xdir = 1 # positive movement direction (serpentine tracking)
    #         xpos1 = xpos
    #         for yp in ypos:
    #             if self.stopFlag:
    #                 break
    #             for xp in xpos1:
    #                 if self.stopFlag:
    #                     break
    #                 stage.moveTo([xp, yp], speed=mp285speed, fine = True, block=True, timeout = 10.)
    #                 (images, frameInfo) = self.PMT_Snap(dirhandle = dirhandle) # now take image
    #                 #  stage.moveBy([tileXY*xdir, 0.], speed=mp285speed, fine = True, block=True, timeout = 10.)
    #             xdir *= -1 # reverse direction
    #             if xdir < 0:
    #                 xpos1 = xpos[::-1] # reverse order of array, serpentine movement.
    #             else:
    #                 xpos1 = xpos
    #         stage.moveTo([xpos[0], ypos[0]],
    #                      speed=originalSpeed, fine = True, block=True, timeout = 30.) # move and wait until complete.  

    #     elif self.param['Timed']: # 
    #         imageFilename = '2pTimed'
    #         info['2pImageType'] = 'Timed'
    #         self.param['Timed', 'Current Frame'] = 0
    #         images = []
    #         nSteps = self.param['Timed', 'N Intervals']
    #         for i in range(nSteps):
    #             if self.stopFlag:
    #                 break
    #             self.param['Timed', 'Current Frame'] = i
    #             (img, frameInfo) = self.takeImage()
    #             img = img[np.newaxis, ...]
    #             if img is None:
    #                return
    #             images.append(img)
    #             self.view.setImage(img)
    #             if self.stopFlag:
    #                 break
                
    #             if i < nSteps-1:
    #                 time.sleep(self.param['Timed', 'Interval'])
    #         imgData = np.concatenate(images, axis=0)
    #         info.update(frameInfo)
    #         if self.param['Store']:
    #             dh = self.manager.getCurrentDir().writeFile(imgData, imageFilename + '.ma', info=info, autoIncrement=True)

    #     else:
    #         imageFilename = '2pImage'
    #         info['2pImageType'] = 'Snap'
    #         (imgData, frameInfo) = self.takeImage()
    #         if imgData is None:
    #             return
    #         self.view.setImage(imgData)
    #         info.update(frameInfo)
    #         if self.param['Store']:
    #             dh = self.manager.getCurrentDir().writeFile(imgData, imageFilename + '.ma', info=info, autoIncrement=True)

    # def PMT_Stop(self):
    #     self.stopFlag = True



class ImagerCamModInterface(CameraModuleInterface):
    """For plugging in the 2p imager system to the camera module.
    """
    def __init__(self, imager, mod):
        self.imager = imager

        CameraModuleInterface.__init__(self, imager, mod)

        mod.window().addItem(imager.imageItem, z=10)

        self.imager.imagingThread.sigNewFrame.connect(self.newFrame)

    def graphicsItems(self):
        gitems = [self.getImageItem()] + list(self.imager.objectiveROImap.values())
        print 'gitems', gitems
        return gitems

    def takeImage(self, closeShutter=True):
        self.imager.imagingThread.takeFrame(closeShutter=closeShutter)

    def getImageItem(self):
        return self.imager.imageItem

    def newFrame(self, frame):
        self.sigNewFrame.emit(self, frame)
    
    def boundingRect(self):
        """
        Return bounding rect of this imaging device in global coordinates
        """
        return self.imager.getBoundary().boundingRect()

    def isRunning(self):
        return self.imager.isRunning()


class ImagingFrame(imaging.Frame):
    """Represents a single collected image frame and its associated metadata."""

    def __init__(self, data, rectscan, info):
        self.lock = Mutex(recursive=True)  # because frame may be accesed by recording thread.
        self._rectscan = rectscan
        self._decomb = (0, False)
        self._image = None
        imaging.Frame.__init__(self, data, info)

    @property
    def rectScan(self):
        return self._rectscan

    def getImage(self, decomb=True, offset=None):
        if self._image is None:
            offset, subpixel = self._decomb
            img = self.rectScan.extractImage(self._data, offset=offset, subpixel=subpixel)
            # note we transpose the image here because pg prefers (col, row) order.
            self._image = img.mean(axis=0).T

        return self._image

    def setDecomb(self, offset, subpixel):
        d = (offset, subpixel)
        if self._decomb != d:
            self._decomb = d
            self._image = None

    def autoDecomb(self):
        offset, subpixel = self._decomb
        offset = self.rectScan.measureMirrorLag(self._data, subpixel=subpixel)
        self.setDecomb(offset, subpixel)


class ImagingThread(Thread):

    sigNewFrame = QtCore.Signal(object)
    sigVideoStopped = QtCore.Signal()
    sigAborted = QtCore.Signal()

    def __init__(self, laserDev, scannerDev):
        Thread.__init__(self)
        self._abort = False
        self._video = True
        self._closeShutter = True  # whether to close shutter at end of acquisition
        self.lock = Mutex(recursive=True)
        self.manager = acq4.Manager.getManager()
        self.laserDev = laserDev
        self.scannerDev = scannerDev

    def setProtocol(self, prot, meta, sys):
        #  prot = task protocol 
        #  meta = output of saveParams to be stored with image
        #  sys = rectscan system for extracting image from pmt data
        with self.lock:
            self.protocol = prot
            self.metainfo = meta
            self.system = sys

    def abort(self):
        with self.lock:
            self._abort = True

    def startVideo(self):
        with self.lock:
            self._abort = False
            self._video = True
            self._closeShutter = True
        if not self.isRunning():
            self.start()

    def stopVideo(self):
        with self.lock:
            self._video = False

    def takeFrame(self, closeShutter=True):
        with self.lock:
            self._abort = False
            self._video = False
            self._closeShutter = closeShutter
        if self.isRunning():
            self.wait()
        self.start()

    def run(self):
        try:
            with self.lock:
                videoRequested = self._video
                closeShutter = self._closeShutter
            if (videoRequested or not closeShutter) and self.laserDev is not None and self.laserDev.hasShutter:
                # force shutter to stay open for the duration of the acquisition
                self.laserDev.openShutter()

            while True:
                # take one frame
                self.acquireFrame(allowBlanking=False)

                # See whether acquisition should end
                with self.lock:
                    video, abort = self._video, self._abort
                if video is False:
                    break
                if abort is True:
                    raise Exception("Imaging acquisition aborted")
        except Exception:
            self.sigAborted.emit()
            printExc("Error in imaging acquisition thread.")
        finally:
            if videoRequested:
                self.sigVideoStopped.emit()
            if closeShutter and self.laserDev is not None and self.laserDev.hasShutter:
                self.laserDev.closeShutter()

    def acquireFrame(self, allowBlanking=True):
        """Acquire one frame and emit sigNewFrame.
        """
        with self.lock:
            prot = self.protocol
            meta = self.metainfo
            rectSystem = self.system

        # Need to build task from a deep copy of the protocol because 
        # it will be modified after execution.
        task = self.manager.createTask(copy.deepcopy(prot))
        
        dur = prot['protocol']['duration']
        start = pg.ptime.time()
        endtime = start + dur - 0.005 

        # Start the task
        task.execute(block = False)

        # Wait until the task has finished
        while not task.isDone():
            with self.lock:
                abort = self._abort
            if abort:
                task.abort()
                self._abort = False
                raise Exception("Imaging acquisition aborted")
            now = pg.ptime.time()
            if now < endtime:
                # long sleep until we expect the protocol to be almost done
                time.sleep(min(0.1, endtime-now))
            else:
                time.sleep(5e-3)

        # Get acquired data and generate metadata
        data = task.getResult()
        pdDevice, pdChannel = meta['Photodetector']
        pmtData = data[pdDevice][pdChannel].view(np.ndarray)
        info = meta.copy()
        info['time'] = start

        info['deviceTranform'] = pg.SRTTransform3D(self.scannerDev.globalTransform())
        tr = rectSystem.imageTransform()
        info['transform'] = pg.SRTTransform3D(tr)

        frame = ImagingFrame(pmtData, rectSystem.copy(), info)
        self.sigNewFrame.emit(frame)
