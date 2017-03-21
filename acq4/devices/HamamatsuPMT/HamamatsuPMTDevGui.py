from PyQt4 import QtGui, QtCore
from acq4.Manager import getManager, logExc, logMsg
from acq4.devices.HamamtsuPMT.hamamatsuPMTTemplate import Ui_HamamatsuForm
#from acq4.devices.Laser.devTemplate import Ui_Form
#from acq4.devices.Laser.LaserDevGui import LaserDevGui
#from maiTaiTemplate import Ui_MaiTaiStatusWidget
import numpy as np
from scipy import stats
from acq4.pyqtgraph.functions import siFormat
import time


class HamamatsuPMTDevGui(QtGui.QWidget):
    
    def __init__(self, dev):
        
        QtGui.QWidget.__init__(self)
        self.dev = dev
        #self.dev.devGui = self  ## make this gui accessible from LaserDevice, so device can change power values. NO, BAD FORM (device is not allowed to talk to guis, it can only send signals)
        self.ui = Ui_HamamatsuForm()
        self.ui.setupUi(self)
        
        if self.dev.isPMTOn():
            self.onOffToggled(True)
            #self.ui.turnOnOffBtn.setChecked(True)
            #if self.dev.getInternalShutter():
            #    self.internalShutterToggled(True)
            #    self._maitaiui.InternalShutterBtn.setChecked(True)
            #self._maitaiui.InternalShutterBtn.setEnabled(True)
        #else:
        #    self._maitaiui.InternalShutterBtn.setEnabled(False)
                
        #self.ui.MaiTaiGroup.hide()
        #self.ui.turnOnOffBtn.hide()
        
        #startWL = self.dev.getWavelength()
        #self._maitaiui.wavelengthSpin_2.setOpts(suffix='m', siPrefix=True, dec=False, step=5e-9)
        #self._maitaiui.wavelengthSpin_2.setValue(startWL)
        #self._maitaiui.wavelengthSpin_2.setOpts(bounds=self.dev.getWavelengthRange())
        #self._maitaiui.currentWaveLengthLabel.setText(siFormat(startWL, suffix='m'))
        
        
        #self._maitaiui.wavelengthSpin_2.valueChanged.connect(self.wavelengthSpinChanged)
        
        #self._maitaiui.turnOnOffBtn.toggled.connect(self.onOffToggled)
        #self._maitaiui.InternalShutterBtn.toggled.connect(self.internalShutterToggled)
        #self._maitaiui.ExternalShutterBtn.toggled.connect(self.externalShutterToggled)
        #self._maitaiui.externalSwitchBtn.toggled.connect(self.externalSwitchToggled)
        #self._maitaiui.linkLaserExtSwitchCheckBox.toggled.connect(self.linkLaserExtSwitch)
        #self._maitaiui.alignmentModeBtn.toggled.connect(self.alignmentModeToggled)


        self.dev.sigPMTGainChanged.connect(self.PMTGainChanged)
        self.dev.sigCoolerErrorOccurred.connect(self.coolerError)
        self.dev.sigOverloadErrorOccurred.connect(self.overloadError)
        
    def onOffToggled(self, b):
        if b:
            self.dev.switchPMTOn()
            self.ui.turnOnOffBtn.setText('Turn PMT Off')
            self.ui.turnOnOffBtn.setStyleSheet("QLabel {background-color: #C00}") 
        else:
            self.dev.switchPMTOff()
            self.ui.turnOnOffBtn.setText('Turn PMT On')
            self.ui.turnOnOffBtn.setStyleSheet("QLabel {background-color: None}")

    def PMTGainChanged(self,gain):
        if gain is None:
            self.ui.PMTGainLabel.setText("?")
        else:
            self.ui.PMTGainLabel.setText(siFormat(gain, suffix='V'))
            
    def coolerError(self):
        self.ui.CoolerStatusLabel.setText('Errror')
    
    def overloadError(self):
        self.ui.CoolerStatusLabel.setText('True')
    
      

            
        
       
        