from PyQt4 import QtGui, QtCore
from acq4.Manager import getManager, logExc, logMsg
from hamamatsuPMTTemplate import Ui_HamamatsuForm
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
        self.ui = Ui_HamamatsuForm()
        self.ui.setupUi(self)
        
        if self.dev.isPeltierOn():
            self.PeltierOnOffToggled(True)
        else:
            self.ui.turnHVOnOffBtn.setEnabled(False)
        
        if self.dev.isHVOn():
            self.PeltierOnOffToggled(True)
            self.HVOnOffToggled(True)
            
            
        #self.ui.gainSpin.setOpts(suffix='V', siPrefix=True, dec=False, step=0.02)
        #self.ui.gainSpin.setValue(self.dev.currentSetGain)
        #self.ui.gainSpin.setOpts(bounds=(0,0.9))
        
        self.ui.turnPeltierOnOffBtn.toggled.connect(self.PeltierOnOffToggled)
        self.ui.turnHVOnOffBtn.toggled.connect(self.HVOnOffToggled)
        
        self.dev.sigPMTGainChanged.connect(self.PMTGainChanged)
        self.dev.sigCoolerErrorOccurred.connect(self.coolerError)
        self.dev.sigOverloadErrorOccurred.connect(self.overloadError)
        self.dev.sigPeltierStatus.connect(self.peltierStatus)
        self.dev.sigPMTPower.connect(self.pmtPower)
        #self.ui.gainSpin.valueChanged.connect(self.gainSpinChanged)
        
    def PeltierOnOffToggled(self, b):
        if b:
            self.dev.activatePeltier()
            self.ui.turnPeltierOnOffBtn.setText('Turn Peltier Off')
            self.ui.turnPeltierOnOffBtn.setStyleSheet("QLabel {background-color: #C00}") 
            self.ui.turnHVOnOffBtn.setEnabled(True)
        else:
            if self.dev.isHVOn:
                self.HVOnOffToggled(False)
                self.ui.turnHVOnOffBtn.setChecked(False)
            self.ui.turnHVOnOffBtn.setEnabled(False)    
            self.dev.deactivatePeltier()
            self.ui.turnPeltierOnOffBtn.setText('Turn Peltier On')
            self.ui.turnPeltierOnOffBtn.setStyleSheet("QLabel {background-color: None}")
    
    def HVOnOffToggled(self, b):
        if b:
            self.dev.activateHV()
            self.ui.turnHVOnOffBtn.setText('Turn High Voltage Off')
            self.ui.turnHVOnOffBtn.setStyleSheet("QLabel {background-color: #C00}") 
        else:
            self.dev.deactivateHV()
            self.ui.turnHVOnOffBtn.setText('Turn High Voltage On')
            self.ui.turnHVOnOffBtn.setStyleSheet("QLabel {background-color: None}")
        
    def PMTGainChanged(self,gain):
        if gain is None:
            self.ui.PMTGainLabel.setText("?")
        else:
            self.ui.PMTGainLabel.setText(siFormat(gain, suffix='V'))
            
    def coolerError(self,coolerError):
        if coolerError:
            self.ui.CoolerStatusLabel.setText('True')
            self.ui.CoolerStatusLabel.setStyleSheet("QLabel {color: #C00}")
        else:
            self.ui.CoolerStatusLabel.setText('False')
            self.ui.CoolerStatusLabel.setStyleSheet("QLabel {color: None}")
        
    #def gainSpinChanged(self,value):
        #self.dev.setPMTGain(value)
        #if self.dev.isHVOn():
            #self.dev.changePMTGain()
            
    
    def overloadError(self,overloadError):
        if overloadError:
            self.ui.OverloadStatusLabel.setText('True')
            self.ui.OverloadStatusLabel.setStyleSheet("QLabel {color: #C00}")
        else:
            self.ui.OverloadStatusLabel.setText('False')
            self.ui.OverloadStatusLabel.setStyleSheet("QLabel {color: None}")
    
    def peltierStatus(self,peltierStat):
        if peltierStat:
            self.ui.peltierLabel.setText('PMT Peltier On')
            self.ui.peltierLabel.setStyleSheet("QLabel {color: #C00}")
        else:
            self.ui.peltierLabel.setText('PMT Peltier Off')
            self.ui.peltierLabel.setStyleSheet("QLabel {color: None}") 

    def pmtPower(self,pmtP):
        if pmtP:
            self.ui.highVoltageLabel.setText('PMT high voltage On')
            self.ui.highVoltageLabel.setStyleSheet("QLabel {color: #C00}")
        else:
            self.ui.highVoltageLabel.setText('PMT high voltage Off')
            self.ui.highVoltageLabel.setStyleSheet("QLabel {color: None}") 
      

            
        
       
        