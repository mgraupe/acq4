# -*- coding: utf-8 -*-
from acq4.devices.PMT import *
from acq4.devices.HamamatsuPMT.HamamatsuPMTDevGui import HamamatsuPMTDevGui
from acq4.util.Mutex import Mutex
from acq4.util.Thread import Thread
import acq4.util.debug as debug
import numpy as np
import time

class HamamatsuPMT(PMT):

    sigPMTGainChanged = QtCore.Signal(object)
    sigCoolerErrorOccurred = QtCore.Signal(object)
    sigOverloadErrorOccurred = QtCore.Signal(object)
    sigPeltierStatus = QtCore.Signal(object)
    sigPMTPower = QtCore.Signal(object)
    
    def __init__(self, dm, config, name):
        self.optimalPMTGain = config.get('PMTgain',0.85)
        self.delay = config.get('HighVoltageDelay',0.5)
        self.gainStepSize = 0.001
        self.gainStepWait = 0.01
        # in sec
        #self.alignmentPower = config.get('alignmentPower',0.2)
        
        self.hamamatsuLock = Mutex(QtCore.QMutex.Recursive)  ## access to self.attributes
        self.maiTaiPower = 0.
        self.maiTaiWavelength = 0
        self.maiTaiHumidity = 0.
        self.maiTaiPumpPower = 0.
        self.maiTaiPulsing = False
        self.maiTaiP2Optimization = False
        self.maiTaiMode = None
        self.maiTaiHistory = None
        
        PMT.__init__(self, dm, config, name)
        
        self.hThread = HamamatsuPMTThread(self)
        self.hThread.sigPMTGainChang.connect(self.gainChanged)
        self.hThread.sigCoolerError.connect(self.coolerError)
        self.hThread.sigOverloadError.connect(self.overloadError)
        self.hThread.sigPeltierStat.connect(self.peltierStatus)
        self.hThread.sigPMTPow.connect(self.PMTPower)
                
        self.hThread.start()
        
        self.currentGain = self.getPMTGain()
        self.currentSetGain = 0.
        
        
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
    
    def changePMTGain(self,newGain):
        steps = abs(int((newGain-self.currentSetGain)/self.gainStepSize))
        for ga in np.linspace(self.currentSetGain,newGain,steps):
            self.setChanHolding('VcontExt',ga)
            time.sleep(self.gainStepWait)
        print 'gain changed from ',self.currentSetGain, ' to ', newGain, ' in ', steps, ' steps'
        self.currentSetGain = newGain
            
    
    def activatePeltier(self):
        print 'Peltier:', self.isPeltierOn()
        print 'turn Peltier on'
        self.switchPeltierOn()
        print 'Peltier:', self.isPeltierOn()
        
    def deactivatePeltier(self):
        print 'Peltier:', self.isPeltierOn()
        print 'turn Peltier off'
        self.switchPeltierOff()
        print 'Peltier:', self.isPeltierOn()
        
    def activateHV(self):
        print 'High Voltage:', self.isHVOn()
        print 'turn High Voltage on'
        self.switchPMTOn()
        self.changePMTGain(self.optimalPMTGain)
        print 'High voltage:',self.isHVOn()
        
    def deactivateHV(self):
        print 'turn High Voltage off'
        self.changePMTGain(0.)
        self.switchHVOff()
        print 'High voltage:',self.isPMTOn()
    
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
    
    def overloadError(self,overloadError):
        with self.hamamatsuLock:   
            self.sigOverloadErrorOccurred.emit(overloadError)
            
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
    
class HamamatsuPMTTask(DeviceTask):
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
        
    #def setWavelength(self, wl):
    #    pass
        
    #def setShutter(self, opened):
    #    wait = QtCore.QWaitCondition()
    #    cmd = ['setShutter', opened]
    #    with self.lock:
    #        self.cmds.append(cmd)
    #def adjustPumpPower(self,currentPower):
    #    """ keeps laser output power between alignmentPower value and  alignmentPower + 25%"""
    #    lastCommandedPP = self.driver.getLastCommandedPumpLaserPower()
    #    if self.dev.alignmentPower*1.25 < currentPower:
    #        newPP = round(lastCommandedPP*0.98,2) # decrease pump power by 2 % 
    #        self.driver.setPumpLaserPower(newPP)
    #    elif self.dev.alignmentPower > currentPower:
    #        newPP = round(lastCommandedPP*1.01,2) # increase pump power by 1 % 
    #        self.driver.setPumpLaserPower(newPP)
    #    #newCommandedPP = self.driver.getLastCommandedPumpLaserPower()
    #    #print 'pump laser power - before : new : after , ', lastCommandedPP, newPP, newCommandedPP
    #    #print 'laser output power : ', currentPower
        
        
    def run(self):
        self.stopThread = False
        #with self.driverLock:
        #    self.sigWLChanged.emit(self.driver.getWavelength()*1e-9)
        while True:
            try:
                #with self.driverLock:
                gain = self.dev.getPMTGain()
                coolerError = self.dev.getCoolerStatus()
                overloadError = self.dev.getOverloadStatus()
                peltierStatus = self.dev.isPeltierOn()
                pmtPower = self.dev.isPMTOn()
                    
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

        #self.driver.close()
    
    def stop(self, block=False):
        with self.lock:
            self.stopThread = True
        if block:
            if not self.wait(10000):
                raise Exception("Timed out while waiting for thread exit!")
