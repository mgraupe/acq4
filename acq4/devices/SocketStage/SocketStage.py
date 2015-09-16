# -*- coding: utf-8 -*-
import time
from PyQt4 import QtGui, QtCore
from ..Stage import Stage, MoveFuture
from acq4.drivers.SocketStage import SocketStage as socketStage_Driver
from acq4.util.Mutex import Mutex
from acq4.util.Thread import Thread
from acq4.pyqtgraph import debug, ptime


def __reload__(old):
    # copy some globals if the module is reloaded
    SocketStage._monitor = old['SocketStage']._monitor


class ChangeNotifier(QtCore.QObject):
    """Used to send raw (unscaled) stage position updates to other devices. 
    In particular, focus motors may use this to hijack unused ROE axes.
    """
    sigPositionChanged = QtCore.Signal(object, object)


class SocketStage(Stage):
    """
    This Device class represents a single drive of a stage/manipulator controlled through a network socket
    Config options are: 

        port: <port at host server>  # eg. 5555
        ipAddress: <ip address of host server> # eg. '172.20.61.180'
    """

    _pos_cache = None
    _notifier = ChangeNotifier()
    _monitor = None
    _drives = [None]*2
    slowSpeed = 4  # speed to move when user requests 'slow' movement

    def __init__(self, man, config, name):
        self.port = config.pop('port')
        self.ipAddress = config.pop('ipAddress')
        if ('transform' in self.config) and ('scale' in self.config['transform']):
            self.scale = config['transform']['scale']
        else:
            self.scale = (1, 1, 1)

        self._drives[0] = self
        
        man.sigAbortAll.connect(self.stop)

        self._lastMove = None

        Stage.__init__(self, man, config, name)
        
        self.netS = socketStage_Driver(self.ipAddress,self.port)
        
        # clear cached position for this device and re-read to generate an initial position update
        self._pos_cache = None
        self.getPosition(refresh=True)

        ## May have multiple SutterMPC200 instances (one per drive), but 
        ## we only need one monitor.
        if SocketStage._monitor is None:
            SocketStage._monitor = MonitorThread(self)
            SocketStage._monitor.start()

    def capabilities(self):
        """Return a structure describing the capabilities of this device"""
        if 'capabilities' in self.config:
            return self.config['capabilities']
        else:
            return {
                'getPos': (True, True, True),
                'setPos': (True, True, True),
                'limits': (True, True, True),
            }

    def stop(self):
        """Stop _any_ moving drives on the MPC200.
        """
        self.netS.stop()

    @classmethod
    def _checkPositionChange(cls, pos=None):
        ## Anyone may call this function. 
        ## If any drive has changed position, SutterMPC200_notifier will emit 
        ## a signal, and the correct devices will be notified.
        #if drive is None:
        #    for dev in cls._drives:
        #        if dev is None:
        #            continue
        for netS in cls._drives:
            #print netS
            pos = netS.netS.getPos()
            break
            
        #        break
        if pos != cls._pos_cache:
            oldpos = cls._pos_cache
            cls._notifier.sigPositionChanged.emit(pos, oldpos)
            netS = cls._drives[0]
            netS._pos_cache = pos
            pos = [pos[i] * netS.scale[i] for i in (0, 1, 2)]
            netS.posChanged(pos)

            return (pos, oldpos)
        return False

    def _getPosition(self):
        # Called by superclass when user requests position refresh
        pos = self.netS.getPos()
        self._checkPositionChange(pos) # might as well check while we're here..
        pos = [pos[i] * self.scale[i] for i in (0, 1, 2)]
        return pos

    def targetPosition(self):
        if self._lastMove is None or self._lastMove.isDone():
            return self.getPosition()
        else:
            return self._lastMove.targetPos

    def quit(self):
        self._monitor.stop()
        Stage.quit(self)

    def _move(self, abs, rel, speed, linear):
        # convert relative to absolute position, fill in Nones with current position.
        pos = self._toAbsolutePosition(abs, rel)

        # convert speed to values accepted by MPC200

        self._lastMove = SocketStageMoveFuture(self, pos, speed)
        return self._lastMove


class MonitorThread(Thread):
    def __init__(self, dev):
        self.dev = dev
        self.lock = Mutex(recursive=True)
        self.stopped = False
        self.interval = 0.3
        
        self.nextMoveId = 0
        self.moveRequest = None
        self._moveStatus = {}
        
        Thread.__init__(self)

    def start(self):
        self.stopped = False
        Thread.start(self)

    def stop(self):
        with self.lock:
            self.stopped = True

    def setInterval(self, i):
        with self.lock:
            self.interval = i
            
    def move(self, pos, speed):
        """Instruct a drive to move. 

        Return an ID that can be used to check on the status of the move until it is complete.
        """
        with self.lock:
            if self.moveRequest is not None:
                raise RuntimeError("Stage is already moving.")
            id = self.nextMoveId
            self.nextMoveId += 1
            self.moveRequest = (id, pos, speed)
            self._moveStatus[id] = (None, None)
            
        return id

    def moveStatus(self, id):
        """Check on the status of a previously requested move.

        Return:
        * None if the request has not been handled yet
        * (start_time, False) if the device is still moving
        * (start_time, True) if the device has stopped
        * (start_time, Exception) instance if there was an error during the move

        If True or an Exception is returned, then the status may not be requested again for the same ID.
        """
        with self.lock:
            start, stat = self._moveStatus[id]
            if stat not in (False, None):
                del self._moveStatus[id]
            return start, stat

    def run(self):
        minInterval = 100e-3
        interval = minInterval
        
        while True:
            try:
                with self.lock:
                    if self.stopped:
                        break
                    maxInterval = self.interval
                    moveRequest = self.moveRequest
                    self.moveRequest = None

                if moveRequest is None:
                    # just check for position update
                    if self.dev._checkPositionChange() is not False:
                        interval = minInterval
                    else:
                        interval = min(maxInterval, interval*2)
                else:
                    # move the drive
                    mid, pos, speed = moveRequest
                    try:
                        with self.dev.netS.lock:
                            # record the move starting time only after locking the device
                            start = ptime.time()
                            with self.lock:
                                self._moveStatus[mid] = (start, False)
                            pos = self.dev.netS.moveTo(pos, speed)
                            self.dev._checkPositionChange( pos)
                    except Exception as err:
                        debug.printExc('Move error:')
                        try:
                            if hasattr(err, 'lastPosition'):
                                self.dev._checkPositionChange(err.lastPosition)
                        finally:
                            with self.lock:
                                self._moveStatus[mid] = (start, err)
                    else:
                        with self.lock:
                            self._moveStatus[mid] = (start, True)

                time.sleep(interval)
            except:
                debug.printExc('Error in Socket Stage monitor thread:')
                time.sleep(maxInterval)
                

class SocketStageMoveFuture(MoveFuture):
    """Provides access to a move-in-progress on an MPC200 drive.
    """
    def __init__(self, dev, pos, speed):
        MoveFuture.__init__(self, dev, pos, speed)
        
        # because of MPC200 idiosyncracies, we must coordinate with the monitor
        # thread to do a move.
        self._expectedDuration = dev.netS.expectedMoveDuration(pos, speed)
        scaled = []
        for i in range(3):
            if dev.scale[i] != 0:
                scaled.append(pos[i] / dev.scale[i])
            else:
                scaled.append(None)
        self._id = SocketStage._monitor.move(scaled, speed)
        self._moveStatus = (None, None)
        while True:
            start, status = self._getStatus()
            # block here until move begins (to check for errors in the move call)
            if status is not None:
                break
            time.sleep(5e-3)
        if isinstance(status, Exception):
            raise status
        
    def wasInterrupted(self):
        """Return True if the move was interrupted before completing.
        """
        return isinstance(self._getStatus()[1], Exception)

    def percentDone(self):
        """Return an estimate of the percent of move completed based on the 
        device's speed table.
        """
        if self.isDone():
            return 100
        dt = ptime.time() - self._getStatus()[0]
        if self._expectedDuration == 0:
            return 99
        return max(min(100 * dt / self._expectedDuration, 99), 0)
    
    def isDone(self):
        """Return True if the move is complete.
        """
        return self._getStatus()[1] not in (None, False)

    def _getStatus(self):
        # check status of move unless we already know it is complete.
        if self._moveStatus[1] in (None, False):
            self._moveStatus = SocketStage._monitor.moveStatus(self._id)
        return self._moveStatus
        