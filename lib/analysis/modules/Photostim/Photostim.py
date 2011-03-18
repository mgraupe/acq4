# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from lib.analysis.AnalysisModule import AnalysisModule
import lib.analysis.modules.EventDetector as EventDetector
import MapCtrlTemplate
import DatabaseGui
from flowchart import *
import flowchart.library.EventDetection as FCEventDetection
import os
from advancedTypes import OrderedDict
import debug
import ColorMapper
import pyqtgraph as pg
import TreeWidget
#import FileLoader
import ProgressDialog

class Photostim(AnalysisModule):
    def __init__(self, host):
        AnalysisModule.__init__(self, host)
        self.dbIdentity = "Photostim"  ## how we identify to the database; this determines which tables we own
        self.selectedSpot = None


        ## setup analysis flowchart
        modPath = os.path.abspath(os.path.split(__file__)[0])
        flowchartDir = os.path.join(modPath, "analysis_fc")
        self.flowchart = Flowchart(filePath=flowchartDir)
        self.flowchart.addInput('events')
        self.flowchart.addInput('regions')
        self.flowchart.addInput('fileHandle')
        self.flowchart.addOutput('dataOut')
        self.analysisCtrl = self.flowchart.widget()
        
        ## color mapper
        self.mapper = ColorMapper.ColorMapper(filePath=os.path.join(modPath, "colormaps"))
        self.mapCtrl = QtGui.QWidget()
        self.mapLayout = QtGui.QVBoxLayout()
        self.mapCtrl.setLayout(self.mapLayout)
        self.recolorBtn = QtGui.QPushButton("Recolor")
        self.mapLayout.splitter = QtGui.QSplitter()
        self.mapLayout.splitter.setOrientation(0)
        self.mapLayout.splitter.setContentsMargins(0,0,0,0)
        self.mapLayout.addWidget(self.mapLayout.splitter)
        self.mapLayout.splitter.addWidget(self.analysisCtrl)
        #self.mapLayout.splitter.addWidget(QtGui.QSplitter())
        self.mapLayout.splitter.addWidget(self.mapper)
        self.mapLayout.splitter.addWidget(self.recolorBtn)
        
        ## scatter plot
        #self.scatterPlot = ScatterPlotter()
        #self.scatterPlot.sigPointClicked.connect(self.scatterPointClicked)
        
        ## setup map DB ctrl
        self.dbCtrl = DBCtrl(self, self.dbIdentity)
        
        ## storage for map data
        #self.scanItems = {}
        self.scans = {}
        self.seriesScans = {}
        self.maps = []
        
        ## create event detector
        fcDir = os.path.join(os.path.abspath(os.path.split(__file__)[0]), "detector_fc")
        self.detector = EventDetector.EventDetector(host, flowchartDir=fcDir, dbIdentity=self.dbIdentity+'.events')
        
        ## override some of its elements
        self.detector.setElement('File Loader', self)
        self.detector.setElement('Database', self.dbCtrl)
        
            
        ## Create element list, importing some gui elements from event detector
        elems = self.detector.listElements()
        self._elements_ = OrderedDict([
            ('Database', {'type': 'ctrl', 'object': self.dbCtrl, 'size': (200, 200)}),
            ('Canvas', {'type': 'canvas', 'pos': ('right',), 'size': (400,400), 'allowTransforms': False}),
            #('Scatter Plot', {'type': 'ctrl', 'object': self.scatterPlot, 'pos': ('below', 'Canvas'), 'size': (400,400)}),
            #('Maps', {'type': 'ctrl', 'pos': ('bottom', 'Database'), 'size': (200,200), 'object': self.mapDBCtrl}),
            ('Detection Opts', elems['Detection Opts'].setParams(pos=('bottom', 'Database'), size= (200,500))),
            ('File Loader', {'type': 'fileInput', 'size': (200, 200), 'pos': ('top', 'Database'), 'host': self, 'showFileTree': False}),
            ('Data Plot', elems['Data Plot'].setParams(pos=('bottom', 'Canvas'), size=(800,200))),
            ('Filter Plot', elems['Filter Plot'].setParams(pos=('bottom', 'Data Plot'), size=(800,200))),
            ('Event Table', elems['Output Table'].setParams(pos=('below', 'Filter Plot'), size=(800,200))),
            ('Stats', {'type': 'dataTree', 'size': (800,200), 'pos': ('below', 'Event Table')}),
            ('Map Opts', {'type': 'ctrl', 'object': self.mapCtrl, 'pos': ('left', 'Canvas'), 'size': (200,400)}),
        ])

        self.initializeElements()
        
        try:
            ## load default chart
            self.flowchart.loadFile(os.path.join(flowchartDir, 'default.fc'))
        except:
            debug.printExc('Error loading default flowchart:')
        
        
        self.detector.flowchart.sigOutputChanged.connect(self.detectorOutputChanged)
        self.flowchart.sigOutputChanged.connect(self.analyzerOutputChanged)
        self.detector.flowchart.sigStateChanged.connect(self.detectorStateChanged)
        self.flowchart.sigStateChanged.connect(self.analyzerStateChanged)
        self.recolorBtn.clicked.connect(self.recolor)
        
        
    def elementChanged(self, element, old, new):
        name = element.name()
        
        ## connect plots to flowchart, link X axes
        if name == 'File Loader':
            new.sigBaseChanged.connect(self.baseDirChanged)
            QtCore.QObject.connect(new.ui.dirTree, QtCore.SIGNAL('selectionChanged'), self.fileSelected)

    def fileSelected(self):
        fh = self.getElement('File Loader').ui.dirTree.selectedFile()
        if fh is not None and fh.isDir():
            print Scan.describe(self.dataModel, fh)


    def baseDirChanged(self, dh):
        typ = dh.info()['dirType']
        if typ == 'Slice':
            cells = [dh[d] for d in dh.subDirs() if dh[d].info().get('dirType',None) == 'Cell']
        elif typ == 'Cell':
            cells = [dh]
        else:
            return
        for cell in cells:
            self.dbCtrl.listMaps(cell)

            
    def loadFileRequested(self, fh):
        canvas = self.getElement('Canvas')
        try:
            if fh.isFile():
                canvas.addFile(fh)
            else:
                self.loadScan(fh)
            return True
        except:
            debug.printExc("Error loading file %s" % fh.name())
            return False
    
    def loadScan(self, fh):
        if fh not in self.scans and fh not in self.seriesScans:
            canvas = self.getElement('Canvas')
            canvasItem = canvas.addFile(fh)
            #scan = Scan(self, fh, canvasItem)
            #self.scanItems[fh] = scan
            if not isinstance(canvasItem, dict):
                scan = Scan(self, fh, canvasItem)
                self.scans[fh] = scan
                #node = QtGui.QTreeWidgetItem([scan.name()])
                #node.scan = scan
                #self.dbCtrl.scanTree.addTopLevelItem(node)
                canvasItem.item.sigPointClicked.connect(self.scanPointClicked)
                #scan.item.sigPointClicked.connect(self.scanPointClicked)
                
                #canvasItem.item.sigPointClicked.connect(self.scanPointClicked)
                #self.scatterPlot.addScan(scan)
                self.dbCtrl.scanLoaded(scan)
                return self.scans[fh]
            else:
                self.seriesScans[fh] = {}
                #pNode = QtGui.QTreeWidgetItem(self.dbCtrl.scanTree, [fh.shortName()])
                #pNode.setFlags((pNode.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsDragEnabled) & ~QtCore.Qt.ItemIsDropEnabled)
                #pNode.setCheckState(0, QtCore.Qt.Checked)
                #self.dbCtrl.scanTree.addTopLevelItem(QtGui.QTreeWidgetItem(fh.shortName()))
                for k in canvasItem.keys():
                    scan = Scan(self, fh, canvasItem[k], name=k)
                    self.seriesScans[fh][k] = scan
                    #scan[k].item.sigPointClicked.connect(self.scanPointClicked)
                    canvasItem[k].item.sigPointClicked.connect(self.scanPointClicked)
                    #node = QtGui.QTreeWidgetItem(pNode, [k])
                    #node.setFlags((node.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsDragEnabled) & ~QtCore.Qt.ItemIsDropEnabled)
                    #node.setCheckState(0, QtCore.Qt.Checked)
                    #node.scan = self.seriesScans[fh][k]
                    #self.scatterPlot.addScan(scan)
                    self.dbCtrl.scanLoaded(scan)
                #self.scatterPlot.addScan(self.seriesScans[fh])
                return self.seriesScans[fh]


    def registerMap(self, map):
        #if map in self.maps:
            #return
        canvas = self.getElement('Canvas')
        canvas.addItem(map.sPlotItem, name=map.name())
        self.maps.append(map)
        map.sPlotItem.sigPointClicked.connect(self.mapPointClicked)
        
    def unregisterMap(self, map):
        canvas = self.getElement('Canvas')
        canvas.removeItem(map.sPlotItem)
        self.maps.remove(map)
        map.sPlotItem.sigPointClicked.disconnect(self.mapPointClicked)
    

    def storeToDB(self):
        pass

    #def getClampFile(self, dh):
        #try:
            #return dh['Clamp2.ma']
        #except:
            #return dh['Clamp1.ma']

    def scanPointClicked(self, point):
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            #print "click!", point.data
            plot = self.getElement("Data Plot")
            plot.clear()
            self.selectedSpot = point
            #fh = self.getClampFile(point.data)
            fh = self.dataModel.getClampFile(point.data)
            self.detector.loadFileRequested(fh)
            #self.dbCtrl.scanSpotClicked(fh)
        finally:
            QtGui.QApplication.restoreOverrideCursor()
            
        
    def mapPointClicked(self, point):
        self.redisplayData(point.data)
        self.dbCtrl.mapSpotClicked(point.data)

    def scatterPointClicked(self, point):
        #scan, fh, time = point.data
        self.redisplayData([point.data])
        #self.scatterLine =

    def redisplayData(self, points):  ## data must be [(scan, fh), ...]
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            plot = self.getElement("Data Plot")
            plot.clear()
            eTable = self.getElement("Event Table")
            sTable = self.getElement("Stats")
            self.mapTicks = []
            
            #num = len(point.data)
            num = len(points)
            statList = []
            evList = []
            for i in range(num):
                color = pg.intColor(i, num)
                #scan, fh = point.data[i]
                scan, fh = points[i][:2]
                if isinstance(fh, basestring):
                    fh = scan.source[fh]
                
                ## plot all data, incl. events
                data = fh.read()['primary']
                pc = plot.plot(data, pen=color, clear=False)
                
                ## mark location of event
                if len(points[i]) == 3:
                    index = points[i][2]
                    pos = float(index)/len(data)
                    #print index
                    self.arrow = pg.CurveArrow(pc, pos=pos)
                    plot.addItem(self.arrow)
                
                ## show stats
                stats = scan.getStats(fh)
                statList.append(stats)
                events = scan.getEvents(fh)['events']
                evList.append(events)
                
                if len(events) > 0:
                    times = events['fitTime']
                    ticks = pg.VTickGroup(times, [0.0, 0.15], pen=color, relative=True, view=plot)
                    plot.addItem(ticks)
                    self.mapTicks.append(ticks)
            
            sTable.setData(statList)
            try:
                eTable.setData(np.concatenate(evList))
            except:
                print evList
                raise
        finally:
            QtGui.QApplication.restoreOverrideCursor()
    
    
    def detectorStateChanged(self):
        #print "STATE CHANGE"
        print "Detector state changed"
        for m in self.scans.itervalues():
            m.forgetEvents()
        for k in self.seriesScans.keys():
            for m in self.seriesScans[k].itervalues():
                m.forgetEvents()
        
    def detectorOutputChanged(self):
        output = self.detector.flowchart.output()
        output['fileHandle']=self.selectedSpot.data
        #table = self.getElement('Stats')
        #stats = self.detector.flowchart.output()['stats']
        #print stats
        #table.setData(stats)
        self.flowchart.setInput(**output)

    def analyzerStateChanged(self):
        print "Analyzer state changed."
        for m in self.scans.itervalues():
            #m.forgetEvents()
            m.forgetStats()
        for k in self.seriesScans.keys():
            for m in self.seriesScans[k].itervalues():
                #m.forgetEvents()
                m.forgetStats()
        
    def analyzerOutputChanged(self):
        table = self.getElement('Stats')
        stats = self.processStats()  ## gets current stats
        table.setData(stats)
        if stats is None:
            return
        self.mapper.setArgList(stats.keys())
        
    #def getCurrentStats(self):
        #stats = self.flowchart.output()['dataOut']
        #spot = self.selectedSpot
        #pos = spot.scenePos()
        #stats['xPos'] = pos.x()
        #stats['yPos'] = pos.y()
        #return stats
        
        
    def recolor(self):
        for i in range(len(self.scans)):
            s = self.scans[self.scans.keys()[i]]
            s.recolor(i, len(self.scans))
        for i in range(len(self.maps)):
            m = self.maps[i]
            m.recolor(self, i, len(self.maps))

    def getColor(self, stats):
        #print "STATS:", stats
        return self.mapper.getColor(stats)

    def processEvents(self, fh):
        print "Process Events:", fh
        return self.detector.process(fh)

    def processStats(self, data=None, spot=None, fh=None):
        if data is None:
            stats = self.flowchart.output()['dataOut']
            spot = self.selectedSpot
        else:
            if 'regions' not in data:
                data['regions'] = self.detector.flowchart.output()['regions']
            if 'fh' is None:
                data['fileHandle'] = self.selectedSpot.data
            else:
                data['fileHandle'] = fh
            stats = self.flowchart.process(**data)['dataOut']
            

        if stats is None:
            raise Exception('No data returned from analysis (check flowchart for errors).')
            
        pos = spot.scenePos()
        stats['xPos'] = pos.x()
        stats['yPos'] = pos.y()
        
        d = spot.data.parent()
        size = d.info().get('Scanner', {}).get('spotSize', 100e-6)
        stats['spotSize'] = size
        print "Process Stats:", spot.data
        
        return stats



    def storeDBSpot(self):
        """Stores data for selected spot immediately, using current flowchart outputs"""
        dbui = self.getElement('Database')
        #identity = self.dbIdentity+'.sites'
        #table = dbui.getTableName(identity)
        db = dbui.getDb()
        
        ## get events and stats for selected spot
        spot = self.selectedSpot
        if spot is None:
            raise Exception("No spot selected")
        #fh = self.getClampFile(spot.data)
        fh = self.dataModel.getClampFile(spot.data)
        print "Store spot:", fh
        parentDir = fh.parent()
        p2 = parentDir.parent()
        if db.dirTypeName(p2) == 'ProtocolSequence':
            parentDir = p2
            
        ## ask eventdetector to store events for us.
        #print parentDir
        self.detector.storeToDB(parentDir=parentDir)
        events = self.detector.output()

        ## store stats
        #stats = self.flowchart.output()['dataOut']
        stats = self.processStats(fh=parentDir)  ## gets current stats if no processing is requested
        
        self.storeStats(stats, fh, parentDir)
        
        
        ## update data in Map
        #try:
            #scan = self.scans[parentDir]
        #except KeyError:
            #scan = self.seriesScans[parentDir][fh]
        #scan.updateSpot(fh, events, stats)
        

    def selectedScan(self):
        loader = self.getElement('File Loader')
        dh = loader.selectedFile()
        scan = self.scans[dh]
        return scan

    def storeDBScan(self, scan):
        """Store all data for a scan, using cached values if possible"""
        #loader = self.getElement('File Loader')
        #dh = loader.selectedFile()
        #scan = self.scans[dh]
        dh = scan.source
        spots = scan.spots()
        print "Store scan:", dh.name()
        with ProgressDialog.ProgressDialog("Storing scan %s" % scan.name(), "Cancel", 0, len(spots)) as dlg:
            for i in xrange(len(spots)):
                s = spots[i]
                #fh = self.getClampFile(s.data)
                fh = self.dataModel.getClampFile(s.data)
                try:
                    ev = scan.getEvents(fh)['events']
                except:
                    print fh, scan.getEvents(fh)
                    raise
                st = scan.getStats(fh)
                self.detector.storeToDB(ev, dh)
                self.storeStats(st, fh, dh)
                dlg.setValue(i)
                if dlg.wasCanceled():
                    raise Exception("Scan store canceled by user.")
                
            print "   scan %s is now locked" % dh.name()
            scan.lock()

    def clearDBScan(self, scan):
        dbui = self.getElement('Database')
        db = dbui.getDb()
        #loader = self.getElement('File Loader')
        #dh = loader.selectedFile()
        #scan = self.scans[dh]
        dh = scan.source
        print "Clear scan", dh
        pRow = db.getDirRowID(dh)
        
        identity = self.dbIdentity+'.sites'
        table = dbui.getTableName(identity)
        db.delete(table, "SourceDir=%d" % pRow)
        
        identity = self.dbIdentity+'.events'
        table = dbui.getTableName(identity)
        db.delete(table, "SourceDir=%d" % pRow)
            
        scan.unlock()


    def storeStats(self, data, fh, parentDir):
        print "Store stats:", fh
        dbui = self.getElement('Database')
        identity = self.dbIdentity+'.sites'
        table = dbui.getTableName(identity)
        db = dbui.getDb()

        if db is None:
            raise Exception("No DB selected")

        pTable, pRow = db.addDir(parentDir)
        
        name = fh.name(relativeTo=parentDir)
        data = data.copy()  ## don't overwrite anything we shouldn't.. 
        data['SourceFile'] = name
        data['SourceDir'] = pRow
        
        ## determine the set of fields we expect to find in the table
        fields = OrderedDict([
            ('SourceDir', 'int'),
            ('SourceFile', 'text'),
        ])
        fields.update(db.describeData(data))
        
        ## Make sure target table exists and has correct columns, links to input file
        db.checkTable(table, owner=identity, fields=fields, links=[('SourceDir', pTable)], create=True)
        
        # delete old
        db.delete(table, "SourceDir=%d and SourceFile='%s'" % (pRow, name))

        # write new
        db.insert(table, data)

    def loadSpotFromDB(self, dh):
        dbui = self.getElement('Database')
        db = dbui.getDb()

        if db is None:
            raise Exception("No DB selected")
        
        #fh = self.getClampFile(dh)
        fh = self.dataModel.getClampFile(dh)
        parentDir = fh.parent()
        p2 = parentDir.parent()
        if db.dirTypeName(p2) == 'ProtocolSequence':
            parentDir = p2
            
        
        pRow = db.getDirRowID(parentDir)
        if pRow is None:
            return None, None
            
        identity = self.dbIdentity+'.sites'
        table = dbui.getTableName(identity)
        if not db.hasTable(table):
            return None, None
        stats = db.select(table, '*', "where SourceDir=%d and SourceFile='%s'" % (pRow, fh.name(relativeTo=parentDir)))
        
        identity = self.dbIdentity+'.events'
        table = dbui.getTableName(identity)
        if not db.hasTable(table):
            return None, None
        events = db.select(table, '*', "where SourceDir=%d and SourceFile='%s'" % (pRow, fh.name(relativeTo=parentDir)), toArray=True)
        
        if events is None:
            ## need to make an empty array with the correct fields
            schema = db.tableSchema(table)
            events = np.empty(0, dtype=[(k, object) for k in schema])
            
        
        return events, stats
        
    def getDb(self):
        dbui = self.getElement('Database')
        db = dbui.getDb()
        return db



class Scan(QtCore.QObject):
    
    sigEventsChanged = QtCore.Signal(object)
    sigLockChanged = QtCore.Signal(object)
    sigItemVisibilityChanged = QtCore.Signal(object)
    
    def __init__(self, host, source, canvasItem, name=None):
        QtCore.QObject.__init__(self)
        self.source = source
        self.canvasItem = canvasItem
        canvasItem.sigVisibilityChanged.connect(self.itemVisibilityChanged)
        self.item = canvasItem.graphicsItem()     ## graphics item
        self.host = host
        self.dataModel = host.dataModel
        self.givenName = name
        self._locked = False  ## prevents flowchart changes from clearing the cache--only individual updates allowed
        self.loadFromDB()
        self.spotDict = {}  ##  fh: spot
        
    def itemVisibilityChanged(self):
        self.sigItemVisibilityChanged.emit(self)
        
    def locked(self):
        return self._locked
        
    def lock(self, lock=True):
        if self.locked() == lock:
            return
        self._locked = lock
        self.sigLockChanged.emit(self)
    
    def unlock(self):
        self.lock(False)
        
    def name(self):
        if self.givenName == None:
            return self.source.shortName()
        else:
            return self.source.shortName() + self.givenName

    def rowId(self):
        db = self.host.getDb()
        table, rid = db.addDir(self.source)
        return rid

    def loadFromDB(self):
        print "Loading scan data for", self.source
        self.events = {}
        self.stats = {}
        self.statExample = None
        haveAll = True
        for spot in self.spots():
            dh = spot.data
            #fh = self.host.getClampFile(dh)
            fh = self.host.dataModel.getClampFile(dh)
            events, stats = self.host.loadSpotFromDB(dh)
            if stats is None or len(stats) == 0:
                print "  No data for spot", dh
                haveAll = False
                continue
            self.statExample = stats
            self.events[fh] = {'events': events}
            self.stats[fh] = stats[0]
        if haveAll:
            print "  have data for all spots; locking."
            self.lock()

    def getStatsKeys(self):
        if self.statExample is None:
            return None
        else:
            return self.statExample.keys()

    def forgetEvents(self):
        if not self.locked():
            print "Scan forget events:", self.source
            self.events = {}
            self.forgetStats()
        
    def forgetStats(self):
        #if not self.locked:
        print "Scan forget stats:", self.source
        self.stats = {}
        
    def recolor(self, n, nMax):
        if not self.item.isVisible():
            return
        spots = self.spots()
        with ProgressDialog.ProgressDialog("Computing spot colors (Scan %d/%d)" % (n+1,nMax), "Cancel", 0, len(spots)) as dlg:
        #progressDlg = QtGui.QProgressDialog("Computing spot colors (Map %d/%d)" % (n+1,nMax), "Cancel", 0, len(spots))
        #progressDlg.setWindowModality(QtCore.Qt.WindowModal)
        #progressDlg.setMinimumDuration(250)
        #try:
            ops = []
            for i in range(len(spots)):
                spot = spots[i]
                fh = self.host.dataModel.getClampFile(spot.data)
                stats = self.getStats(fh, signal=False)
                #print "stats:", stats
                color = self.host.getColor(stats)
                ops.append((spot, color))
                dlg.setValue(i+1)
                #QtGui.QApplication.processEvents()
                if dlg.wasCanceled():
                    raise Exception("Recolor canceled by user.")
        #except:
            #raise
        #finally:
            ### close progress dialog no matter what happens
            #progressDlg.setValue(len(spots))
        
        ## delay until the very end for speed.
        for spot, color in ops:
            spot.setBrush(color)
            
        self.sigEventsChanged.emit(self)  ## it's possible events didn't actually change, but meh.
        
        
            
    def getStats(self, fh, signal=True):
        #print "getStats", fh
        spot = self.getSpot(fh)
        #print "  got spot:", spot
        #except:
            #raise Exception("File %s is not in this scan" % fh.name())
        if fh not in self.stats:
            print "No stats cache for", fh.name(), "compute.."
            events = self.getEvents(fh, signal=signal)
            try:
                stats = self.host.processStats(events, spot, fh=fh)
            except:
                print events
                raise
            self.stats[fh] = stats
        return self.stats[fh]

    def getEvents(self, fh, process=True, signal=True):
        if fh not in self.events:
            if process:
                print "No event cache for", fh.name(), "compute.."
                events = self.host.processEvents(fh)
                self.events[fh] = events
                if signal:
                    self.sigEventsChanged.emit(self)
            else:
                return None
        return self.events[fh]
        
    def getAllEvents(self):
        #print "getAllEvents", self.name()
        events = []
        for fh in self.events:
            ev = self.getEvents(fh, process=False)
            if ev is not None and len(ev['events']) > 0:
                events.append(ev['events'])
            #else:
                #print "  ", fh, ev
        #if len(self.events) == 0:
            #print "self.events is empty"
        if len(events) > 0:
            return np.concatenate(events)
        else:
            #print "scan", self.name(), "has no pre-processed events"
            return None
        
    def spots(self):
        gi = self.item
        return gi.points()

    def updateSpot(self, fh, events, stats):
        self.events[fh] = events
        self.stats[fh] = stats

    def getSpot(self, fh):
        if fh not in self.spotDict:
            for s in self.spots():
                self.spotDict[self.host.dataModel.getClampFile(s.data)] = s
        return self.spotDict[fh]
    
    @staticmethod
    def describe(dataModel, source):
        '''Generates a big dictionary of parameters that describe a scan.'''
        rec = {}
        #source = source
        #sinfo = source.info()
        #if 'sequenceParams' in sinfo:
        if dataModel.isSequence(source):
            file = dataModel.getClampFile(source[source.ls()[0]])
            #first = source[source.ls()[0]]
        else:
            file = dataModel.getClampFile(source)
            #first = source
        
        #if next.exists('Clamp1.ma'):
            #cname = 'Clamp1'
            #file = next['Clamp1.ma']
        #elif next.exists('Clamp2.ma'):
            #cname = 'Clamp2'
            #file = next['Clamp2.ma']
        #else:
            #return {}
        
        if file == None:
            return {}
            
        #data = file.read()
        #info = data._info[-1]
        rec['mode'] = dataModel.getClampMode(file)
        rec['holding'] = dataModel.getClampHoldingLevel(file)
        
        #if 'ClampState' in info:
            #rec['mode'] = info['ClampState']['mode']
            #rec['holding'] = info['ClampState']['holding']
        #else:
            #try:
                #rec['mode'] = info['mode']
                #rec['holding'] = float(sinfo['devices'][cname]['holdingSpin'])*1000.
            #except:
                #pass
        
        #cell = source.parent()
        #day = cell.parent().parent()
        #dinfo = day.info()
        #rec['acsf'] = dinfo.get('solution', '')
        rec['acsf'] = dataModel.getACSF(file)
        #rec['internal'] = dinfo.get('internal', '')
        rec['internal'] = dataModel.getInternalSoln(file)
        
        #rec['temp'] = dinfo.get('temperature', '')
        rec['temp'] = dataModel.getTemp(file)
        
        #rec['cellType'] = cell.info().get('type', '')
        rec['cellType'] = dataModel.getCellType(file)
        
        #ninfo = next.info()
        #if 'Temperature.BathTemp' in ninfo:
            #rec['temp'] = ninfo['Temperature.BathTemp']
        return rec

        
class Map:
    mapFields = OrderedDict([
        ('cell', 'int'),
        ('scans', 'blob'),
        #('date', 'int'),
        #('name', 'text'),
        ('description', 'text'),
        ('cellType', 'text'),
        ('mode', 'text'),
        ('holding', 'real'),
        ('internal', 'text'),
        ('acsf', 'text'),
        ('drug', 'text'),
        ('temp', 'real'),
    ])
        
    def __init__(self, host, rec=None):
        self.host = host
        self.stubs = []      ## list of tuples (fh, treeItem, rowid) for scans that have not been loaded yet
        self.scans = []      ## list of Scan instances
        self.scanItems = {}  ## maps {scan: tree item}
        self.points = []         ## Holds all data: [ (position, [(scan, dh), ...], spotData), ... ]
        self.pointsByFile = {}   ## just a lookup dictionary
        self.spots = []          ## used to construct scatterplotitem
        self.sPlotItem = pg.ScatterPlotItem(pxMode=False)
        
        self.header = self.mapFields.keys()[2:]
        
        self.item = QtGui.QTreeWidgetItem([""] * len(self.header))
        self.item.setFlags(QtCore.Qt.ItemIsSelectable| QtCore.Qt.ItemIsEditable| QtCore.Qt.ItemIsEnabled)
        self.item.map = self
        self.item.setExpanded(True)
        self.rowID = None
        
        if rec is not None:
            self.rowID = rec['rowid']
            scans = rec['scans']
            #del rec['scans']
            #del rec['cell']
            for i in range(len(self.header)):
                self.item.setText(i, str(rec[self.header[i]]))
            for fh,rowid in scans:
                item = QtGui.QTreeWidgetItem([fh.shortName()])
                #print "Create scan stub:", fh
                self.stubs.append((fh, item, rowid))
                item.handle = fh
                self.item.addChild(item)

    def name(self, cell=None):
        rec = self.getRecord()
        if cell is None:
            cell = rec['cell']
        if cell is None:
            return ""
        name = cell.shortName()
        if rec['holding'] < -.04:
            name = name + "_excitatory"
        elif rec['holding'] >= -.01:
            name = name + "_inhibitory"
        return name

    def rebuildPlot(self):
        ## decide on point locations, build scatterplot
        self.points = []         ## Holds all data: [ (position, [(scan, dh), ...], spotData), ... ]
        self.pointsByFile = {}   ## just a lookup dictionary
        self.spots = []               ## used to construct scatterplotitem
        for scan in self.scans:  ## iterate over all points in all scans
            #if isinstance(scan, tuple):
                #continue    ## need to load before building
            self.addScanSpots(scan)
        self.sPlotItem.setPoints(self.spots)

    def addScanSpots(self, scan):
        for pt in scan.spots():
            pos = pt.scenePos()
            size = pt.boundingRect().width()
            added = False
            fh = self.host.dataModel.getClampFile(pt.data)
            for pt2 in self.points:     ## check all previously added points for position match
                pos2 = pt2[0]
                dp = pos2-pos
                dist = (dp.x()**2 + dp.y()**2)**0.5
                if dist < size/3.:      ## if position matches, add scan/spot data into existing site
                    pt2[1].append((scan, pt.data))
                    pt2[2]['data'].append((scan, fh))
                    added = True
                    self.pointsByFile[pt.data] = pt2
                    break
            if not added:               ## ..otherwise, add a new site
                self.spots.append({'pos': pos, 'size': size, 'data': [(scan, fh)]})
                self.points.append((pos, [(scan, fh)], self.spots[-1]))
                self.pointsByFile[pt.data] = self.points[-1]

    def addScan(self, scanList):
        for scan in scanList:
            if scan in self.scans:
                continue
                #raise Exception("Scan already present in this map.")
            
            if len(self.scans) == 0:
                ## auto-populate fields
                rec = self.generateDefaults(scan)
                for i in range(2, len(self.mapFields)):
                    ind = i-2
                    key = self.mapFields.keys()[i]
                    if key in rec and str(self.item.text(ind)) == '':
                        self.item.setText(ind, str(rec[key]))

            self.scans.append(scan)
            item = QtGui.QTreeWidgetItem([scan.name()])
            item.scan = scan
            self.item.addChild(item)
            self.item.setExpanded(True)
            
            self.scanItems[scan] = item

    def generateDefaults(self, scan):
        rec = {}
        source = scan.source
        sinfo = source.info()
        if 'sequenceParams' in sinfo:
            next = source[source.ls()[0]]
        else:
            next = source
        
        if next.exists('Clamp1.ma'):
            cname = 'Clamp1'
            file = next['Clamp1.ma']
        elif next.exists('Clamp2.ma'):
            cname = 'Clamp2'
            file = next['Clamp2.ma']
            
        data = file.read()
        info = data._info[-1]
        if 'ClampState' in info:
            rec['mode'] = info['ClampState']['mode']
            rec['holding'] = info['ClampState']['holding']
        else:  ## older meta-info format for MultiClamp
            rec['mode'] = info['mode']
            try:
                rec['holding'] = float(sinfo['devices'][cname]['holdingSpin'])*1000.
            except:
                pass
        
        cell = source.parent()
        day = cell.parent().parent()
        dinfo = day.info()
        rec['acsf'] = dinfo.get('solution', '')
        rec['internal'] = dinfo.get('internal', '')
        rec['temp'] = dinfo.get('temperature', '')
        
        rec['cellType'] = cell.info().get('type', '')
        
        ninfo = next.info()
        if 'Temperature.BathTemp' in ninfo:
            rec['temp'] = ninfo['Temperature.BathTemp']
        rec['description'] = self.name(source.parent())
        return rec


    def removeScan(self, scan):
        self.scans.remove(scan)
        item = self.scanItems[scan]
        self.item.removeChild(item)
        
    def getRecord(self):
        ### Create a dictionary with all the record data for this map. 
        
        rec = {}
        i = 0
        for k in self.mapFields:
            if k == 'scans':  ## list of row IDs of the scans included in this map
                rowids = []
                for s in self.stubs:
                    rowids.append(s[2])
                for s in self.scans:
                    rowids.append(s.rowId())
                rec[k] = rowids
            elif k == 'cell':   ## decide which cell this map belongs to. 
                if len(self.scans) == 0 and len(self.stubs) == 0:
                    rec[k] = None
                else:
                    if len(self.scans) > 0:
                        rec[k] = self.scans[0].source.parent()
                    else:
                        rec[k] = self.stubs[0][0].parent()
                        
                    #if isinstance(s, tuple):
                        #rec[k] = s[0].parent()
                    #else:
                        #rec[k] = self.scans[0].source.parent()
            else:
                rec[k] = str(self.item.text(i))
                if self.mapFields[k] == 'real':
                    try:
                        num = rec[k].replace('C', '')  ## convert to numerical value (by stripping units)
                        rec[k] = float(num)
                    except:
                        pass
                i += 1
        return rec
        
            
    def recolor(self, host, n, nMax):
        if not self.sPlotItem.isVisible():
            return
        spots = self.sPlotItem.points()
        colors = []
        with ProgressDialog.ProgressDialog("Computing map %s (%d/%d)" % (self.name(), n, nMax), "Cancel", 0, len(spots)) as dlg:
            for i in xrange(len(spots)):
                s = spots[i]
                data = []
                sources = s.data
                for scan, dh in sources:
                    data.append(scan.getStats(dh))
                
                if len(data) == 0:
                    continue
                if len(data) == 1:
                    mergeData = data[0]
                else:
                    mergeData = {}
                    for k in data[0]:
                        vals = [d[k] for d in data if k in d]
                        try:
                            if len(data) == 2:
                                mergeData[k] = np.mean(vals)
                            elif len(data) > 2:
                                mergeData[k] = np.median(vals)
                            elif len(data) == 1:
                                mergeData[k] = vals[0]
                            else:
                                mergeData[k] = 0
                        except:
                            mergeData[k] = vals[0]
                #print mergeData
                color = host.getColor(mergeData)
                #s.setBrush(color)  ## wait until after to set the colors
                colors.append((s, color))
                dlg.setValue(i)
                if dlg.wasCanceled():
                    raise Exception("Process canceled by user.")
                
        for s, c in colors:
            s.setColor(c)


class DBCtrl(QtGui.QWidget):
    """Interface for reading and writing to the database.
    A map consists of one or more (probably overlapping) scans and associated meta-data."""
    def __init__(self, host, identity):
        QtGui.QWidget.__init__(self)
        self.host = host
        self.dbIdentity = identity
        
        ## DB tables we will be using  {owner: defaultTableName}
        tables = OrderedDict([
            (self.dbIdentity+'.maps', 'Photostim_maps'),
            (self.dbIdentity+'.sites', 'Photostim_sites'),
            (self.dbIdentity+'.events', 'Photostim_events')
        ])
        self.maps = []
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        self.dbgui = DatabaseGui.DatabaseGui(dm=host.dataManager(), tables=tables)
        self.layout.addWidget(self.dbgui)
        for name in ['getTableName', 'getDb']:
            setattr(self, name, getattr(self.dbgui, name))
        #self.scanTree = TreeWidget.TreeWidget()
        #self.layout.addWidget(self.scanTree)
        self.ui = MapCtrlTemplate.Ui_Form()
        self.mapWidget = QtGui.QWidget()
        self.ui.setupUi(self.mapWidget)
        self.layout.addWidget(self.mapWidget)
        
        
        labels = Map.mapFields.keys()[2:]
        self.ui.mapTable.setHeaderLabels(labels)
        self.ui.mapTable.itemChanged.connect(self.mapItemChanged)
        
        self.ui.newMapBtn.clicked.connect(self.newMapClicked)
        self.ui.loadMapBtn.clicked.connect(self.loadMapClicked)
        self.ui.delMapBtn.clicked.connect(self.delMapClicked)
        self.ui.addScanBtn.clicked.connect(self.addScanClicked)
        self.ui.removeScanBtn.clicked.connect(self.removeScanClicked)
        self.ui.clearDBSpotBtn.clicked.connect(self.clearDBSpot)
        self.ui.storeDBSpotBtn.clicked.connect(self.storeDBSpot)
        self.ui.clearDBScanBtn.clicked.connect(self.clearDBScan)
        self.ui.storeDBScanBtn.clicked.connect(self.storeDBScan)
        self.ui.scanTree.itemChanged.connect(self.scanTreeItemChanged)

    def scanLoaded(self, scan):
        ## Scan has been loaded, add a new item into the scanTree
        item = QtGui.QTreeWidgetItem([scan.name(), '', ''])
        self.ui.scanTree.addTopLevelItem(item)
        scan.scanTreeItem = item
        item.scan = scan
        item.setCheckState(2, QtCore.Qt.Checked)
        scan.sigLockChanged.connect(self.scanLockChanged)
        self.scanLockChanged(scan)
        scan.sigItemVisibilityChanged.connect(self.scanItemVisibilityChanged)
        
    def scanTreeItemChanged(self, item, col):
        if col == 2:
            vis = item.checkState(col) == QtCore.Qt.Checked
            scan = item.scan
            ci = scan.canvasItem
            ci.setVisible(vis)
        
    def scanLockChanged(self, scan):
        ## scan has been locked/unlocked (or newly loaded), update the indicator in the scanTree
        item = scan.scanTreeItem
        if scan.locked():
            item.setText(1, 'Yes')
        else:
            item.setText(1, 'No')
            
    def scanItemVisibilityChanged(self, scan):
        treeItem = scan.scanTreeItem
        cItem = scan.canvasItem
        checked = treeItem.checkState(2) == QtCore.Qt.Checked
        vis = cItem.isVisible()
        if vis == checked:
            return
        if vis:
            treeItem.setCheckState(2, QtCore.Qt.Checked)
        else:
            treeItem.setCheckState(2, QtCore.Qt.Unchecked)
            

    def newMap(self, rec=None):
        m = Map(self.host, rec)
        self.maps.append(m)
        item = m.item
        self.ui.mapTable.addTopLevelItem(item)
        self.ui.mapTable.setCurrentItem(item)

    def mapItemChanged(self, item, col):
        self.writeMapRecord(item.map)
        

    def writeMapRecord(self, map):
        dbui = self.host.getElement('Database')
        db = dbui.getDb()
        if db is None:
            return
            
        ident = self.dbIdentity+'.maps'
        table = dbui.getTableName(ident)
        
        rec = map.getRecord()
        cell = rec['cell']
        if cell is not None:
            pt, rid = db.addDir(cell)
            rec['cell'] = rid
        if rec['cell'] is None:
            return
        
        #fields = db.describeData(rec)
        #fields['cell'] = 'int'
        db.checkTable(table, ident, Map.mapFields, [('cell', 'Cell')], create=True)
        
        if map.rowID is None:
            db.insert(table, rec)
            map.rowID = db.lastInsertRow()
        else:
            rec['rowid'] = map.rowID
            db.insert(table, rec, replaceOnConflict=True)

    def deleteMap(self, map):
        item = map.item
        self.ui.mapTable.takeTopLevelItem(self.ui.mapTable.indexOfTopLevelItem(item))
        rowID = map.rowID
        if rowID is None:
            return
        
        dbui = self.host.getElement('Database')
        db = dbui.getDb()
        if db is None:
            raise Exception("No DB Loaded.")
            
        ident = self.dbIdentity+'.maps'
        table = dbui.getTableName(ident)
        if db.tableOwner(table) != ident:
            raise Exception("Table %s not owned by %s" % (table, ident))
        
        db.delete(table, 'rowid=%d'%rowID)
        
        self.host.unregisterMap(map)
        

    def listMaps(self, cell):
        """List all maps associated with the file handle for cell"""
        dbui = self.host.getElement('Database')
        db = dbui.getDb()
        if db is None:
            raise Exception("No DB Loaded.")
            
        ident = self.dbIdentity+'.maps'
        table = dbui.getTableName(ident)
        if not db.hasTable(table):
            return
        if db.tableOwner(table) != ident:
            raise Exception("Table %s not owned by %s" % (table, ident))
        
        row = db.getDirRowID(cell)
        if row is None:
            return
            
        maps = db.select(table, ['rowid','*'], 'where cell=%d'%row)
        #print maps
        for rec in maps:
            scans = []
            for rowid in rec['scans']:
                fh = db.getDir('ProtocolSequence', rowid)    ## NOTE: single-spot maps use a different table!
                scans.append((fh, rowid))
            rec['scans'] = scans
            self.newMap(rec)


    def loadMap(self, map):
        ## turn scan stubs into real scans
        rscans = []
        for i in range(len(map.stubs)):
            stub = map.stubs[i]
            #if not isinstance(scan, tuple):  ## scan is already loaded, skip
                #rscans.append(scan)
                #continue
            newScan = self.host.loadScan(stub[0])
            #newScan.item = scan[1]
            treeItem = stub[1]
            treeItem.scan = newScan
            rscans.append(newScan)
            map.scanItems[newScan] = treeItem
        map.scans = rscans
        map.stubs = []
            
        ## decide on point set, generate scatter plot 
        map.rebuildPlot()
        
        self.host.registerMap(map)

        
        



    def newMapClicked(self):
        ## Create a new map in the database
        try:
            self.newMap()
            self.ui.newMapBtn.success("OK.")
        except:
            self.ui.newMapBtn.failure("Error.")
            raise
        
        pass
    
    def loadMapClicked(self):
        try:
            map = self.selectedMap()
            self.loadMap(map)
            self.ui.loadMapBtn.success("OK.")
        except:
            self.ui.loadMapBtn.failure("Error.")
            raise
    
    def delMapClicked(self):
        try:
            map = self.selectedMap()
            self.deleteMap(map)
            self.ui.addScanBtn.success("Deleted.")
        except:
            self.ui.addScanBtn.failure("Error.")
            raise
        
    #def getSelectedScanFromScanTree(self):
        #"""Needs to return a list of scans."""
        #if self.scanTree.currentItem().childCount() == 0:
            #scan = self.scanTree.currentItem().scan
            #return [scan]
        #else:
            #scans = []
            #for i in range(self.scanTree.currentItem().childCount()):
                #scan = self.scanTree.currentItem().child(i).scan
                #scans.append(scan)
            #return scans
        
    def addScanClicked(self):
        try:
            #scan = self.getSelectedScanFromScanTree()
            scan = self.selectedScan()
            map = self.selectedMap()
            map.addScan(scan)
            self.writeMapRecord(map)
            map.rebuildPlot()
            self.ui.addScanBtn.success("OK.")
        except:
            self.ui.addScanBtn.failure("Error.")
            raise
    
    def removeScanClicked(self):
        try:
            item = self.ui.mapTable.currentItem()
            scan = item.scan
            map = item.parent().map
            map.removeScan(scan)
            self.writeMapRecord(map)
            map.rebuildPlot()
            self.ui.removeScanBtn.success("OK.")
        except:
            self.ui.removeScanBtn.failure("Error.")
            raise
        
    def clearDBSpot(self):
        ## remove all events referencing this spot
        ## remove stats for this spot
        pass
    
    def storeDBSpot(self):
        try:
            self.host.storeDBSpot()
            self.ui.storeDBSpotBtn.success("Stored.")
        except:
            self.ui.storeDBSpotBtn.failure("Error.")
            raise
        
    def selectedMap(self):
        item = self.ui.mapTable.currentItem()
        if not hasattr(item, 'map'):
            item = item.parent()
        return item.map
        
    def selectedScan(self):
        item = self.ui.scanTree.currentItem()
        #if not hasattr(item, 'scan'):
            #return None
        return item.scan
        
    
    def clearDBScan(self):
        try:
            scan = self.selectedScan()
            if scan is None:
                raise Exception("No scan selected.")
            self.host.clearDBScan(scan)
            self.ui.clearDBScanBtn.success("Cleared.")
        except:
            self.ui.clearDBScanBtn.failure("Error.")
            raise
    
    def storeDBScan(self):
        try:
            scan = self.selectedScan()
            if scan is None:
                raise Exception("No scan selected.")
            self.host.storeDBScan(scan)
            self.ui.storeDBScanBtn.success("Stored.")
        except:
            self.ui.storeDBScanBtn.failure("Error.")
            raise
    



class ScatterPlotter(QtGui.QSplitter):
    
    sigPointClicked = QtCore.Signal(object)
    
    def __init__(self):
        QtGui.QSplitter.__init__(self)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.plot = pg.PlotWidget()
        self.addWidget(self.plot)
        self.ctrl = QtGui.QWidget()
        self.addWidget(self.ctrl)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.ctrl.setLayout(self.layout)
        
        self.scanList = TreeWidget.TreeWidget()
        self.layout.addWidget(self.scanList)
        
        self.filter = FCEventDetection.EventFilter('eventFilter')
        self.layout.addWidget(self.filter.ctrlWidget())
        
        self.xCombo = QtGui.QComboBox()
        self.yCombo = QtGui.QComboBox()
        self.layout.addWidget(self.xCombo)
        self.layout.addWidget(self.yCombo)
        
        self.columns = []
        self.scans = {}    ## maps scan: (scatterPlotItem, treeItem)
        
        self.xCombo.currentIndexChanged.connect(self.updateAll)
        self.yCombo.currentIndexChanged.connect(self.updateAll)
        self.filter.sigStateChanged.connect(self.updateAll)
        self.scanList.itemChanged.connect(self.itemChanged)

    def itemChanged(self, item, col):
        gi = self.scans[item.scan][0]
        if item.checkState(0) == QtCore.Qt.Checked:
            gi.show()
        else:
            gi.hide()



    def addScan(self, scanDict):
        plot = pg.ScatterPlotItem(pen=QtGui.QPen(QtCore.Qt.NoPen), brush=pg.mkBrush((255, 255, 255, 100)))
        self.plot.addDataItem(plot)
        
        if not isinstance(scanDict, dict):
            scanDict = {'key':scanDict}
        #print "Adding:", scan.name
        for scan in scanDict.values():
            item = QtGui.QTreeWidgetItem([scan.name()])
            item.setCheckState(0, QtCore.Qt.Checked)
            item.scan = scan
            self.scanList.addTopLevelItem(item)
            self.scans[scan] = (plot, item)
            self.updateScan(scan)
            scan.sigEventsChanged.connect(self.updateScan)
    
    def updateScan(self, scan):
        try:
            self.updateColumns(scan)
            x, y = self.getAxes()
            plot = self.scans[scan][0]
            data = scan.getAllEvents()
            if data is None:
                plot.setPoints([])
                return
                
            data = self.filter.process(data, {})
            
            pts = [{'pos': (data['output'][i][x], data['output'][i][y]), 'data': (scan, data['output'][i]['SourceFile'], data['output'][i]['index'])} for i in xrange(len(data))]
            plot.setPoints(pts)
            
            plot.sigPointClicked.connect(self.pointClicked)
        except:
            debug.printExc("Error updating scatter plot:")
        
    def pointClicked(self, point):
        self.sigPointClicked.emit(point)
    
    def updateAll(self):
        for s in self.scans:
            if self.scans[s][1].checkState(0) == QtCore.Qt.Checked:
                self.updateScan(s)
    
    def updateColumns(self, scan):
        ev = scan.getAllEvents()
        if ev is None:
            return
        cols = ev.dtype.names
        for c in cols:
            if c not in self.columns:
                self.xCombo.addItem(c)
                self.yCombo.addItem(c)
        for c in self.columns:
            if c not in cols:
                ind = self.xCombo.findText(c)
                self.xCombo.removeItem(ind)
                self.yCombo.removeItem(ind)
        self.columns = cols
    
    def getAxes(self):
        return str(self.xCombo.currentText()), str(self.yCombo.currentText())
    