import serial, struct, time, collections
import numpy as np
import socket as sock
import re

try:
    # this is nicer because it provides deadlock debugging information
    from acq4.util.Mutex import RecursiveMutex as RLock
except ImportError:
    from threading import RLock

#try:
#    from ..SerialDevice import SerialDevice, TimeoutError, DataError
#except ValueError:
#    ## relative imports not allowed when running from command prompt
#    if __name__ == '__main__':
#        import sys, os
#        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#        from SerialDevice import SerialDevice, TimeoutError, DataError


def threadsafe(method):
    # decorator for automatic mutex lock/unlock
    def lockMutex(self, *args, **kwds):
        with self.lock:
            return method(self, *args, **kwds)
    return lockMutex


class SocketStage():
    """
    Provides access to a stage controlled from a different computer through the network connection.

    Example::

        stage = stocketStage.getDevice('com4')

        # get information about which drives are active
        n, drives = dev.getDriveStatus()

        # read position of drive 0
        print dev.getPos(0)

        # move drive 1 to x=10mm
        dev.moveTo(1, [10e-3, 0, 0], 'fast')
    """

    def __init__(self, ipAddress,portOnHost,precision):
        
        self.s = sock.socket(sock.AF_INET, sock.SOCK_STREAM) #create a socket object
        self.host = ipAddress
        self.port = portOnHost
        
        self.sizeOfDataPackage = 1014
        # stage operates in microns and ACQ4 in meters
        self.conversion = 1.E6
        
        self.locationPrecision = precision
        self.axes = collections.OrderedDict([(0,'x'),(1,'y'),(2,'z')])
        
        self.s.connect((self.host,self.port))
        
        self.lock = RLock()
        self.moving = False
    
    def __del__(self):
        self.s.send('disconnect')
        del self.s
        
    @threadsafe
    def getPos(self):
        """Get current position reported by stage.

        Returns a tuple (x,y,z); values given in meters.

        """
        try:
            self.s.send('getPos')
            ans = self.s.recv(self.sizeOfDataPackage)
        except sock.error as err :
            raise err
        
        pos = self.convertResponse(ans)
        pos = tuple(pos/self.conversion)

        return pos

    @threadsafe
    def relativeMoveTo(self, pos, timeout=None):
        """Make a relative move of stage.
        
        Any item in the position may be set as None to leave it unchanged.
        
        *speed* may be specified as an integer 0-15 for constant speed, or 
        'fast' indicating that the drive should use acceleration to move as
        quickly as possible. For constant speeds, a value of 15 is maximum,
        about 1.3mm/sec for the _fastest moving axis_, not for the net speed
        of all three axes.

        If *timeout* is None, then a suitable timeout is chosen based on the selected 
        speed and distance to be traveled.
        
        Positions must be specified in meters unless *scaled* = False, in which 
        case position is specified in motor steps. 

        This method will either 1) block until the move is complete and return the 
        final position, 2) raise TimeoutError if the timeout has elapsed or, 3) raise 
        RuntimeError if the move was unsuccessful (final position does not match the 
        requested position). Exceptions contain the final position as `ex.lastPosition`.
        """

        currentPos = self.getPos()
        
        # replace none entries with current position values
        pos = np.asarray(pos)
        for i in range(3):
            if pos[i] is None:
                pos[i] = 0
        
        # step below C843 precision
        if np.all(np.abs(pos) < self.locationPrecision):
            print 'aborted since relative move too small', np.abs(pos), self.locationPrecision
            return tuple(currentPos)

        # be sure to never request out-of-bounds position
        for i in range(3):
            if not (0 <= (currentPos[i]+pos[i]) < (25.e-3)):
                raise ValueError("Invalid coordinate %d : %g must be in [0, 25.e-3]" % (i, (currentPos[i]+pos[i])))

        #if timeout is None:
        #    # maximum distance to be travelled along any axis
        #    dist = (np.abs(ustepPos - currentPos) * self.scale).max()
        #    v = self.speedTable[speed]
        #    timeout = 1.0 + 1.5 * dist / v
        #    # print "dist, speed, timeout:", dist, v, timeout

        # Send move command
        #self.readAll()
        #if speed == 'fast':
        #    cmd = b'M' + struct.pack('<lll', *ustepPos)
        #    self.write(cmd)
        #else:
        #    #self.write(b'O')  # position updates on (these are broken in mpc200?)
        #    # self.write(b'F')  # position updates off
        #    # self.read(1, term='\r')
        #    self.write(b'S')
        #    # MPC200 crashes if the entire packet is written at once; this sleep is mandatory
        #    time.sleep(0.03)
        #    self.write(struct.pack('<B3i', speed, *ustepPos))
        
        # wait for any movement to finish 
        isMoving = True
        while isMoving:
            self.s.send('checkMovement')
            ans = self.s.recv(self.sizeOfDataPackage)
            mov = self.convertResponse(ans)
            print ans
            if not mov :
                isMoving = False
            time.sleep(0.3)
        
        try:
            for i in range(3):
                if pos[i]:
                    posSent = pos[i]*self.conversion
                    self.s.send('relativeMoveTo,%s,%s' % (self.axes[i],posSent))
                    ans = self.s.recv(self.sizeOfDataPackage)
                    print ans
        except sock.error as err:
            raise err
        
        
        # wait for move to complete
        #try:
        #    self._moving = True
        #    self.read(1, term='\r', timeout=timeout)
        #except DataError:
        #    # If the move is interrupted, sometimes we get junk on the serial line.
        #    time.sleep(0.03)
        #    self.readAll()
        #except TimeoutError:
        #    # just for debugging
        #    print "start pos:", currentPos, "move pos:", ustepPos
        #    raise
        #finally:
        #    self._moving = False

        # finally, make sure we ended up at the right place.
        newPos = self.getPos()
        #newPos = tuple([currentPos[i]/self.conversion for i in [1,2,3]])
        #for i in range(3):
        #    if abs(newPos[i] - pos[i]) > self.locationPrecision:
        #        err = RuntimeError("Move was unsuccessful (%r != %r)."  % (tuple(newPos), tuple(ustepPos)))
        #        err.lastPosition = newPos
        #        raise err
        return newPos
    @threadsafe
    def moveTo(self, pos, speed=None, timeout=None):
        """Make a absolute move of stage.
        
        Any item in the position may be set as None to leave it unchanged.
        
        *speed* may be specified as an integer 0-15 for constant speed, or 
        'fast' indicating that the drive should use acceleration to move as
        quickly as possible. For constant speeds, a value of 15 is maximum,
        about 1.3mm/sec for the _fastest moving axis_, not for the net speed
        of all three axes.

        If *timeout* is None, then a suitable timeout is chosen based on the selected 
        speed and distance to be traveled.
        
        Positions must be specified in meters unless *scaled* = False, in which 
        case position is specified in motor steps. 

        This method will either 1) block until the move is complete and return the 
        final position, 2) raise TimeoutError if the timeout has elapsed or, 3) raise 
        RuntimeError if the move was unsuccessful (final position does not match the 
        requested position). Exceptions contain the final position as `ex.lastPosition`.
        """

        currentPos = self.getPos()
        
        # replace none entries with current position values
        pos = np.asarray(pos)
        for i in range(3):
            if pos[i] is None:
                pos[i] = currentPos[i]
        
        # step below C843 precision
        if np.all(np.abs(pos-np.asarray(currentPos)) < self.locationPrecision):
            return tuple(currentPos)

        # be sure to never request out-of-bounds position
        for i in range(3):
            if not (0 <= pos[i] < (25.e-3)):
                raise ValueError("Invalid coordinate %d : %g must be in [0, 25.e-3]" % (i, pos[i]))

        #if timeout is None:
        #    # maximum distance to be travelled along any axis
        #    dist = (np.abs(ustepPos - currentPos) * self.scale).max()
        #    v = self.speedTable[speed]
        #    timeout = 1.0 + 1.5 * dist / v
        #    # print "dist, speed, timeout:", dist, v, timeout

        # Send move command
        #self.readAll()
        #if speed == 'fast':
        #    cmd = b'M' + struct.pack('<lll', *ustepPos)
        #    self.write(cmd)
        #else:
        #    #self.write(b'O')  # position updates on (these are broken in mpc200?)
        #    # self.write(b'F')  # position updates off
        #    # self.read(1, term='\r')
        #    self.write(b'S')
        #    # MPC200 crashes if the entire packet is written at once; this sleep is mandatory
        #    time.sleep(0.03)
        #    self.write(struct.pack('<B3i', speed, *ustepPos))
        
        # wait for any movement to finish 
        isMoving = True
        while isMoving:
            self.s.send('checkMovement')
            ans = self.s.recv(self.sizeOfDataPackage)
            mov = self.convertResponse(ans)
            print ans
            if not mov :
                isMoving = False
            time.sleep(0.3)
        
        try:
            for i in range(3):
                if (currentPos[i] - pos[i]):
                    posSent = pos[i]*self.conversion
                    self.s.send('absoluteMoveTo,%s,%s' % (self.axes[i],posSent))
                    ans = self.s.recv(self.sizeOfDataPackage)
                    time.sleep(0.3)
                    # make another move since precision is low for large movements
                    self.s.send('absoluteMoveTo,%s,%s' % (self.axes[i],posSent))
                    ans = self.s.recv(self.sizeOfDataPackage)
                    print ans
        except sock.error as err:
            raise err
        
        
        # wait for move to complete
        #try:
        #    self._moving = True
        #    self.read(1, term='\r', timeout=timeout)
        #except DataError:
        #    # If the move is interrupted, sometimes we get junk on the serial line.
        #    time.sleep(0.03)
        #    self.readAll()
        #except TimeoutError:
        #    # just for debugging
        #    print "start pos:", currentPos, "move pos:", ustepPos
        #    raise
        #finally:
        #    self._moving = False

        # finally, make sure we ended up at the right place.
        newPos = self.getPos()
        #newPos = tuple([currentPos[i]/self.conversion for i in [1,2,3]])
        for i in range(3):
            if abs(newPos[i] - pos[i]) > self.locationPrecision:
                err = RuntimeError("Move was unsuccessful (%r != %r)."  % (newPos[i], pos[i]))
                err.lastPosition = newPos
                raise err
        return newPos
    
    def expectedMoveDuration(self, pos, speed):
        """Return the expected time duration required to move *drive* to *pos* at *speed*.
        """
        cPos = self.getPos()

        dx = np.abs(np.array(pos) - cPos).max()
        return dx / 10.
    
    def convertResponse(self, answer):    
        #print answer, type(answer), len(answer)
        fanswer = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+",answer)
        #if not fanswer[0] == '1':
        #    raise 
        #print 'convert',fanswer, len(fanswer)
        if len(fanswer)==1:
            return int(fanswer[0])
        
        pos = np.zeros(3)
        for i in range(3):
            pos[i] = float(fanswer[i+1])
        
        return pos
        
    # Disabled--official word from Sutter is that the position updates sent during a move are broken.
    # def readMoveUpdate(self):
    #     """Read a single update packet sent during a move.

    #     If the drive is moving, then return the current position of the drive.
    #     If the drive is stopped, then return True.
    #     If the drive motion was interrupted, then return False.

    #     Note: update packets are not generated when moving in 'fast' mode.
    #     """
    #     try:
    #         d = self.read(12, timeout=0.5)
    #     except TimeoutError as err:
    #         if err.data == 'I':
    #             return False
    #         else:
    #             print "timeout:", repr(err.data)
    #             return True

    #     pos = []
    #     # unpack four three-byte integers
    #     for i in range(4):
    #         x = d[i*3:(i+1)*3] + '\0'
    #         pos.append(struct.unpack('<i', x)[0])

    #     return pos
    def stop(self):
        """ disconnect the socket stage
        """
        self.s.send('disconnect')
        ans = self.s.recv(self.sizeOfDataPackage)
    
    def stopMovement(self):
        """Stop moving the active drive.
        """
        # lock before stopping if possible
        if self.lock.acquire(blocking=False):
            try:
                self.write('\3')
                self.read(1, term='\r')
            finally:
                self.lock.release()

        # If the lock is in use, then we write immediately and hope for the best.
        else:
            self.write('\3')
            with self.lock:
                time.sleep(0.02)
                self.readAll()




