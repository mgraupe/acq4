# -*- coding: utf-8 -*-
from acq4.devices.PMT import *
from acq4.devices.DAQGeneric import *
from acq4.devices.HamamatsuPMT.HamamatsuPMTDevGui import HamamatsuPMTDevGui
from acq4.util.Mutex import Mutex
from acq4.util.Thread import Thread
import acq4.util.debug as debug
import numpy as np
import time

class HamamatsuPMT(PMT):
    """
    Control of the Hamamtsu PMT (H7422) through the M9012 temperature control and power supply unit. Cooling and high voltage settings can be controlled throug the I/O connecters on the card which in turn are linked to the DAQ input/output channels. The device interface allows to arm the PMT and control the gain voltage. Furthermore, resetting is possible in case cooling and overload errors occur.     
    
    Configuration example:
    
    # Hamamatsu Photomultiplier device
    PMT:
        driver: 'HamamatsuPMT'
        parentDevice: 'FilterWheel'
        PMTgain : 0.85 # optimal gain in volts
        channels:
            Input:
                device: 'DAQ'
                channel: '/Dev2/ctr0' #'/Dev1/ai0'
                #mode: 'PseudoDiff'
                type: 'ci' #'ai'
            PeltierPower:
                device: 'DAQ'
                channel: '/Dev2/port1/line1' 
                type: 'do' #'ai'
            PeltierError:
                device: 'DAQ'
                channel: '/Dev2/port1/line2' 
                type: 'di' #'ai'
            PMTPower:
                device: 'DAQ'
                channel: '/Dev2/port1/line3' 
                type: 'do' #'ai'
            PMTOverloadError:
                device: 'DAQ'
                channel: '/Dev2/port1/line4' 
                type: 'di' #'ai'
            VcontExt:
                device: 'DAQ'
                channel: '/Dev2/ao3' 
                type: 'ao' #'ai'
            VcontMon:
                device: 'DAQ'
                channel: '/Dev2/ai9' 
                mode: 'rse'
                type: 'ai' #'ai'

    """

    sigPMTGainChanged = QtCore.Signal(object)
    sigCoolerErrorOccurred = QtCore.Signal(object)
    sigOverloadErrorOccurred = QtCore.Signal(object)
    sigPeltierStatus = QtCore.Signal(object)
    sigPMTPower = QtCore.Signal(object)
    
    def __init__(self, dm, config, name):
        self.currentSetGain = config.get('PMTgain',0.85)
        self.gainStepSize = 0.001
        self.gainStepWait = 0.01 # in sec
        self.HVpowerTimeOut = 3.
        self.PelPowerTimeOut = 1.
        self.fixingOverloadError = False
        self.fixingPelError = False
        
        PMT.__init__(self, dm, config, name)
        self.hamamatsuLock = Mutex(QtCore.QMutex.Recursive)  ## access to self.attributes
        
        if self.isHVOn():
            self.currentGain = self.getPMTGain()
        else:
            self.currentGain = 0.
        
        self.hThread = HamamatsuPMTThread(self)
        self.hThread.sigPMTGainChang.connect(self.gainChanged)
        self.hThread.sigCoolerError.connect(self.coolerError)
        self.hThread.sigOverloadError.connect(self.overloadError)
        self.hThread.sigPeltierStat.connect(self.peltierStatus)
        self.hThread.sigPMTPow.connect(self.PMTPower)
        self.hThread.start()
        
        dm.declareInterface(name, ['HamamatsuPMT'], self)
        dm.sigAbortAll.connect(self.deactivatePMT)
        
    def isHVOn(self):
       with self.hamamatsuLock:
           return self.getChanHolding('PMTPower')
       
    def switchHVOn(self):
        with self.hamamatsuLock:
            self.setChanHolding('PMTPower',1)

    def switchHVOff(self):
        with self.hamamatsuLock:
            self.setChanHolding('PMTPower',0)
    
    def isPeltierOn(self):
       with self.hamamatsuLock:
           return self.getChanHolding('PeltierPower')
       
    def switchPeltierOn(self):
        with self.hamamatsuLock:
            self.setChanHolding('PeltierPower',1)

    def switchPeltierOff(self):
        with self.hamamatsuLock:
            self.setChanHolding('PeltierPower',0)
    
    def setPMTGain(self,value):
        self.currentSetGain = value
    
    def changePMTGain(self,newGain=False):
        if gainOn:
            with self.hamamatsuLock:
                self.setChanHolding('VcontExt',1)    
        else:
            with self.hamamatsuLock:
                self.setChanHolding('VcontExt',0)

    def deactivatePMT(self):
        if self.isHVOn():
            self.deactivateHV()
        if self.isPeltierOn():
            self.deactivatePeltier()
    
    def activatePeltier(self):
        print 'Peltier:', self.isPeltierOn()
        print 'turn Peltier on'
        self.switchPeltierOn()
        print 'Peltier:', self.isPeltierOn()
        
    def deactivatePeltier(self):
        if self.isHVOn():
            self.deactivateHV()
        print 'Peltier:', self.isPeltierOn()
        print 'turn Peltier off'
        self.switchPeltierOff()
        print 'Peltier:', self.isPeltierOn()
        
    def activateHV(self):
        print 'High Voltage:', self.isHVOn()
        print 'turn High Voltage on'
        self.switchHVOn()
        self.changePMTGain(gainOn=True)
        print 'High voltage:',self.isHVOn()
        
    def deactivateHV(self):
        print 'turn High Voltage off'
        self.changePMTGain(gainOn=False)
        self.switchHVOff()
        print 'High voltage:',self.isHVOn()
    
    def getPMTGain(self):
        with self.hamamatsuLock:    
            gain = self.getChannelValue('VcontMon')
            return gain
    
    def getCoolerStatus(self):
        with self.hamamatsuLock:   
            coolerError = self.getChannelValue('PeltierError')
            return coolerError
        
    def getOverloadStatus(self):
        with self.hamamatsuLock:   
            overloadError = self.getChannelValue('PMTOverloadError')
            return overloadError
        
    def gainChanged(self,gain):
        with self.hamamatsuLock:   
            self.pmtGain = gain
            self.sigPMTGainChanged.emit(gain)
    
    def coolerError(self,coolerError):
        with self.hamamatsuLock:   
            self.sigCoolerErrorOccurred.emit(coolerError)
            if (coolerError) and (not self.fixingPelError):
                self.fixingPelError = True
                self.deactivateHV()
                time.sleep(self.HVpowerTimeOut)
                self.deactivatePeltier()
                time.sleep(self.PelPowerTimeOut)
                self.activatePeltier()
                self.activateHV()
                self.fixingPelError = False
                
    def overloadError(self,overloadError):
        with self.hamamatsuLock:   
            self.sigOverloadErrorOccurred.emit(overloadError)
            if (overloadError) and (not self.fixingOverloadError):
                self.fixingOverloadError = True
                self.deactivateHV()
                print 'high voltage time out ...',
                time.sleep(self.HVpowerTimeOut)
                print 'ended'
                self.activateHV()
                self.fixingOverloadError = False
                
    def peltierStatus(self,peltierStat):
        with self.hamamatsuLock:
            self.sigPeltierStatus.emit(peltierStat)
            
    def PMTPower(self,pmtP):
        with self.hamamatsuLock:
            self.sigPMTPower.emit(pmtP)
    
    def createTask(self, cmd, parentTask):
        return HamamatsuPMTTask(self, cmd, parentTask)

    def deviceInterface(self, win):
        return HamamatsuPMTDevGui(self)
    
class HamamatsuPMTTask(DAQGenericTask):
    pass
    
class HamamatsuPMTThread(Thread):

    sigPMTGainChang = QtCore.Signal(object)
    sigCoolerError = QtCore.Signal(object)
    sigOverloadError = QtCore.Signal(object)
    sigPeltierStat = QtCore.Signal(object)
    sigPMTPow = QtCore.Signal(object)

    def __init__(self, dev):
        Thread.__init__(self)
        self.lock = Mutex(QtCore.QMutex.Recursive)
        self.dev = dev
        self.cmds = {}
        self.overloaded = False
        
    def run(self):
        self.stopThread = False
        while True:
            try:
                gain = self.dev.getPMTGain()
                coolerError = self.dev.getCoolerStatus()
                overloadError = self.dev.getOverloadStatus()
                peltierStatus = self.dev.isPeltierOn()
                pmtPower = self.dev.isHVOn()
                    
                self.sigPMTGainChang.emit(gain)
                self.sigCoolerError.emit(coolerError)
                self.sigOverloadError.emit(overloadError)
                self.sigPeltierStat.emit(peltierStatus)
                self.sigPMTPow.emit(pmtPower)
                time.sleep(0.5)
            except:
                debug.printExc("Error in Hamamatsu PMT communication thread:")
                
            self.lock.lock()
            if self.stopThread:
                self.lock.unlock()
                break
            self.lock.unlock()
            time.sleep(0.02)

    
    def stop(self, block=False):
        with self.lock:
            self.stopThread = True
        if block:
            if not self.wait(10000):
                raise Exception("Timed out while waiting for thread exit!")
