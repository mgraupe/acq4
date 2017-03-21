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
        if 'PeltierPower' in config['channels']:
            daqConfig['PeltierPower'] = config['channels']['PeltierPower']
            self.hasPeltierPower = True
        if 'PeltierError' in config['channels']:
            daqConfig['PeltierError'] = config['channels']['PeltierError']
            self.hasPeltierError = True
        if 'PMTPower' in config['channels']:
            daqConfig['PMTPower'] = config['channels']['PMTPower']
            self.hasPMTPower = True
        if 'PMTOverloadError' in config['channels']:
            daqConfig['PMTOverloadError'] = config['channels']['PMTOverloadError']
            self.hasPMTOverloadError = True
        if 'VcontExt' in config['channels']:
            daqConfig['VcontExt'] = config['channels']['VcontExt']
            self.hasVcontExt = True
        if 'VcontMon' in config['channels']:
            daqConfig['VcontMon'] = config['channels']['VcontMon']
            self.hasVcontMon = True
        OptomechDevice.__init__(self, dm, config, name)
        DAQGeneric.__init__(self, dm, daqConfig, name)

    def getFilterDevice(self):
        # return parent filter device or None
        if 'Filter' in self.omConf['parentDevice'] :
            return self.omConf['parentDevice']
        else:
            return None
        
        
