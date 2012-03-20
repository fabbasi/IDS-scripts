"""
<name>MDS Qt</name>
<description>Multi dimensional scaling (Qt)</description>
<icon>icons/MDS.png</icon>
<contact>Ales Erjavec (ales.erjavec(@at@)fri.uni-lj.si)</contact>
<priority>2500</priority>
"""

from OWWidget import *
import Orange
import orange
import orngMDS
import OWGUI
import numpy, sys, math, time, os
import OWColorPalette
import OWToolbars
#from OWGraph import *
#from PyQt4.Qwt5 import *

from OrangeWidgets.plot.owplot import OWPlot, OWCurve
from OrangeWidgets.plot.owpoint import OWPoint

from random import random


class OWMDSQt(OWWidget):
    settingsList=["graph.PointSize", "graph.proportionGraphed", "graph.ColorAttr", "graph.SizeAttr",
                  "graph.ShapeAttr", "graph.NameAttr", "graph.ShowStress", "graph.NumStressLines",
                  "graph.ShowName", "graph.differentWidths", "graph.stressByTransparency", "graph.useAntialiasing"
                  "StressFunc", "applyLSMT", "toolbarSelection", "autoSendSelection", "selectionOptions", "computeStress",
                  "RefreshMode"]
    contextHandlers={"":DomainContextHandler("", [ContextField("graph.ColorAttr", DomainContextHandler.Optional),
                                                  ContextField("graph.SizeAttr", DomainContextHandler.Optional),
                                                  ContextField("graph.ShapeAttr", DomainContextHandler.Optional),
                                                  ContextField("graph.NameAttr", DomainContextHandler.Optional),
                                                  ContextField("graph.ShowName", DomainContextHandler.Optional)])}
    
    def __init__(self, parent=None, signalManager=None, name="Multi Dimensional Scaling"):
        OWWidget.__init__(self, parent, signalManager, name, wantGraph=True)
        self.inputs=[("Distances", orange.SymMatrix, self.cmatrix), ("Data Subset", ExampleTable, self.cselected)]
        self.outputs=[("Data", ExampleTable)]

        self.StressFunc=3
        self.minStressDelta=5e-5
        self.maxIterations=5000
        self.maxImprovment=10
        self.autoSendSelection=0
        self.toolbarSelection=0
        self.selectionOptions=0
        self.computeStress=1
        self.ReDraw=1
        self.NumIter=1
        self.RefreshMode=0
        self.applyLSMT = 0

        self.stressFunc=[("Kruskal stress", orngMDS.KruskalStress),
                              ("Sammon stress", orngMDS.SammonStress),
                              ("Signed Sammon stress", orngMDS.SgnSammonStress),
                              ("Signed relative stress", orngMDS.SgnRelStress)]
        
        self.graph=MDSPlot(self.mainArea)
        self.mainArea.layout().addWidget(self.graph)
        
        self.loadSettings()

        tabs=OWGUI.tabWidget(self.controlArea)
        
        mds=OWGUI.createTabPage(tabs, "MDS")
        graph=OWGUI.createTabPage(tabs, "Graph")

        ##MDS Tab        
        init=OWGUI.widgetBox(mds, "Initialization")
        OWGUI.button(init, self, "Randomize", self.randomize)
        OWGUI.button(init, self, "Jitter", self.jitter)
        OWGUI.button(init, self, "Torgerson", self.torgerson)
        opt=OWGUI.widgetBox(mds, "Optimization")

        self.startButton=OWGUI.button(opt, self, "Optimize", self.testStart)
        OWGUI.button(opt, self, "Single Step", self.smacofStep)
        box = OWGUI.widgetBox(opt, "Stress Function")
        OWGUI.comboBox(box, self, "StressFunc", items=[a[0] for a in self.stressFunc], callback=self.updateStress)        
        OWGUI.radioButtonsInBox(opt, self, "RefreshMode", ["Every step", "Every 10 steps", "Every 100 steps"], "Refresh During Optimization", callback=lambda :1)
        
        self.stopping=OWGUI.widgetBox(opt, "Stopping Conditions")
        OWGUI.hSlider(OWGUI.widgetBox(self.stopping, "Min. stress change", flat=True),
                      self, "minStressDelta", minValue=5e-5, maxValue=1e-2, step=5e-5, 
                      labelFormat="%.5f", intOnly=0)
        OWGUI.hSlider(OWGUI.widgetBox(self.stopping, "Max. number of steps", flat=True), 
                      self, "maxIterations", minValue=10, maxValue=5000, step=10, 
                      labelFormat="%i")

        ##Graph Tab        
        OWGUI.hSlider(graph, self, "graph.PointSize", box="Point Size", minValue=1, maxValue=20, callback=self.graph.updateData)
        self.colorCombo=OWGUI.comboBox(graph, self, "graph.ColorAttr", box="Color", callback=self.graph.updateData)
        self.sizeCombo=OWGUI.comboBox(graph, self, "graph.SizeAttr", box="Size", callback=self.graph.updateData)
        self.shapeCombo=OWGUI.comboBox(graph, self, "graph.ShapeAttr", box="Shape", callback=self.graph.updateData)
        self.nameCombo=OWGUI.comboBox(graph, self, "graph.NameAttr", box="Label", callback=self.graph.updateData)
        
        box = OWGUI.widgetBox(graph, "Distances & Stress")
        OWGUI.checkBox(box, self, "graph.ShowStress", "Show similar pairs", callback = self.graph.updateLinesRepaint)
        b2 = OWGUI.widgetBox(box)
        OWGUI.widgetLabel(b2, "Proportion of connected pairs")
        OWGUI.separator(b2, height=3)
        sl = OWGUI.hSlider(b2, self, "graph.proportionGraphed", minValue=0, maxValue=20, callback=self.graph.updateLinesRepaint, tooltip="Proportion of connected pairs (Maximum of 1000 lines will be drawn")
        OWGUI.checkBox(box, self, "graph.differentWidths", "Show distance by line width", callback = self.graph.updateLinesRepaint)
        OWGUI.checkBox(box, self, "graph.stressByTransparency", "Show stress by transparency", callback = self.graph.updateData)
        OWGUI.checkBox(box, self, "graph.stressBySize", "Show stress by symbol size", callback = self.updateStressBySize)
        self.updateStressBySize(True)
        
        OWGUI.checkBox(graph, self, "graph.antialias_points", label="Use antialiasing", box="Antialiasing", tooltip="Use antialiasing for beter quality graphics", callback=self.graph.updateData)

        self.zoomToolbar=OWToolbars.ZoomSelectToolbar(self, graph, self.graph, self.autoSendSelection)
        self.connect(self.zoomToolbar.buttonSendSelections, SIGNAL("clicked()"), self.sendSelections)
        self.graph.autoSendSelectionCallback = lambda :self.autoSendSelection and self.sendSelections()

        OWGUI.checkBox(graph, self, "autoSendSelection", "Auto send selected")
        OWGUI.radioButtonsInBox(graph, self, "selectionOptions", ["Don't append", "Append coordinates", "Append coordinates as meta"], box="Append coordinates", callback=self.sendIf)

        mds.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        graph.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.controlArea.setMinimumWidth(250)
        
        OWGUI.rubber(mds)
        OWGUI.rubber(self.controlArea)
        
        infoBox=OWGUI.widgetBox(mds, "Info")
        self.infoA=OWGUI.widgetLabel(infoBox, "Avg. stress:")
        self.infoB=OWGUI.widgetLabel(infoBox, "Num. steps")
#        OWGUI.button(self.controlArea, self, "Save", self.graph.saveToFile, debuggingEnabled = 0)
        self.connect(self.graphButton, SIGNAL("clicked()"), self.graph.saveToFile)
        self.resize(900,630)

        self.done=True
        self.data=None
        self.selectedInputExamples=[]
        self.selectedInput=[]

    def cmatrix(self, matrix=None):
        self.closeContext()
        self.origMatrix=matrix
        self.data=data=None
        if matrix:
            self.data=data=getattr(matrix, "items")
            matrix.matrixType = orange.SymMatrix.Symmetric 
            
        self.graph.ColorAttr=0
        self.graph.SizeAttr=0
        self.graph.ShapeAttr=0
        self.graph.NameAttr=0
        self.graph.closestPairs = None
        if isinstance(data, orange.ExampleTable):
            self.setExampleTable(data)
        elif isinstance(data, list):
            self.setList(data)
        elif isinstance(data, orange.VarList):
            self.setVarList(data)
        if matrix:
            self.mds=orngMDS.MDS(matrix)
            self.mds.points=numpy.random.random(size=[self.mds.n, self.mds.dim])
            self.mds.getStress()
            self.stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
            if data and type(data) == orange.ExampleTable:
                self.openContext("",self.data) 
            self.graph.setData(self.mds, self.colors, self.sizes, self.shapes, self.names, self.selectedInput)
        else:
            self.graph.clear()

    def cselected(self, selected=[]):
        self.selectedInputExamples=selected or []
        if self.data and type(self.data)==orange.ExampleTable:
            self.setExampleTable(self.data)
            self.graph.setData(self.mds, self.colors, self.sizes, self.shapes, self.names, self.selectedInput)

    def setExampleTable(self, data):
        self.colorCombo.clear()
        self.sizeCombo.clear()
        self.shapeCombo.clear()
        self.nameCombo.clear()
        attributes=[attr for attr in data.domain.variables+data.domain.getmetas().values() or [] ]
        discAttributes=filter(lambda a: a.varType==orange.VarTypes.Discrete, attributes)
        contAttributes=filter(lambda a: a.varType==orange.VarTypes.Continuous, attributes)
        attrName=[attr.name for attr in attributes]
        for name in ["Same color"]+attrName:
            self.colorCombo.addItem(name)
        for name in ["Same size"]+map(lambda a:a.name, contAttributes):
            self.sizeCombo.addItem(name)
        for name in ["Same shape"]+map(lambda a: a.name, discAttributes):
            self.shapeCombo.addItem(name)
        for name in ["No name"]+attrName:
            self.nameCombo.addItem(name)

#        if data.domain.classVar:
#            if data.domain.classVar.varType == orange.VarTypes.Discrete:
#                self.graph.ColorAttr = len(data.domain.variables) # index 0 is Same color!
#            elif data.domain.classVar.varType == orange.VarTypes.Continuous:
#                self.graph.SizeAttr = len(data.domain.variables) # index 0 is Same color!
        try:
            self.graph.NameAttr = 1 + [name.lower() for name in attrName].index("name")
        except:
            pass
        
        self.attributes=attributes
        self.discAttributes=discAttributes
        self.contAttributes=contAttributes

        self.colors=[[Qt.black]*(len(attributes)+1) for i in range(len(data))]
        self.shapes=[[OWPoint.Ellipse]*(len(discAttributes)+1) for i in range(len(data))]
        self.sizes=[[1.0]*(len(contAttributes)+1) for i in range(len(data))]
        self.names=[[""]*(len(attributes)+1) for i in range(len(data))]
        try:
            selectedInput=self.selectedInputExamples.select(data.domain)
        except Exception:
            selectedInput=[]
        self.selectedInput=map(lambda d: selectedInput and (d in selectedInput), data)
        contI=discI=attrI=1
        def check(ex, a):
            try:
                ex[a]
            except:
                return False
            return not ex[a].isSpecial()
        
        for j, attr in enumerate(attributes):
            if attr.varType==orange.VarTypes.Discrete:
                c=OWColorPalette.ColorPaletteHSV(len(attr.values))
                for i in range(len(data)):
                    self.colors[i][attrI]= check(data[i],attr)  and c[int(data[i][attr])] or Qt.black
##                    self.shapes[i][discI]= data[i][attr].isSpecial() and self.graph.shapeList[0] or self.graph.shapeList[int(data[i][attr])%len(self.graph.shapeList)]
                    self.shapes[i][discI]= check(data[i],attr) and self.graph.shapeList[int(data[i][attr])%len(self.graph.shapeList)] or self.graph.shapeList[0]
                    self.names[i][attrI]= check(data[i],attr) and " "+str(data[i][attr]) or ""
                    #self.sizes[i][contI]=5
                attrI+=1
                discI+=1
            elif attr.varType==orange.VarTypes.Continuous:
                c=OWColorPalette.ColorPaletteBW(-1)
                #val=[e[attr] for e in data if not e[attr].isSpecial()]
                val=[e[attr] for e in data if check(e, attr)]
                minVal=min(val or [0])
                maxVal=max(val or [1])
                span = max(maxVal - minVal, 1e-6)
                for i in range(len(data)):
                    self.colors[i][attrI]=check(data[i],attr) and c.getColor((data[i][attr] - minVal)/span) or Qt.black 
                    #self.shapes[i][discI]=self.graph.shapeList[0]
                    self.names[i][attrI]=check(data[i],attr) and " "+str(data[i][attr]) or ""
                    self.sizes[i][contI]=check(data[i],attr) and (float(self.data[i][attr]) - minVal) / span or 1.0
                contI+=1
                attrI+=1
            else:
                for i in range(len(data)):
                    self.colors[i][attrI]=Qt.black
                    #self.shapes[i][j+1]=self.graph.shapeList[0]
                    self.names[i][attrI]= check(data[i],attr) and " "+str(data[i][attr]) or ""
                    #self.sizes[i][j+1]=5
                attrI+=1
        if data and data.domain.classVar:
            if data.domain.classVar.varType == orange.VarTypes.Discrete:
                self.graph.ColorAttr = len(self.colors[0]) - 1 # index 0 is Same color!
            elif data.domain.classVar.varType == orange.VarTypes.Continuous:
                self.graph.SizeAttr = len(self.sizes[0]) - 1 # index 0 is Same color!

    def setList(self, data):
        self.colorCombo.clear()
        self.sizeCombo.clear()
        self.shapeCombo.clear()
        self.nameCombo.clear()
        for name in ["Same color", "strain"]:
            self.colorCombo.addItem(name)
        for name in ["No name", "name", "strain"]:
            self.nameCombo.addItem(name)

        self.colors=[[Qt.black]*3 for i in range(len(data))]
        self.shapes=[[OWPoint.Ellipse] for i in range(len(data))]
        self.sizes=[[1.0] for i in range(len(data))]
        self.selectedInput=[False]*len(data)

        if type(data[0]) in [str, unicode]:
            self.names = [("", di, "", "") for di in data]
        else:
            self.names=[[""]*4 for i in range(len(data))]
            try:
                strains=list(set([d.strain for d in data]))
                c=OWColorPalette.ColorPaletteHSV(len(strains))
                for i, d in enumerate(data):
                    self.colors[i][1]=c[strains.index(d.strain)]
                    self.names[i][1]=" "+d.name
                    self.names[i][2]=" "+d.strain
            except Exception, val:
                print val

    def setVarList(self, data):
        self.colorCombo.clear()
        self.sizeCombo.clear()
        self.shapeCombo.clear()
        self.nameCombo.clear()
        for name in ["Same color", "Variable"]:
            self.colorCombo.addItem(name)
        for name in ["No name", "Var name"]:
            self.nameCombo.addItem(name)
        self.colors=[[Qt.black]*3 for i in range(len(data))]
        self.shapes=[[OWPoint.Ellipse] for i in range(len(data))]
        self.sizes=[[1.0] for i in range(len(data))]
        self.names=[[""]*4 for i in range(len(data))]
        self.selectedInput=[False]*len(data)
        try:
            c=OWColorPalette.ColorPaletteHSV(len(data))
            for i, d in enumerate(data):
                self.colors[i][1]=c[i]
                self.names[i][1]=" " +str(d.name)
        except Exception, val:
            print val

    def updateStressBySize(self, noRepaint = False):
        self.sizeCombo.setDisabled(self.graph.stressBySize)
        if not noRepaint:
            self.graph.updateData()
        
    def smacofStep(self):
        if not getattr(self, "mds", None):
            return
        for i in range(self.NumIter):
            self.mds.SMACOFstep()
        if self.computeStress:
            self.mds.getStress(self.stressFunc[self.StressFunc][1])
            self.stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
        #st=time.clock()
        if self.ReDraw:
            self.graph.updateData()
        #print "Update:", time.clock()-st

## I (Janez) disabled LSMT because it is implemented as it never should be:
#  orngMDS.LSMT transforms the distance matrix itself (indeed there is
#  the original stored, too), and from that point on there is no way the
#  user can "untransform" it, except for resending the signal
#  Since the basic problem is in bad design of orngMDS, I removed the option
#  from the widget. If somebody has time to fix orngMDS first, he's welcome. 
    def LSMT(self):
        if not getattr(self, "mds", None):
            return
        self.mds.LSMT()
        if self.computeStress:
            self.mds.getStress(self.stressFunc[self.StressFunc][1])
            self.stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
        if self.ReDraw:
            self.graph.updateData()

    def torgerson(self):
        if not getattr(self, "mds", None):
            return
        self.mds.Torgerson()
        if self.computeStress:
            self.mds.getStress(self.stressFunc[self.StressFunc][1])
            self.stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
        self.graph.updateData()

    def randomize(self):
        if not getattr(self, "mds", None):
            return
        self.mds.points = numpy.random.random(size=[self.mds.n,2])
        if self.computeStress:
            self.mds.getStress(self.stressFunc[self.StressFunc][1])
            self.stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
        self.graph.updateData()

    def jitter(self):
        if not getattr(self, "mds", None):
            return
        mi = numpy.min(self.mds.points, axis=0)
        ma = numpy.max(self.mds.points, axis=0)
        st = 0.05 * (ma - mi)
        for i in range(self.mds.n):
            for j in range(2):
                self.mds.points[i][j] += st[j]*(random() - 0.5)
        if self.computeStress:
            self.mds.getStress(self.stressFunc[self.StressFunc][1])
            self.stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
        self.graph.updateData()

    def start(self):
        if not getattr(self, "mds", None):
            return
        if self.done==False:
            self.done=True
            return
        self.done=False
        self.startButton.setText("Stop")
        numIter=0
        self.progressBarInit()
        pcur=0
        startStress=oldStress=stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
        startTime=time.clock()
        hist=[stress]*3
        while not self.done and numIter<self.maxIterations:
            for i in range(self.NumIter):
                self.mds.SMACOFstep()
                qApp.processEvents()
            if self.computeStress:
                self.mds.getStress(self.stressFunc[self.StressFunc][1])
                self.stress=stress=self.getAvgStress(self.stressFunc[self.StressFunc][1])
                hist.pop(0)
                hist.append(abs(oldStress-stress))
            numIter+=1
            self.infoB.setText("Num. steps: %i" % numIter)
            qApp.processEvents()
            if self.ReDraw:
                self.graph.updateData()
            qApp.processEvents()
            if self.computeStress and abs(sum(hist)/3)<abs(self.minStressDelta*oldStress):
                break
            ## Update progress bar
            p1=abs(self.minStressDelta*oldStress)/max(sum(hist)/3, 1e-6)*100
            if p1>100: p1=0
            pcur=min(max([p1, float(numIter)/self.maxIterations*100, pcur]),99)
            self.progressBarSet(int(pcur))

            oldStress=stress
        self.startButton.setText("Optimize")
        self.progressBarFinished()
        #if not self.ReDraw:
        self.graph.updateData()
        self.done=True
        #print "time %i " % (time.clock()-startTime)

    def testStart(self):
        if not getattr(self, "mds", None):
            return
        if self.done==False:
            self.done=True
            return
        self.done=False
        self.startButton.setText("Stop Optimization")
        self.stopping.setDisabled(1)
        self.progressBarInit()
        self.iterNum=0
        self.mds.progress_callback=self.callback
        self.mds.mds.optimize(self.maxIterations, self.stressFunc[self.StressFunc][1], self.minStressDelta)
        if self.iterNum%(math.pow(10,self.RefreshMode)):
            self.graph.updateData()
        self.startButton.setText("Optimize")
        self.stopping.setDisabled(0)
        self.progressBarFinished()
        self.done=True

    def callback(self, a,b=None):
        if not self.iterNum%(math.pow(10,self.RefreshMode)):
            self.graph.updateData()
        self.iterNum+=1
        self.infoB.setText("Num. steps: %i" % self.iterNum)
        self.infoA.setText("Avg. Stress: %f" % self.mds.avgStress)
        self.progressBarSet(int(a*100))
        qApp.processEvents()
        if self.done:
            return 0
        else:
            return 1


    def getAvgStress(self, stressf=orngMDS.SgnRelStress):
        return self.mds.avgStress
        """
        self.mds.getDistance()
        total=0.0
        total=sum([abs(a[0]) for a in self.mds.arr])
        self.infoA.setText("Avg. stress: %.7f" % (total/(self.mds.n*self.mds.n)))
        return total/(self.mds.n*self.mds.n)
        """

    def sendIf(self, i=-1):
        if self.autoSendSelection:
            self.sendSelections()
        
    def sendSelections(self):
        if not getattr(self, "mds", None):
            return
        points = self.graph.main_curve.points()
        selectedInd = [i for i, p in enumerate(points) if p.is_selected()]
        if type(self.data)==orange.ExampleTable:
            self.sendExampleTable(selectedInd)
        elif type(self.data)==list:
            self.sendList(selectedInd)

    def sendExampleTable(self, selectedInd):
        if self.selectionOptions==0:
            self.send("Data", orange.ExampleTable(self.data.getitems(selectedInd)))
        else:
            xAttr=orange.FloatVariable("X")
            yAttr=orange.FloatVariable("Y")
            if self.selectionOptions==1:
                domain=orange.Domain([xAttr, yAttr]+[v for v in self.data.domain.variables])
                domain.addmetas(self.data.domain.getmetas())
            else:
                domain=orange.Domain(self.data.domain)
                domain.addmeta(orange.newmetaid(), xAttr)
                domain.addmeta(orange.newmetaid(), yAttr)
            selection=orange.ExampleTable(domain)
            selection.extend(self.data.getitems(selectedInd))
            for i in range(len(selectedInd)):
                selection[i][xAttr]=self.mds.points[selectedInd[i]][0]
                selection[i][yAttr]=self.mds.points[selectedInd[i]][1]
            self.send("Data", selection)

    def sendList(self, selectedInd):
        if self.data and type(self.data[0]) == str:
            xAttr=orange.FloatVariable("X")
            yAttr=orange.FloatVariable("Y")
            nameAttr=  orange.StringVariable("name")
            if self.selectionOptions == 1:
                domain = orange.Domain([xAttr, yAttr, nameAttr])
                selection = orange.ExampleTable(domain)
                for i in range(len(selectedInd)):
                    selection.append(list(self.mds.points[selectedInd[i]]) + [self.data[i]])
            else:
                domain = orange.Domain([nameAttr])
                if self.selectionOptions:
                    domain.addmeta(orange.newmetaid(), xAttr)
                    domain.addmeta(orange.newmetaid(), yAttr)
                selection = orange.ExampleTable(domain)
                for i in range(len(selectedInd)):
                    selection.append([self.data[i]])
                    if self.selectionOptions:
                        selection[i][xAttr]=self.mds.points[selectedInd[i]][0]
                        selection[i][yAttr]=self.mds.points[selectedInd[i]][1]
            self.send("Data", selection)
            return
               
        if not selectedInd:
            self.send("Structured Data Files", None)
        else:
            datasets=[self.data[i] for i in selectedInd]
            names=list(set([d.dirname for d in datasets]))
            data=[(name, [d for d in filter(lambda a:a.strain==name, datasets)]) for name in names]
            self.send("Structured Data Files",data)

    def updateStress(self):
        if not getattr(self, "mds", None):
            return
        self.mds.getStress(self.stressFunc[self.StressFunc][1])
        self.graph.replot()

    def sendReport(self):
        self.reportSettings("Optimization",
                            [("Stress function", self.stressFunc[self.StressFunc][0]),
                             ("Minimal stress change", self.minStressDelta),
                             ("Maximal number of steps", self.maxIterations)])
        if self.graph.ColorAttr or self.graph.stressBySize or self.graph.SizeAttr or self.graph.ShapeAttr or self.graph.NameAttr or self.graph.ShowStress:
            self.reportSettings("Visual settings",
                                [self.graph.ColorAttr and ("Point color", self.colorCombo.currentText()),
                                 self.graph.stressBySize  and ("Point size", "&lt;stress&gt;")
                                    or self.graph.SizeAttr and ("Point size", self.sizeCombo.currentText()),
                                 self.graph.ShapeAttr and ("Point shape", self.shapeCombo.currentText()),
                                 self.graph.NameAttr and ("Labels", self.nameCombo.currentText()),
                                 self.graph.ShowStress and ("Proportion of connected pairs", self.graph.proportionGraphed)])
        self.reportSection("Chart")
        self.reportImage(self.graph.saveToFileDirect)
                             

class MDSPlot(OWPlot):
    def __init__(self, parent=None, name=None):
        OWPlot.__init__(self, parent, name)
        self.use_animations = False
        self.animate_points = False
        self.antialias_points = True
        self.data = None
        self.mds = None
        self.PointSize = 5
        self.ColorAttr = 0
        self.SizeAttr = 0
        self.ShapeAttr = 0
        self.NameAttr = 0
        self.ShowStress = False
        self.differentWidths = True
        self.stressByTransparency = True
        self.stressBySize = False
        self.NumStressLines = 10
        self.proportionGraphed = 20
        self.ShowName = True
        #self.curveKeys=[]
        self.pointKeys = []
        self.points = []
        self.lines = []
        self.lineKeys = []
        self.distanceLineCurves = []
        self.colors = []
        self.sizes = []
        self.closestPairs = None
        self.shapeList = [OWPoint.Ellipse,
                          OWPoint.Rect,
                          OWPoint.Diamond,
                          OWPoint.Triangle,
                          OWPoint.DTriangle ,
                          OWPoint.UTriangle,
                          OWPoint.LTriangle,
                          OWPoint.RTriangle,
                          OWPoint.Cross,
                          OWPoint.XCross ]

    def setData(self, mds, colors, sizes, shapes, names, showFilled):
        self.mds = mds
        self.colors = colors
        self.sizes = sizes
        self.shapes = shapes
        self.names = names
        self.showFilled = showFilled
        self.updateData()

    def updateData(self):
        self.clear()
        self.distanceLineCurves = []
        if self.ShowStress:
            self.updateDistanceLines()
        self.setPoints()
        self.replot()

    def updateDistanceLines(self):
        if not self.mds:
            return
        N = len(self.mds.points)
        np = min(int(N*(N-1)/2. * self.proportionGraphed/100.), 1000) # draw maximum of 1000 closest pairs
        needlines = int(math.ceil((1 + math.sqrt(1+8*np)) / 2)) 

        if self.closestPairs is None or len(self.closestPairs) < np:
            import heapq
            m = self.mds.originalDistances
            self.closestPairs = sorted(heapq.nsmallest(np, ((m[i, j], i, j) for i in range(m.dim) for j in range(i))))
                
        for c in self.distanceLineCurves:
            try:
                c.detach()
            except RuntimeError, ex: #underlying C/C++ object has been deleted
                pass
        self.distanceLineCurves = []
                
        hdist = self.closestPairs[:np]
        if not hdist:
            return
    
        black = QColor(192,192,192)
        if self.differentWidths:
            mindist = hdist[0][0]
            maxdist = hdist[-1][0]
        else:
            mindist = maxdist = 0
        if maxdist != mindist:
            k = 3 / (maxdist - mindist)**2
            for dist, i, j in hdist:
                pti, ptj = self.mds.points[i], self.mds.points[j]
                c = self.add_curve("n_lines", black, black, 2, style=OWCurve.Lines, xData=[pti[0],ptj[0]], yData=[pti[1],ptj[1]], lineWidth = max(1, (maxdist - dist)**2 * k))
                c.set_in_background(True)
                self.distanceLineCurves.append(c)
        else:
            for dist, i, j in hdist:
                pti, ptj = self.mds.points[i], self.mds.points[j]
                c = self.add_curve("n_lines", black, black, 2, OWCurve.Lines, xData=[pti[0],ptj[0]], yData=[pti[1],ptj[1]], lineWidth = 2)
                c.set_in_background(True)
                self.distanceLineCurves.append(c)
        
                    
    def updateLinesRepaint(self):
        if self.mds:
            if self.ShowStress:
                self.updateDistanceLines()
            else:
                for c in self.distanceLineCurves:
                    try:
                        c.detach()
                    except RuntimeError, ex: #underlying C/C++ object has been deleted
                        pass 
                self.distanceLineCurves = []
            self.replot()

    def setPoints(self):
        if not self.mds:
            return 
        x_data = [p[0] for p in self.mds.points]
        y_data = [p[1] for p in self.mds.points]
        
        if self.stressBySize or self.stressByTransparency:
            stresses = map(sum, self.mds.stress)
            
            mins, maxs = min(stresses), max(stresses)
            stress_scale = 1. / max(1e-7, maxs - mins)
#            stress_scale = 1. / max(1e-7, maxs - mins)
            
        if self.ColorAttr != 0:
            colors = [c[self.ColorAttr] for c in self.colors]
        else:
            colors = [QColor(Qt.black) for _ in self.colors] #QColor(Qt.black)
            
        if self.stressByTransparency:
            for c, s in zip(colors, stresses):
                c.setAlpha(math.floor((1.0 - ((s - mins) * stress_scale)) * 255))
            
        if self.stressBySize:
            sizes = [(s - mins) * stress_scale * self.PointSize for s in stresses]
        elif self.SizeAttr != 0:
            sizes = [s[self.SizeAttr] * self.PointSize for s in self.sizes]
        else:
            sizes = [self.PointSize]
            
        if self.ShapeAttr != 0:
            shapes = [s[self.ShapeAttr] for s in self.shapes]
        else:
            shapes = [self.shapeList[0]]
        
        if self.NameAttr != 0:
            labels = [n[self.NameAttr] for n in self.names]
        else:
            labels = []
            
        self.set_main_curve_data(x_data, y_data, colors, labels, sizes, shapes, self.showFilled)
        
    def sendData(self, *args):
        pass
    

if __name__=="__main__":
    app=QApplication(sys.argv)
    w=OWMDSQt()
    w.show()
    data=orange.ExampleTable("../../doc/datasets/iris.tab")
##    data = orange.ExampleTable(r"E:\Development\Orange Datasets\UCI\iris.tab")
##    data=orange.ExampleTable("/home/ales/src/MDSjakulin/eu_nations.txt")
    matrix = orange.SymMatrix(len(data))
    dist = orange.ExamplesDistanceConstructor_Euclidean(data)
    matrix = orange.SymMatrix(len(data))
    matrix.setattr('items', data)
    for i in range(len(data)):
        for j in range(i+1):
            matrix[i, j] = dist(data[i], data[j])

    w.cmatrix(matrix)
    w.cselected(orange.ExampleTable(data[:50]))
    app.exec_()
    w.saveSettings()

