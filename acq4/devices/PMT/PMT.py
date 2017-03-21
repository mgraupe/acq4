# -*- coding: utf-8 -*-
from acq4.devices.Device import *
from acq4.devices.OptomechDevice import OptomechDevice
from acq4.devices.DAQGeneric import DAQGeneric

class PMT(DAQGeneric, OptomechDevice):
    def __init__(self, dm, config, name):
        self.omConf = {}
        for k in ['parentDevice', 'transform']:
            if k in config:
                self.omConf[k] = config.pop(k)
        daqConfig = {}
        if 'PeltierPower' in config:
            daqConfig['PeltierPower'] = config['PeltierPower']
            self.hasPeltierPower = True
         if 'PeltierError' in config:
            daqConfig['PeltierError'] = config['PeltierError']
            self.hasPeltierError = True
        if 'PMTPower' in config:
            daqConfig['PMTPower'] = config['PMTPower']
            self.hasPMTPower = True
        if 'PMTOverloadError' in config:
            daqConfig['PMTOverloadError'] = config['PMTOverloadError']
            self.hasPMTOverloadError = True
        if 'Vcont-ext' in config:
            daqConfig['VcontExt'] = config['VcontExt']
            self.hasVcontExt = True
        if 'Vcont-mon' in config:
            daqConfig['VcontMon'] = config['VcontMon']
            self.hasVcontMon = True
        OptomechDevice.__init__(self, dm, config, name)
        DAQGeneric.__init__(self, dm, daqConfig, name)

    def getFilterDevice(self):
        # return parent filter device or None
        if 'Filter' in self.omConf['parentDevice'] :
            return self.omConf['parentDevice']
        else:
            return None
        
        
