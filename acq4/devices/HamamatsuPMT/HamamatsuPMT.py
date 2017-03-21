# -*- coding: utf-8 -*-
from acq4.devices.PMT import *
from acq4.devices.HamamatsuPMT.HamamatsuPMTDevGui import HamamatsuPMTDevGui
from acq4.util.Mutex import Mutex
from acq4.util.Thread import Thread
import acq4.util.debug as debug
import time

class HamamatsuPMT(PMT):

    sigPMTGainChanged = QtCore.Signal(object)
    sigCoolerErrorOccurred = QtCore.Signal(object)
    sigOverloadErrorOccurred = QtCore.Signal(object)
    sigPeltierStatus = QtCore.Signal(object)
    sigPMTPower = QtCore.Signal(object)
    
    def __init__(self, dm, config, name):
        #self.port = config['port']-1  ## windows com ports start at COM1, pyserial ports start at 0
        self.pmtGain = config.get('PMTgain',0.85)
        self.delay = 1. # in sec
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
        
        
        
        #self.hasShutter = True
        #self.hasTunableWavelength = True
        
        #if self.hasExternalSwitch:
        #    if not self.getInternalShutter():
        #        self.setChanHolding('externalSwitch', 1)
        
        dm.sigAbortAll.connect(self.deactivatePMT)
        
    def isPMTOn(self):
       with self.hamamatsuLock:
           return self.getChanHolding('PMTPower')
       
    def switchPMTOn(self):
        with self.hamamatsuLock:
            self.setChanHolding('PMTPower',1)

    def switchPMTOff(self):
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
    
    def activatePMT(self):
        self.switchPeltierOn()
        time.sleep(5.)
        self.switchPMTOn()
        
    def deactivatePMT(self):
        self.switchPMTOff()
        time.sleep(5.)
        self.switchPeltierOff()
    
    def getPMTGain(self):
        with self.hamamatsuLock:    
            gain = self.getChannelValue('VcontMon')
            return gain
    
    def getCoolerStatus(self):
        with self.hamamatsuLock:   
            coolerError = self.getChannelValue('PeltierError')
            if coolerError:
                return 'True'
            else:
                return 'False'
        
    def getOverloadStatus(self):
        with self.hamamatsuLock:   
            overloadError = self.getChannelValue('PMTOverloadError')
            if overloadError:
                return 'True'
            else:
                return 'False'
        
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
    # This is disabled--internal shutter in coherent laser should NOT be used by ACQ4; use a separate shutter.
    #
    # def start(self):
    #     # self.shutterOpened = self.dev.getShutter()
    #     # if not self.shutterOpened:
    #     #     self.dev.openShutter()
    #     #     time.sleep(2.0)  ## opening the shutter causes momentary power drop; give laser time to recover
    #     #                      ## Note: It is recommended to keep the laser's shutter open rather than
    #     #                      ## rely on this to open it for you.
    #     LaserTask.start(self)
        
    # def stop(self, abort):
    #     if not self.shutterOpened:
    #         self.dev.closeShutter()
    #     LaserTask.stop(self, abort)
        
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
        #self.driver = driver
        #self.driverLock = lock
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
                self.sigOverloadError.emit(coolerError)
                self.sigCoolerError.emit(overloadError)
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
