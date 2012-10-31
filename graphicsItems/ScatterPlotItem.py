from pyqtgraph.Qt import QtGui, QtCore, USE_PYSIDE
from pyqtgraph.Point import Point
import pyqtgraph.functions as fn
from .GraphicsItem import GraphicsItem
from .GraphicsObject import GraphicsObject
import numpy as np
import scipy.stats
import weakref
import pyqtgraph.debug as debug
from pyqtgraph.pgcollections import OrderedDict
#import pyqtgraph as pg 

__all__ = ['ScatterPlotItem', 'SpotItem']


## Build all symbol paths
Symbols = OrderedDict([(name, QtGui.QPainterPath()) for name in ['o', 's', 't', 'd', '+']])
Symbols['o'].addEllipse(QtCore.QRectF(-0.5, -0.5, 1, 1))
Symbols['s'].addRect(QtCore.QRectF(-0.5, -0.5, 1, 1))
coords = {
    't': [(-0.5, -0.5), (0, 0.5), (0.5, -0.5)],
    'd': [(0., -0.5), (-0.4, 0.), (0, 0.5), (0.4, 0)],
    '+': [
        (-0.5, -0.05), (-0.5, 0.05), (-0.05, 0.05), (-0.05, 0.5),
        (0.05, 0.5), (0.05, 0.05), (0.5, 0.05), (0.5, -0.05), 
        (0.05, -0.05), (0.05, -0.5), (-0.05, -0.5), (-0.05, -0.05)
    ],
}
for k, c in coords.items():
    Symbols[k].moveTo(*c[0])
    for x,y in c[1:]:
        Symbols[k].lineTo(x, y)
    Symbols[k].closeSubpath()

    
def drawSymbol(painter, symbol, size, pen, brush):
    painter.scale(size, size)
    painter.setPen(pen)
    painter.setBrush(brush)
    if isinstance(symbol, basestring):
        symbol = Symbols[symbol]
    if np.isscalar(symbol):
        symbol = Symbols.values()[symbol % len(Symbols)]
    painter.drawPath(symbol)

    
def renderSymbol(symbol, size, pen, brush, device=None):
    """
    Render a symbol specification to QImage.
    Symbol may be either a QPainterPath or one of the keys in the Symbols dict.
    If *device* is None, a new QPixmap will be returned. Otherwise,
    the symbol will be rendered into the device specified (See QPainter documentation 
    for more information).
    """
    ## see if this pixmap is already cached
    #global SymbolPixmapCache
    #key = (symbol, size, fn.colorTuple(pen.color()), pen.width(), pen.style(), fn.colorTuple(brush.color()))
    #if key in SymbolPixmapCache:
        #return SymbolPixmapCache[key]
        
    ## Render a spot with the given parameters to a pixmap
    penPxWidth = max(np.ceil(pen.width()), 1)
    image = QtGui.QImage(int(size+penPxWidth), int(size+penPxWidth), QtGui.QImage.Format_ARGB32)
    image.fill(0)
    p = QtGui.QPainter(image)
    p.setRenderHint(p.Antialiasing)
    p.translate(image.width()*0.5, image.height()*0.5)
    drawSymbol(p, symbol, size, pen, brush)
    p.end()
    return image
    #pixmap = QtGui.QPixmap(image)
    #SymbolPixmapCache[key] = pixmap
    #return pixmap

def makeSymbolPixmap(size, pen, brush, symbol):
    ## deprecated
    img = renderSymbol(symbol, size, pen, brush)
    return QtGui.QPixmap(img)
    
class SymbolAtlas:
    """
    Used to efficiently construct a single QPixmap containing all rendered symbols
    for a ScatterPlotItem. This is required for fragment rendering.
    
    Use example:
        atlas = SymbolAtlas()
        sc1 = atlas.getSymbolCoords('o', 5, QPen(..), QBrush(..))
        sc2 = atlas.getSymbolCoords('t', 10, QPen(..), QBrush(..))
        pm = atlas.getAtlas()
        
    """
    class SymbolCoords(list):  ## needed because lists are not allowed in weak references.
        pass
    
    def __init__(self):
        # symbol key : [x, y, w, h] atlas coordinates
        # note that the coordinate list will always be the same list object as 
        # long as the symbol is in the atlas, but the coordinates may
        # change if the atlas is rebuilt.
        # weak value; if all external refs to this list disappear, 
        # the symbol will be forgotten.
        self.symbolMap = weakref.WeakValueDictionary()
        
        self.atlasData = None # numpy array of atlas image
        self.atlas = None     # atlas as QPixmap
        self.atlasValid = False
        
    def getSymbolCoords(self, opts):
        """
        Given a list of spot records, return an object representing the coordinates of that symbol within the atlas
        """
        coords = np.empty(len(opts), dtype=object)
        for i, rec in enumerate(opts):
            symbol, size, pen, brush = rec['symbol'], rec['size'], rec['pen'], rec['brush']
            pen = fn.mkPen(pen) if not isinstance(pen, QtGui.QPen) else pen
            brush = fn.mkBrush(brush) if not isinstance(pen, QtGui.QBrush) else brush
            key = (symbol, size, fn.colorTuple(pen.color()), pen.width(), pen.style(), fn.colorTuple(brush.color()))
            if key not in self.symbolMap:
                newCoords = SymbolAtlas.SymbolCoords()
                self.symbolMap[key] = newCoords
                self.atlasValid = False
                #try:
                    #self.addToAtlas(key)  ## squeeze this into the atlas if there is room
                #except:
                    #self.buildAtlas()  ## otherwise, we need to rebuild
            
            coords[i] = self.symbolMap[key]
        return coords
        
    def buildAtlas(self):
        # get rendered array for all symbols, keep track of avg/max width
        rendered = {}
        avgWidth = 0.0
        maxWidth = 0
        images = []
        for key, coords in self.symbolMap.items():
            if len(coords) == 0:
                pen = fn.mkPen(color=key[2], width=key[3], style=key[4])
                brush = fn.mkBrush(color=key[5])
                img = renderSymbol(key[0], key[1], pen, brush)
                images.append(img)  ## we only need this to prevent the images being garbage collected immediately
                arr = fn.imageToArray(img, copy=False, transpose=False)
            else:
                (x,y,w,h) = self.symbolMap[key]
                arr = self.atlasData[x:x+w, y:y+w]
            rendered[key] = arr
            w = arr.shape[0]
            avgWidth += w
            maxWidth = max(maxWidth, w)
            
        nSymbols = len(rendered)
        if nSymbols > 0:
            avgWidth /= nSymbols
            width = max(maxWidth, avgWidth * (nSymbols**0.5))
        else:
            avgWidth = 0
            width = 0
        
        # sort symbols by height
        symbols = sorted(rendered.keys(), key=lambda x: rendered[x].shape[1], reverse=True)
        
        self.atlasRows = []

        x = width
        y = 0
        rowheight = 0
        for key in symbols:
            arr = rendered[key]
            w,h = arr.shape[:2]
            if x+w > width:
                y += rowheight
                x = 0
                rowheight = h
                self.atlasRows.append([y, rowheight, 0])
            self.symbolMap[key][:] = x, y, w, h
            x += w
            self.atlasRows[-1][2] = x
        height = y + rowheight

        self.atlasData = np.zeros((width, height, 4), dtype=np.ubyte)
        for key in symbols:
            x, y, w, h = self.symbolMap[key]
            self.atlasData[x:x+w, y:y+h] = rendered[key]
        self.atlas = None
        self.atlasValid = True
    
    def getAtlas(self):
        if not self.atlasValid:
            self.buildAtlas()
        if self.atlas is None:
            if len(self.atlasData) == 0:
                return QtGui.QPixmap(0,0)
            img = fn.makeQImage(self.atlasData, copy=False, transpose=False)
            self.atlas = QtGui.QPixmap(img)
        return self.atlas
        
    
    
    
class ScatterPlotItem(GraphicsObject):
    """
    Displays a set of x/y points. Instances of this class are created
    automatically as part of PlotDataItem; these rarely need to be instantiated
    directly.
    
    The size, shape, pen, and fill brush may be set for each point individually 
    or for all points. 
    
    
    ========================  ===============================================
    **Signals:**
    sigPlotChanged(self)      Emitted when the data being plotted has changed
    sigClicked(self, points)  Emitted when the curve is clicked. Sends a list
                              of all the points under the mouse pointer.
    ========================  ===============================================
    
    """
    #sigPointClicked = QtCore.Signal(object, object)
    sigClicked = QtCore.Signal(object, object)  ## self, points
    sigPlotChanged = QtCore.Signal(object)
    def __init__(self, *args, **kargs):
        """
        Accepts the same arguments as setData()
        """
        prof = debug.Profiler('ScatterPlotItem.__init__', disabled=True)
        GraphicsObject.__init__(self)
        
        self.picture = None   # QPicture used for rendering when pxmode==False
        self.fragments = None # fragment specification for pxmode; updated every time the view changes.
        self.fragmentAtlas = SymbolAtlas()
        
        self.data = np.empty(0, dtype=[('x', float), ('y', float), ('size', float), ('symbol', object), ('pen', object), ('brush', object), ('data', object), ('fragCoords', object), ('item', object)])
        self.bounds = [None, None]  ## caches data bounds
        self._maxSpotWidth = 0      ## maximum size of the scale-variant portion of all spots
        self._maxSpotPxWidth = 0    ## maximum size of the scale-invariant portion of all spots
        self.opts = {'pxMode': True, 'useCache': True}   ## If useCache is False, symbols are re-drawn on every paint.
        
        self.setPen(200,200,200, update=False)
        self.setBrush(100,100,150, update=False)
        self.setSymbol('o', update=False)
        self.setSize(7, update=False)
        prof.mark('1')
        self.setData(*args, **kargs)
        prof.mark('setData')
        prof.finish()
        
        #self.setCacheMode(self.DeviceCoordinateCache)
        
    def setData(self, *args, **kargs):
        """
        **Ordered Arguments:**
        
        * If there is only one unnamed argument, it will be interpreted like the 'spots' argument.
        * If there are two unnamed arguments, they will be interpreted as sequences of x and y values.
        
        ====================== ===============================================================================================
        **Keyword Arguments:**
        *spots*                Optional list of dicts. Each dict specifies parameters for a single spot:
                               {'pos': (x,y), 'size', 'pen', 'brush', 'symbol'}. This is just an alternate method
                               of passing in data for the corresponding arguments.
        *x*,*y*                1D arrays of x,y values.
        *pos*                  2D structure of x,y pairs (such as Nx2 array or list of tuples)
        *pxMode*               If True, spots are always the same size regardless of scaling, and size is given in px.
                               Otherwise, size is in scene coordinates and the spots scale with the view.
                               Default is True
        *symbol*               can be one (or a list) of:
                               * 'o'  circle (default)
                               * 's'  square
                               * 't'  triangle
                               * 'd'  diamond
                               * '+'  plus
                               * any QPainterPath to specify custom symbol shapes. To properly obey the position and size,
                               custom symbols should be centered at (0,0) and width and height of 1.0. Note that it is also
                               possible to 'install' custom shapes by setting ScatterPlotItem.Symbols[key] = shape.
        *pen*                  The pen (or list of pens) to use for drawing spot outlines.
        *brush*                The brush (or list of brushes) to use for filling spots.
        *size*                 The size (or list of sizes) of spots. If *pxMode* is True, this value is in pixels. Otherwise,
                               it is in the item's local coordinate system.
        *data*                 a list of python objects used to uniquely identify each spot.
        *identical*            *Deprecated*. This functionality is handled automatically now.
        ====================== ===============================================================================================
        """
        oldData = self.data  ## this causes cached pixmaps to be preserved while new data is registered.
        self.clear()  ## clear out all old data
        self.addPoints(*args, **kargs)

    def addPoints(self, *args, **kargs):
        """
        Add new points to the scatter plot. 
        Arguments are the same as setData()
        """
        
        ## deal with non-keyword arguments
        if len(args) == 1:
            kargs['spots'] = args[0]
        elif len(args) == 2:
            kargs['x'] = args[0]
            kargs['y'] = args[1]
        elif len(args) > 2:
            raise Exception('Only accepts up to two non-keyword arguments.')
        
        ## convert 'pos' argument to 'x' and 'y'
        if 'pos' in kargs:
            pos = kargs['pos']
            if isinstance(pos, np.ndarray):
                kargs['x'] = pos[:,0]
                kargs['y'] = pos[:,1]
            else:
                x = []
                y = []
                for p in pos:
                    if isinstance(p, QtCore.QPointF):
                        x.append(p.x())
                        y.append(p.y())
                    else:
                        x.append(p[0])
                        y.append(p[1])
                kargs['x'] = x
                kargs['y'] = y
        
        ## determine how many spots we have
        if 'spots' in kargs:
            numPts = len(kargs['spots'])
        elif 'y' in kargs and kargs['y'] is not None:
            numPts = len(kargs['y'])
        else:
            kargs['x'] = []
            kargs['y'] = []
            numPts = 0
        
        ## Extend record array
        oldData = self.data
        self.data = np.empty(len(oldData)+numPts, dtype=self.data.dtype)
        ## note that np.empty initializes object fields to None and string fields to ''
        
        self.data[:len(oldData)] = oldData
        #for i in range(len(oldData)):
            #oldData[i]['item']._data = self.data[i]  ## Make sure items have proper reference to new array
            
        newData = self.data[len(oldData):]
        newData['size'] = -1  ## indicates to use default size
        
        if 'spots' in kargs:
            spots = kargs['spots']
            for i in range(len(spots)):
                spot = spots[i]
                for k in spot:
                    #if k == 'pen':
                        #newData[k] = fn.mkPen(spot[k])
                    #elif k == 'brush':
                        #newData[k] = fn.mkBrush(spot[k])
                    if k == 'pos':
                        pos = spot[k]
                        if isinstance(pos, QtCore.QPointF):
                            x,y = pos.x(), pos.y()
                        else:
                            x,y = pos[0], pos[1]
                        newData[i]['x'] = x
                        newData[i]['y'] = y
                    elif k in ['x', 'y', 'size', 'symbol', 'pen', 'brush', 'data']:
                        newData[i][k] = spot[k]
                    #elif k == 'data':
                        #self.pointData[i] = spot[k]
                    else:
                        raise Exception("Unknown spot parameter: %s" % k)
        elif 'y' in kargs:
            newData['x'] = kargs['x']
            newData['y'] = kargs['y']
        
        if 'pxMode' in kargs:
            self.setPxMode(kargs['pxMode'])
            
        ## Set any extra parameters provided in keyword arguments
        for k in ['pen', 'brush', 'symbol', 'size']:
            if k in kargs:
                setMethod = getattr(self, 'set' + k[0].upper() + k[1:])
                setMethod(kargs[k], update=False, dataSet=newData)
        
        if 'data' in kargs:
            self.setPointData(kargs['data'], dataSet=newData)
        
        self.prepareGeometryChange()
        self.bounds = [None, None]
        self.invalidate()
        self.updateSpots(newData)
        self.sigPlotChanged.emit(self)
        
    def invalidate(self):
        ## clear any cached drawing state
        self.picture = None
        self.fragments = None
        self.update()
        
    def getData(self):
        return self.data['x'], self.data['y']
    
        
    def setPoints(self, *args, **kargs):
        ##Deprecated; use setData
        return self.setData(*args, **kargs)
        
    def implements(self, interface=None):
        ints = ['plotData']
        if interface is None:
            return ints
        return interface in ints
    
    def setPen(self, *args, **kargs):
        """Set the pen(s) used to draw the outline around each spot. 
        If a list or array is provided, then the pen for each spot will be set separately.
        Otherwise, the arguments are passed to pg.mkPen and used as the default pen for 
        all spots which do not have a pen explicitly set."""
        update = kargs.pop('update', True)
        dataSet = kargs.pop('dataSet', self.data)
        
        if len(args) == 1 and (isinstance(args[0], np.ndarray) or isinstance(args[0], list)):
            pens = args[0]
            if len(pens) != len(dataSet):
                raise Exception("Number of pens does not match number of points (%d != %d)" % (len(pens), len(dataSet)))
            dataSet['pen'] = pens
        else:
            self.opts['pen'] = fn.mkPen(*args, **kargs)
        
        dataSet['fragCoords'] = None
        if update:
            self.updateSpots(dataSet)
        
    def setBrush(self, *args, **kargs):
        """Set the brush(es) used to fill the interior of each spot. 
        If a list or array is provided, then the brush for each spot will be set separately.
        Otherwise, the arguments are passed to pg.mkBrush and used as the default brush for 
        all spots which do not have a brush explicitly set."""
        update = kargs.pop('update', True)
        dataSet = kargs.pop('dataSet', self.data)
            
        if len(args) == 1 and (isinstance(args[0], np.ndarray) or isinstance(args[0], list)):
            brushes = args[0]
            if len(brushes) != len(dataSet):
                raise Exception("Number of brushes does not match number of points (%d != %d)" % (len(brushes), len(dataSet)))
            #for i in xrange(len(brushes)):
                #self.data[i]['brush'] = fn.mkBrush(brushes[i], **kargs)
            dataSet['brush'] = brushes
        else:
            self.opts['brush'] = fn.mkBrush(*args, **kargs)
            #self._spotPixmap = None
        
        dataSet['fragCoords'] = None
        if update:
            self.updateSpots(dataSet)

    def setSymbol(self, symbol, update=True, dataSet=None):
        """Set the symbol(s) used to draw each spot. 
        If a list or array is provided, then the symbol for each spot will be set separately.
        Otherwise, the argument will be used as the default symbol for 
        all spots which do not have a symbol explicitly set."""
        if dataSet is None:
            dataSet = self.data
            
        if isinstance(symbol, np.ndarray) or isinstance(symbol, list):
            symbols = symbol
            if len(symbols) != len(dataSet):
                raise Exception("Number of symbols does not match number of points (%d != %d)" % (len(symbols), len(dataSet)))
            dataSet['symbol'] = symbols
        else:
            self.opts['symbol'] = symbol
            self._spotPixmap = None
        
        dataSet['fragCoords'] = None
        if update:
            self.updateSpots(dataSet)
    
    def setSize(self, size, update=True, dataSet=None):
        """Set the size(s) used to draw each spot. 
        If a list or array is provided, then the size for each spot will be set separately.
        Otherwise, the argument will be used as the default size for 
        all spots which do not have a size explicitly set."""
        if dataSet is None:
            dataSet = self.data
            
        if isinstance(size, np.ndarray) or isinstance(size, list):
            sizes = size
            if len(sizes) != len(dataSet):
                raise Exception("Number of sizes does not match number of points (%d != %d)" % (len(sizes), len(dataSet)))
            dataSet['size'] = sizes
        else:
            self.opts['size'] = size
            self._spotPixmap = None
            
        dataSet['fragCoords'] = None
        if update:
            self.updateSpots(dataSet)
        
    def setPointData(self, data, dataSet=None):
        if dataSet is None:
            dataSet = self.data
            
        if isinstance(data, np.ndarray) or isinstance(data, list):
            if len(data) != len(dataSet):
                raise Exception("Length of meta data does not match number of points (%d != %d)" % (len(data), len(dataSet)))
        
        ## Bug: If data is a numpy record array, then items from that array must be copied to dataSet one at a time.
        ## (otherwise they are converted to tuples and thus lose their field names.
        if isinstance(data, np.ndarray) and len(data.dtype.fields) > 1:
            for i, rec in enumerate(data):
                dataSet['data'][i] = rec
        else:
            dataSet['data'] = data
        
    def setPxMode(self, mode):
        if self.opts['pxMode'] == mode:
            return
            
        self.opts['pxMode'] = mode
        self.invalidate()
        
    def updateSpots(self, dataSet=None):
        if dataSet is None:
            dataSet = self.data
        self._maxSpotWidth = 0
        self._maxSpotPxWidth = 0
        invalidate = False
        self.measureSpotSizes(dataSet)
        if self.opts['pxMode']:
            mask = np.equal(dataSet['fragCoords'], None)
            if np.any(mask):
                invalidate = True
                opts = self.getSpotOpts(dataSet[mask])
                coords = self.fragmentAtlas.getSymbolCoords(opts)
                dataSet['fragCoords'][mask] = coords
                
            #for rec in dataSet:
                #if rec['fragCoords'] is None:
                    #invalidate = True
                    #rec['fragCoords'] = self.fragmentAtlas.getSymbolCoords(*self.getSpotOpts(rec))
        if invalidate:
            self.invalidate()

    def getSpotOpts(self, recs):
        if recs.ndim == 0:
            rec = recs
            symbol = rec['symbol']
            if symbol is None:
                symbol = self.opts['symbol']
            size = rec['size']
            if size < 0:
                size = self.opts['size']
            pen = rec['pen']
            if pen is None:
                pen = self.opts['pen']
            brush = rec['brush']
            if brush is None:
                brush = self.opts['brush']
            return (symbol, size, fn.mkPen(pen), fn.mkBrush(brush))
        else:
            recs = recs.copy()
            recs['symbol'][np.equal(recs['symbol'], None)] = self.opts['symbol']
            recs['size'][np.equal(recs['size'], -1)] = self.opts['size']
            recs['pen'][np.equal(recs['pen'], None)] = fn.mkPen(self.opts['pen'])
            recs['brush'][np.equal(recs['brush'], None)] = fn.mkBrush(self.opts['brush'])
            return recs
            
            
        
    def measureSpotSizes(self, dataSet):
        for rec in dataSet:
            ## keep track of the maximum spot size and pixel size
            symbol, size, pen, brush = self.getSpotOpts(rec)
            width = 0
            pxWidth = 0
            if self.opts['pxMode']:
                pxWidth = size + pen.width()
            else:
                width = size
                if pen.isCosmetic():
                    pxWidth += pen.width()
                else:
                    width += pen.width()
            self._maxSpotWidth = max(self._maxSpotWidth, width)
            self._maxSpotPxWidth = max(self._maxSpotPxWidth, pxWidth)
        self.bounds = [None, None]
    
    
    def clear(self):
        """Remove all spots from the scatter plot"""
        #self.clearItems()
        self.data = np.empty(0, dtype=self.data.dtype)
        self.bounds = [None, None]
        self.invalidate()

    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        if frac >= 1.0 and self.bounds[ax] is not None:
            return self.bounds[ax]
        
        #self.prepareGeometryChange()
        if self.data is None or len(self.data) == 0:
            return (None, None)
        
        if ax == 0:
            d = self.data['x']
            d2 = self.data['y']
        elif ax == 1:
            d = self.data['y']
            d2 = self.data['x']
        
        if orthoRange is not None:
            mask = (d2 >= orthoRange[0]) * (d2 <= orthoRange[1])
            d = d[mask]
            d2 = d2[mask]
            
        if frac >= 1.0:
            ## increase size of bounds based on spot size and pen width
            px = self.pixelLength(Point(1, 0) if ax == 0 else Point(0, 1))  ## determine length of pixel along this axis
            if px is None:
                px = 0
            minIndex = np.argmin(d)
            maxIndex = np.argmax(d)
            minVal = d[minIndex]
            maxVal = d[maxIndex]
            spotSize = 0.5 * (self._maxSpotWidth + px * self._maxSpotPxWidth)
            self.bounds[ax] = (minVal-spotSize, maxVal+spotSize)
            return self.bounds[ax]
        elif frac <= 0.0:
            raise Exception("Value for parameter 'frac' must be > 0. (got %s)" % str(frac))
        else:
            return (scipy.stats.scoreatpercentile(d, 50 - (frac * 50)), scipy.stats.scoreatpercentile(d, 50 + (frac * 50)))
            

    #def defaultSpotPixmap(self):
        ### Return the default spot pixmap
        #if self._spotPixmap is None:
            #self._spotPixmap = makeSymbolPixmap(size=self.opts['size'], brush=self.opts['brush'], pen=self.opts['pen'], symbol=self.opts['symbol'])
        #return self._spotPixmap

    def boundingRect(self):
        (xmn, xmx) = self.dataBounds(ax=0)
        (ymn, ymx) = self.dataBounds(ax=1)
        if xmn is None or xmx is None:
            xmn = 0
            xmx = 0
        if ymn is None or ymx is None:
            ymn = 0
            ymx = 0
        return QtCore.QRectF(xmn, ymn, xmx-xmn, ymx-ymn)

    def viewTransformChanged(self):
        self.prepareGeometryChange()
        GraphicsObject.viewTransformChanged(self)
        self.bounds = [None, None]
        self.fragments = None
        
    def generateFragments(self):
        tr = self.deviceTransform()
        if tr is None:
            return
        pts = np.empty((2,len(self.data['x'])))
        pts[0] = self.data['x']
        pts[1] = self.data['y']
        pts = fn.transformCoordinates(tr, pts)
        self.fragments = []
        for i in xrange(len(self.data)):
            rec = self.data[i]
            pos = QtCore.QPointF(pts[0,i], pts[1,i])
            x,y,w,h = rec['fragCoords']
            rect = QtCore.QRectF(y, x, h, w)
            self.fragments.append(QtGui.QPainter.PixmapFragment.create(pos, rect))
            
    def paint(self, p, *args):
        #p.setPen(fn.mkPen('r'))
        #p.drawRect(self.boundingRect())
        if self.opts['pxMode']:
            atlas = self.fragmentAtlas.getAtlas()
            #arr = fn.imageToArray(atlas.toImage(), copy=True)
            #if hasattr(self, 'lastAtlas'):
                #if np.any(self.lastAtlas != arr):
                    #print "Atlas changed:", arr
            #self.lastAtlas = arr
            
            if self.fragments is None:
                self.updateSpots()
                self.generateFragments()
                    
            p.resetTransform()
            
            if not USE_PYSIDE and self.opts['useCache']:
                p.drawPixmapFragments(self.fragments, atlas)
            else:
                for i in range(len(self.data)):
                    rec = self.data[i]
                    frag = self.fragments[i]
                    p.resetTransform()
                    p.translate(frag.x, frag.y)
                    drawSymbol(p, *self.getSpotOpts(rec))
        else:
            if self.picture is None:
                self.picture = QtGui.QPicture()
                p2 = QtGui.QPainter(self.picture)
                for rec in self.data:
                    
                    p2.resetTransform()
                    p2.translate(rec['x'], rec['y'])
                    drawSymbol(p2, *self.getSpotOpts(rec))
                p2.end()
                
            self.picture.play(p)

        
    def points(self):
        for rec in self.data:
            if rec['item'] is None:
                rec['item'] = SpotItem(rec, self)
        return self.data['item']
        
    def pointsAt(self, pos):
        x = pos.x()
        y = pos.y()
        pw = self.pixelWidth()
        ph = self.pixelHeight()
        pts = []
        for s in self.points():
            sp = s.pos()
            ss = s.size()
            sx = sp.x()
            sy = sp.y()
            s2x = s2y = ss * 0.5
            if self.opts['pxMode']:
                s2x *= pw
                s2y *= ph
            if x > sx-s2x and x < sx+s2x and y > sy-s2y and y < sy+s2y:
                pts.append(s)
                #print "HIT:", x, y, sx, sy, s2x, s2y
            #else:
                #print "No hit:", (x, y), (sx, sy)
                #print "       ", (sx-s2x, sy-s2y), (sx+s2x, sy+s2y)
        #pts.sort(lambda a,b: cmp(b.zValue(), a.zValue()))
        return pts[::-1]
            

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            pts = self.pointsAt(ev.pos())
            if len(pts) > 0:
                self.ptsClicked = pts
                self.sigClicked.emit(self, self.ptsClicked)
                ev.accept()
            else:
                #print "no spots"
                ev.ignore()
        else:
            ev.ignore()


class SpotItem(object):
    """
    Class referring to individual spots in a scatter plot.
    These can be retrieved by calling ScatterPlotItem.points() or 
    by connecting to the ScatterPlotItem's click signals.
    """

    def __init__(self, data, plot):
        #GraphicsItem.__init__(self, register=False)
        self._data = data
        self._plot = plot
        #self.setParentItem(plot)
        #self.setPos(QtCore.QPointF(data['x'], data['y']))
        #self.updateItem()
    
    def data(self):
        """Return the user data associated with this spot."""
        return self._data['data']
    
    def size(self):
        """Return the size of this spot. 
        If the spot has no explicit size set, then return the ScatterPlotItem's default size instead."""
        if self._data['size'] == -1:
            return self._plot.opts['size']
        else:
            return self._data['size']
    
    def pos(self):
        return Point(self._data['x'], self._data['y'])
        
    def viewPos(self):
        return self._plot.mapToView(self.pos())
    
    def setSize(self, size):
        """Set the size of this spot. 
        If the size is set to -1, then the ScatterPlotItem's default size 
        will be used instead."""
        self._data['size'] = size
        self.updateItem()
    
    def symbol(self):
        """Return the symbol of this spot. 
        If the spot has no explicit symbol set, then return the ScatterPlotItem's default symbol instead.
        """
        symbol = self._data['symbol']
        if symbol is None:
            symbol = self._plot.opts['symbol']
        try:
            n = int(symbol)
            symbol = list(Symbols.keys())[n % len(Symbols)]
        except:
            pass
        return symbol
    
    def setSymbol(self, symbol):
        """Set the symbol for this spot.
        If the symbol is set to '', then the ScatterPlotItem's default symbol will be used instead."""
        self._data['symbol'] = symbol
        self.updateItem()

    def pen(self):
        pen = self._data['pen']
        if pen is None:
            pen = self._plot.opts['pen']
        return fn.mkPen(pen)
    
    def setPen(self, *args, **kargs):
        """Set the outline pen for this spot"""
        pen = fn.mkPen(*args, **kargs)
        self._data['pen'] = pen
        self.updateItem()
    
    def resetPen(self):
        """Remove the pen set for this spot; the scatter plot's default pen will be used instead."""
        self._data['pen'] = None  ## Note this is NOT the same as calling setPen(None)
        self.updateItem()
    
    def brush(self):
        brush = self._data['brush']
        if brush is None:
            brush = self._plot.opts['brush']
        return fn.mkBrush(brush)
    
    def setBrush(self, *args, **kargs):
        """Set the fill brush for this spot"""
        brush = fn.mkBrush(*args, **kargs)
        self._data['brush'] = brush
        self.updateItem()
    
    def resetBrush(self):
        """Remove the brush set for this spot; the scatter plot's default brush will be used instead."""
        self._data['brush'] = None  ## Note this is NOT the same as calling setBrush(None)
        self.updateItem()
    
    def setData(self, data):
        """Set the user-data associated with this spot"""
        self._data['data'] = data

    def updateItem(self):
        self._data['fragCoords'] = None
        self._plot.updateSpots([self._data])
        self._plot.invalidate()

#class PixmapSpotItem(SpotItem, QtGui.QGraphicsPixmapItem):
    #def __init__(self, data, plot):
        #QtGui.QGraphicsPixmapItem.__init__(self)
        #self.setFlags(self.flags() | self.ItemIgnoresTransformations)
        #SpotItem.__init__(self, data, plot)
    
    #def setPixmap(self, pixmap):
        #QtGui.QGraphicsPixmapItem.setPixmap(self, pixmap)
        #self.setOffset(-pixmap.width()/2.+0.5, -pixmap.height()/2.)
    
    #def updateItem(self):
        #symbolOpts = (self._data['pen'], self._data['brush'], self._data['size'], self._data['symbol'])
        
        ### If all symbol options are default, use default pixmap
        #if symbolOpts == (None, None, -1, ''):
            #pixmap = self._plot.defaultSpotPixmap()
        #else:
            #pixmap = makeSymbolPixmap(size=self.size(), pen=self.pen(), brush=self.brush(), symbol=self.symbol())
        #self.setPixmap(pixmap)


#class PathSpotItem(SpotItem, QtGui.QGraphicsPathItem):
    #def __init__(self, data, plot):
        #QtGui.QGraphicsPathItem.__init__(self)
        #SpotItem.__init__(self, data, plot)

    #def updateItem(self):
        #QtGui.QGraphicsPathItem.setPath(self, Symbols[self.symbol()])
        #QtGui.QGraphicsPathItem.setPen(self, self.pen())
        #QtGui.QGraphicsPathItem.setBrush(self, self.brush())
        #size = self.size()
        #self.resetTransform()
        #self.scale(size, size)