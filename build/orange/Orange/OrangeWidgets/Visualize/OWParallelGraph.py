#
# OWParallelGraph.py
#
import orngEnviron
from OWGraph import *
#from OWDistributions import *
from orngScaleData import *
from statc import pearsonr

NO_STATISTICS = 0
MEANS  = 1
MEDIAN = 2

class OWParallelGraph(OWGraph, orngScaleData):
    def __init__(self, parallelDlg, parent = None, name = None):
        OWGraph.__init__(self, parent, name)
        orngScaleData.__init__(self)

        self.parallelDlg = parallelDlg
        self.showDistributions = 0
        self.toolRects = []
        self.useSplines = 0
        self.showStatistics = 0
        self.lastSelectedCurve = None
        self.enabledLegend = 0
        self.enableGridXB(0)
        self.enableGridYL(0)
        self.domainContingency = None
        self.alphaValue2 = 150
        self.autoUpdateAxes = 1
        self.oldLegendKeys = []
        self.selectionConditions = {}
        self.visualizedAttributes = []
        self.visualizedMidLabels = []
        self.selectedExamples = []
        self.unselectedExamples = []
        self.bottomPixmap = QPixmap(os.path.join(orngEnviron.directoryNames["widgetDir"], "icons/upgreenarrow.png"))
        self.topPixmap = QPixmap(os.path.join(orngEnviron.directoryNames["widgetDir"], "icons/downgreenarrow.png"))

        self.axisScaleDraw(QwtPlot.xBottom).enableComponent(QwtScaleDraw.Backbone, 0)
        self.axisScaleDraw(QwtPlot.xBottom).enableComponent(QwtScaleDraw.Ticks, 0)
        self.axisScaleDraw(QwtPlot.yLeft).enableComponent(QwtScaleDraw.Backbone, 0)
        self.axisScaleDraw(QwtPlot.yLeft).enableComponent(QwtScaleDraw.Ticks, 0)

    def setData(self, data, subsetData = None, **args):
        OWGraph.setData(self, data)
        orngScaleData.setData(self, data, subsetData, **args)
        self.domainContingency = None
        


    # update shown data. Set attributes, coloring by className ....
    def updateData(self, attributes, midLabels = None, updateAxisScale = 1):
        self.removeDrawingCurves(removeLegendItems = 0, removeMarkers = 1)  # don't delete legend items
        if attributes != self.visualizedAttributes:
            self.selectionConditions = {}       # reset selections

        self.visualizedAttributes = []
        self.visualizedMidLabels = []
        self.selectedExamples = []
        self.unselectedExamples = []

        if not (self.haveData or self.haveSubsetData):  return
        if len(attributes) < 2: return

        self.visualizedAttributes = attributes
        self.visualizedMidLabels = midLabels
        for name in self.selectionConditions.keys():        # keep only conditions that are related to the currently visualized attributes
            if name not in self.visualizedAttributes:
                self.selectionConditions.pop(name)

        # set the limits for panning
        self.xPanningInfo = (1, 0, len(attributes)-1)
        self.yPanningInfo = (0, 0, 0)   # we don't enable panning in y direction so it doesn't matter what values we put in for the limits

        if updateAxisScale:
            if self.showAttrValues: self.setAxisScale(QwtPlot.yLeft, -0.04, 1.04, 1)
            else:                   self.setAxisScale(QwtPlot.yLeft, -0.02, 1.02, 1)

            if self.autoUpdateAxes:
                if attributes and isinstance(self.dataDomain[attributes[-1]], orange.EnumVariable):
                    self.setAxisScale(QwtPlot.xBottom, -0.1, len(attributes) - 0.4, 1)
                else:
                    self.setAxisScale(QwtPlot.xBottom, -0.1, len(attributes) - 0.9, 1)
            else:
                m = self.axisScaleDiv(QwtPlot.xBottom).interval().minValue()
                M = self.axisScaleDiv(QwtPlot.xBottom).interval().maxValue()
                if m < 0 or M > len(attributes) - 2:
                    self.setAxisScale(QwtPlot.xBottom, 0, len(attributes)-1, 1)

        self.setAxisScaleDraw(QwtPlot.xBottom, DiscreteAxisScaleDraw([self.getAttributeLabel(attr) for attr in attributes]))
        #self.setAxisScaleDraw(QwtPlot.yLeft, HiddenScaleDraw())
        self.setAxisMaxMajor(QwtPlot.xBottom, len(attributes))
        self.setAxisMaxMinor(QwtPlot.xBottom, 0)

        length = len(attributes)
        indices = [self.attributeNameIndex[label] for label in attributes]

        xs = range(length)
        dataSize = len(self.scaledData[0])

        if self.dataHasDiscreteClass:
            self.discPalette.setNumberOfColors(len(self.dataDomain.classVar.values))


        # ############################################
        # draw the data
        # ############################################
        subsetIdsToDraw = self.haveSubsetData and dict([(self.rawSubsetData[i].id, 1) for i in self.getValidSubsetIndices(indices)]) or {}
        validData = self.getValidList(indices)
        mainCurves = {}
        subCurves = {}
        conditions = dict([(name, attributes.index(name)) for name in self.selectionConditions.keys()])

        for i in range(dataSize):
            if not validData[i]:
                continue

            if not self.dataHasClass:
                newColor = (0,0,0)
            elif self.dataHasContinuousClass:
                newColor = self.contPalette.getRGB(self.noJitteringScaledData[self.dataClassIndex][i])
            else:
                newColor = self.discPalette.getRGB(self.originalData[self.dataClassIndex][i])

            data = [self.scaledData[index][i] for index in indices]

            # if we have selected some conditions and the example does not match it we show it as a subset data
            if 0 in [data[index] >= self.selectionConditions[name][0] and data[index] <= self.selectionConditions[name][1] for (name, index) in conditions.items()]:
                alpha = self.alphaValue2
                curves = subCurves
                self.unselectedExamples.append(i)
            # if we have subset data then use alpha2 for main data and alpha for subset data
            elif self.haveSubsetData and not subsetIdsToDraw.has_key(self.rawData[i].id):
                alpha = self.alphaValue2
                curves = subCurves
                self.unselectedExamples.append(i)
            else:
                alpha = self.alphaValue
                curves = mainCurves
                self.selectedExamples.append(i)
                if subsetIdsToDraw.has_key(self.rawData[i].id):
                    subsetIdsToDraw.pop(self.rawData[i].id)

            newColor += (alpha,)

            if not curves.has_key(newColor):
                curves[newColor] = []
            curves[newColor].extend(data)

        # if we have a data subset that contains examples that don't exist in the original dataset we show them here
        if subsetIdsToDraw != {}:
            validSubsetData = self.getValidSubsetList(indices)

            for i in range(len(self.rawSubsetData)):
                if not validSubsetData[i]: continue
                if not subsetIdsToDraw.has_key(self.rawSubsetData[i].id): continue

                data = [self.scaledSubsetData[index][i] for index in indices]
                if not self.dataDomain.classVar or self.rawSubsetData[i].getclass().isSpecial():
                    newColor = (0,0,0)
                elif self.dataHasContinuousClass:
                    newColor = self.contPalette.getRGB(self.noJitteringScaledSubsetData[self.dataClassIndex][i])
                else:
                    newColor = self.discPalette.getRGB(self.originalSubsetData[self.dataClassIndex][i])

                if 0 in [data[index] >= self.selectionConditions[name][0] and data[index] <= self.selectionConditions[name][1] for (name, index) in conditions.items()]:
                    newColor += (self.alphaValue2,)
                    curves = subCurves
                else:
                    newColor += (self.alphaValue,)
                    curves = mainCurves

                if not curves.has_key(newColor):
                    curves[newColor] = []
                curves[newColor].extend(data)

        # add main curves
        keys = mainCurves.keys()
        keys.sort()     # otherwise the order of curves change when we slide the alpha slider
        for key in keys:
            curve = ParallelCoordinatesCurve(len(attributes), mainCurves[key], key)
            if self.useAntialiasing:  
                curve.setRenderHint(QwtPlotItem.RenderAntialiased)
            if self.useSplines:
                curve.setCurveAttribute(QwtPlotCurve.Fitted)
#                curve.setCurveFitter(QwtSplineCurveFitter())
            curve.attach(self)

        # add sub curves
        keys = subCurves.keys()
        keys.sort()     # otherwise the order of curves change when we slide the alpha slider
        for key in keys:
            curve = ParallelCoordinatesCurve(len(attributes), subCurves[key], key)
            if self.useAntialiasing: 
                curve.setRenderHint(QwtPlotItem.RenderAntialiased)
            if self.useSplines:      
                curve.setCurveAttribute(QwtPlotCurve.Fitted)
            curve.attach(self)



        # ############################################
        # do we want to show distributions with discrete attributes
        if self.showDistributions and self.dataHasDiscreteClass and self.haveData:
            self.showDistributionValues(validData, indices)

        # ############################################
        # draw vertical lines that represent attributes
        for i in range(len(attributes)):
            self.addCurve("", lineWidth = 2, style = QwtPlotCurve.Lines, symbol = QwtSymbol.NoSymbol, xData = [i,i], yData = [0,1])
            if self.showAttrValues == 1:
                attr = self.dataDomain[attributes[i]]
                if attr.varType == orange.VarTypes.Continuous:
                    strVal1 = "%%.%df" % (attr.numberOfDecimals) % (self.attrValues[attr.name][0])
                    strVal2 = "%%.%df" % (attr.numberOfDecimals) % (self.attrValues[attr.name][1])
                    align1 = i == 0 and Qt.AlignRight | Qt.AlignBottom or i == len(attributes)-1 and Qt.AlignLeft | Qt.AlignBottom or Qt.AlignHCenter | Qt.AlignBottom
                    align2 = i == 0 and Qt.AlignRight | Qt.AlignTop or i == len(attributes)-1 and Qt.AlignLeft | Qt.AlignTop or Qt.AlignHCenter | Qt.AlignTop
                    self.addMarker(strVal1, i, 0.0-0.01, alignment = align1)
                    self.addMarker(strVal2, i, 1.0+0.01, alignment = align2)

                elif attr.varType == orange.VarTypes.Discrete:
                    attrVals = getVariableValuesSorted(self.dataDomain[attributes[i]])
                    valsLen = len(attrVals)
                    for pos in range(len(attrVals)):
                        # show a rectangle behind the marker
                        self.addMarker(attrVals[pos], i+0.01, float(1+2*pos)/float(2*valsLen), alignment = Qt.AlignRight | Qt.AlignVCenter, bold = 1, brushColor = Qt.white)

        # ##############################################
        # show lines that represent standard deviation or quartiles
        # ##############################################
        if self.showStatistics and self.haveData:
            data = []
            for i in range(length):
                if self.dataDomain[indices[i]].varType != orange.VarTypes.Continuous:
                    data.append([()])
                    continue  # only for continuous attributes
                array = numpy.compress(numpy.equal(self.validDataArray[indices[i]], 1), self.scaledData[indices[i]])  # remove missing values

                if not self.dataHasClass or self.dataHasContinuousClass:    # no class
                    if self.showStatistics == MEANS:
                        m = array.mean()
                        dev = array.std()
                        data.append([(m-dev, m, m+dev)])
                    elif self.showStatistics == MEDIAN:
                        sorted = numpy.sort(array)
                        if len(sorted) > 0:
                            data.append([(sorted[int(len(sorted)/4.0)], sorted[int(len(sorted)/2.0)], sorted[int(len(sorted)*0.75)])])
                        else:
                            data.append([(0,0,0)])
                else:
                    curr = []
                    classValues = getVariableValuesSorted(self.dataDomain.classVar)
                    classValueIndices = getVariableValueIndices(self.dataDomain.classVar)
                    for c in range(len(classValues)):
                        scaledVal = ((classValueIndices[classValues[c]] * 2) + 1) / float(2*len(classValueIndices))
                        nonMissingValues = numpy.compress(numpy.equal(self.validDataArray[indices[i]], 1), self.noJitteringScaledData[self.dataClassIndex])  # remove missing values
                        arr_c = numpy.compress(numpy.equal(nonMissingValues, scaledVal), array)
                        if len(arr_c) == 0:
                            curr.append((0,0,0)); continue
                        if self.showStatistics == MEANS:
                            m = arr_c.mean()
                            dev = arr_c.std()
                            curr.append((m-dev, m, m+dev))
                        elif self.showStatistics == MEDIAN:
                            sorted = numpy.sort(arr_c)
                            curr.append((sorted[int(len(arr_c)/4.0)], sorted[int(len(arr_c)/2.0)], sorted[int(len(arr_c)*0.75)]))
                    data.append(curr)

            # draw vertical lines
            for i in range(len(data)):
                for c in range(len(data[i])):
                    if data[i][c] == (): continue
                    x = i - 0.03*(len(data[i])-1)/2.0 + c*0.03
                    col = QColor(self.discPalette[c])
                    col.setAlpha(self.alphaValue2)
                    self.addCurve("", col, col, 3, QwtPlotCurve.Lines, QwtSymbol.NoSymbol, xData = [x,x,x], yData = [data[i][c][0], data[i][c][1], data[i][c][2]], lineWidth = 4)
                    self.addCurve("", col, col, 1, QwtPlotCurve.Lines, QwtSymbol.NoSymbol, xData = [x-0.03, x+0.03], yData = [data[i][c][0], data[i][c][0]], lineWidth = 4)
                    self.addCurve("", col, col, 1, QwtPlotCurve.Lines, QwtSymbol.NoSymbol, xData = [x-0.03, x+0.03], yData = [data[i][c][1], data[i][c][1]], lineWidth = 4)
                    self.addCurve("", col, col, 1, QwtPlotCurve.Lines, QwtSymbol.NoSymbol, xData = [x-0.03, x+0.03], yData = [data[i][c][2], data[i][c][2]], lineWidth = 4)

            # draw lines with mean/median values
            classCount = 1
            if not self.dataHasClass or self.dataHasContinuousClass:
                classCount = 1 # no class
            else: classCount = len(self.dataDomain.classVar.values)
            for c in range(classCount):
                diff = - 0.03*(classCount-1)/2.0 + c*0.03
                ys = []
                xs = []
                for i in range(len(data)):
                    if data[i] != [()]: ys.append(data[i][c][1]); xs.append(i+diff)
                    else:
                        if len(xs) > 1:
                            col = QColor(self.discPalette[c])
                            col.setAlpha(self.alphaValue2)
                            self.addCurve("", col, col, 1, QwtPlotCurve.Lines, QwtSymbol.NoSymbol, xData = xs, yData = ys, lineWidth = 4)
                        xs = []; ys = []
                col = QColor(self.discPalette[c])
                col.setAlpha(self.alphaValue2)
                self.addCurve("", col, col, 1, QwtPlotCurve.Lines, QwtSymbol.NoSymbol, xData = xs, yData = ys, lineWidth = 4)


        # ##################################################
        # show labels in the middle of the axis
        if midLabels:
            for j in range(len(midLabels)):
                self.addMarker(midLabels[j], j+0.5, 1.0, alignment = Qt.AlignCenter | Qt.AlignTop)

        # show the legend
        if self.enabledLegend == 1 and self.dataHasDiscreteClass:
            if self.dataDomain.classVar.varType == orange.VarTypes.Discrete:
                legendKeys = []
                varValues = getVariableValuesSorted(self.dataDomain.classVar)
                #self.addCurve("<b>" + self.dataDomain.classVar.name + ":</b>", QColor(0,0,0), QColor(0,0,0), 0, symbol = QwtSymbol.NoSymbol, enableLegend = 1)
                for ind in range(len(varValues)):
                    #self.addCurve(varValues[ind], self.discPalette[ind], self.discPalette[ind], 15, symbol = QwtSymbol.Rect, enableLegend = 1)
                    legendKeys.append((varValues[ind], self.discPalette[ind]))
                if legendKeys != self.oldLegendKeys:
                    self.oldLegendKeys = legendKeys
                    self.legend().clear()
                    self.addCurve("<b>" + self.dataDomain.classVar.name + ":</b>", QColor(0,0,0), QColor(0,0,0), 0, symbol = QwtSymbol.NoSymbol, enableLegend = 1)
                    for (name, color) in legendKeys:
                        self.addCurve(name, color, color, 15, symbol = QwtSymbol.Rect, enableLegend = 1)
            else:
                l = len(attributes)-1
                xs = [l*1.15, l*1.20, l*1.20, l*1.15]
                count = 200; height = 1/200.
                for i in range(count):
                    y = i/float(count)
                    col = self.contPalette[y]
                    curve = PolygonCurve(QPen(col), QBrush(col), xData = xs, yData = [y,y, y+height, y+height])
                    curve.attach(self)

                # add markers for min and max value of color attribute
                [minVal, maxVal] = self.attrValues[self.dataDomain.classVar.name]
                decimals = self.dataDomain.classVar.numberOfDecimals
                self.addMarker("%%.%df" % (decimals) % (minVal), xs[0] - l*0.02, 0.04, Qt.AlignLeft)
                self.addMarker("%%.%df" % (decimals) % (maxVal), xs[0] - l*0.02, 1.0 - 0.04, Qt.AlignLeft)
        else:
            self.legend().clear()
            self.oldLegendKeys = []

        self.replot()


    # ##########################################
    # SHOW DISTRIBUTION BAR GRAPH
    def showDistributionValues(self, validData, indices):
        # create color table
        clsCount = len(self.dataDomain.classVar.values)
        #if clsCount < 1: clsCount = 1.0

        # we create a hash table of possible class values (happens only if we have a discrete class)
        classValueSorted  = getVariableValuesSorted(self.dataDomain.classVar)
        if self.domainContingency == None:
            self.domainContingency = orange.DomainContingency(self.rawData)

        maxVal = 1
        for attr in indices:
            if self.dataDomain[attr].varType != orange.VarTypes.Discrete:
                continue
            if self.dataDomain[attr] == self.dataDomain.classVar:
                maxVal = max(maxVal, max(orange.Distribution(attr, self.rawData) or [1]))
            else:
                maxVal = max(maxVal, max([max(val or [1]) for val in self.domainContingency[attr].values()] or [1]))
                

        for graphAttrIndex, index in enumerate(indices):
            attr = self.dataDomain[index]
            if attr.varType != orange.VarTypes.Discrete: continue
            if self.dataDomain[index] == self.dataDomain.classVar:
                contingency = orange.Contingency(self.dataDomain[index], self.dataDomain[index])
                dist = orange.Distribution(self.dataDomain[index], self.rawData)
                for val in self.dataDomain[index].values:
                    contingency[val][val] = dist[val]
            else:
                contingency = self.domainContingency[index]
                                
            attrLen = len(attr.values)

            # we create a hash table of variable values and their indices
            variableValueIndices = getVariableValueIndices(self.dataDomain[index])
            variableValueSorted = getVariableValuesSorted(self.dataDomain[index])

            # create bar curve
            for j in range(attrLen):
                attrVal = variableValueSorted[j]
                try:
                    attrValCont = contingency[attrVal]
                except IndexError, ex:
                    print >> sys.stderr, ex, attrVal, contingency
                    continue
                
                for i in range(clsCount):
                    clsVal = classValueSorted[i]

                    newColor = QColor(self.discPalette[i])
                    newColor.setAlpha(self.alphaValue)

                    width = float(attrValCont[clsVal]*0.5) / float(maxVal)
                    interval = 1.0/float(2*attrLen)
                    yOff = float(1.0 + 2.0*j)/float(2*attrLen)
                    height = 0.7/float(clsCount*attrLen)

                    yLowBott = yOff + float(clsCount*height)/2.0 - i*height
                    curve = PolygonCurve(QPen(newColor), QBrush(newColor), xData = [graphAttrIndex, graphAttrIndex + width, graphAttrIndex + width, graphAttrIndex], yData = [yLowBott, yLowBott, yLowBott - height, yLowBott - height], tooltip = (self.dataDomain[index].name, variableValueSorted[j], len(self.rawData), [(clsVal, attrValCont[clsVal]) for clsVal in classValueSorted]))
                    curve.attach(self)


    # handle tooltip events
    def event(self, ev):
        if ev.type() == QEvent.ToolTip:
            x = self.invTransform(QwtPlot.xBottom, ev.pos().x())
            y = self.invTransform(QwtPlot.yLeft, ev.pos().y())

            canvasPos = self.canvas().mapFrom(self, ev.pos())
            xFloat = self.invTransform(QwtPlot.xBottom, canvasPos.x())
            contact, (index, pos) = self.testArrowContact(int(round(xFloat)), canvasPos.x(), canvasPos.y())
            if contact:
                attr = self.dataDomain[self.visualizedAttributes[index]]
                if attr.varType == orange.VarTypes.Continuous:
                    condition = self.selectionConditions.get(attr.name, [0,1])
                    val = self.attrValues[attr.name][0] + condition[pos] * (self.attrValues[attr.name][1] - self.attrValues[attr.name][0])
                    strVal = attr.name + "= %%.%df" % (attr.numberOfDecimals) % (val)
                    QToolTip.showText(ev.globalPos(), strVal)
            else:
                for curve in self.itemList():
                    if type(curve) == PolygonCurve and curve.boundingRect().contains(x,y) and getattr(curve, "tooltip", None):
                        (name, value, total, dist) = curve.tooltip
                        count = sum([v[1] for v in dist])
                        if count == 0: continue
                        tooltipText = "Attribute: <b>%s</b><br>Value: <b>%s</b><br>Total instances: <b>%i</b> (%.1f%%)<br>Class distribution:<br>" % (name, value, count, 100.0*count/float(total))
                        for (val, n) in dist:
                            tooltipText += "&nbsp; &nbsp; <b>%s</b> : <b>%i</b> (%.1f%%)<br>" % (val, n, 100.0*float(n)/float(count))
                        QToolTip.showText(ev.globalPos(), tooltipText[:-4])

        elif ev.type() == QEvent.MouseMove:
            QToolTip.hideText()

        return OWGraph.event(self, ev)


    def testArrowContact(self, indices, x, y):
        if type(indices) != list: indices = [indices]
        for index in indices:
            if index >= len(self.visualizedAttributes) or index < 0: continue
            intX = self.transform(QwtPlot.xBottom, index)
            bottom = self.transform(QwtPlot.yLeft, self.selectionConditions.get(self.visualizedAttributes[index], [0,1])[0])
            bottomRect = QRect(intX-self.bottomPixmap.width()/2, bottom, self.bottomPixmap.width(), self.bottomPixmap.height())
            if bottomRect.contains(QPoint(x,y)): return 1, (index, 0)
            top = self.transform(QwtPlot.yLeft, self.selectionConditions.get(self.visualizedAttributes[index], [0,1])[1])
            topRect = QRect(intX-self.topPixmap.width()/2, top-self.topPixmap.height(), self.topPixmap.width(), self.topPixmap.height())
            if topRect.contains(QPoint(x,y)): return 1, (index, 1)
        return 0, (0, 0)

    def mousePressEvent(self, e):
        canvasPos = self.canvas().mapFrom(self, e.pos())
        xFloat = self.invTransform(QwtPlot.xBottom, canvasPos.x())
        contact, info = self.testArrowContact(int(round(xFloat)), canvasPos.x(), canvasPos.y())

        if contact:
            self.pressedArrow = info
        elif self.state in [ZOOMING, PANNING]:
            OWGraph.mousePressEvent(self, e)


    def mouseMoveEvent(self, e):
        if hasattr(self, "pressedArrow"):
            canvasPos = self.canvas().mapFrom(self, e.pos())
            yFloat = min(1, max(0, self.invTransform(QwtPlot.yLeft, canvasPos.y())))
            index, pos = self.pressedArrow
            attr = self.dataDomain[self.visualizedAttributes[index]]
            oldCondition = self.selectionConditions.get(attr.name, [0,1])
            oldCondition[pos] = yFloat
            self.selectionConditions[attr.name] = oldCondition
            self.updateData(self.visualizedAttributes, self.visualizedMidLabels, updateAxisScale = 0)

            if attr.varType == orange.VarTypes.Continuous:
                val = self.attrValues[attr.name][0] + oldCondition[pos] * (self.attrValues[attr.name][1] - self.attrValues[attr.name][0])
                strVal = attr.name + "= %%.%df" % (attr.numberOfDecimals) % (val)
                QToolTip.showText(e.globalPos(), strVal)
            if self.sendSelectionOnUpdate and self.autoSendSelectionCallback:
                self.autoSendSelectionCallback()

        elif self.state in [ZOOMING, PANNING]:
            OWGraph.mouseMoveEvent(self, e)

    def mouseReleaseEvent(self, e):
        if hasattr(self, "pressedArrow"):
            del self.pressedArrow
            if self.autoSendSelectionCallback and not (self.sendSelectionOnUpdate and self.autoSendSelectionCallback):
                self.autoSendSelectionCallback() # send the new selection
        elif self.state in [ZOOMING, PANNING]:
            OWGraph.mouseReleaseEvent(self, e)


    def staticMouseClick(self, e):
        if e.button() == Qt.LeftButton and self.state == ZOOMING:
            if self.tempSelectionCurve: self.tempSelectionCurve.detach()
            self.tempSelectionCurve = None
            canvasPos = self.canvas().mapFrom(self, e.pos())
            x = self.invTransform(QwtPlot.xBottom, canvasPos.x())
            y = self.invTransform(QwtPlot.yLeft, canvasPos.y())
            diffX = (self.axisScaleDiv(QwtPlot.xBottom).interval().maxValue() -  self.axisScaleDiv(QwtPlot.xBottom).interval().minValue()) / 2.

            xmin = x - (diffX/2.) * (x - self.axisScaleDiv(QwtPlot.xBottom).interval().minValue()) / diffX
            xmax = x + (diffX/2.) * (self.axisScaleDiv(QwtPlot.xBottom).interval().maxValue() - x) / diffX
            ymin = self.axisScaleDiv(QwtPlot.yLeft).interval().maxValue()
            ymax = self.axisScaleDiv(QwtPlot.yLeft).interval().minValue()

            self.zoomStack.append((self.axisScaleDiv(QwtPlot.xBottom).interval().minValue(), self.axisScaleDiv(QwtPlot.xBottom).interval().maxValue(), self.axisScaleDiv(QwtPlot.yLeft).interval().minValue(), self.axisScaleDiv(QwtPlot.yLeft).interval().maxValue()))
            self.setNewZoom(xmin, xmax, ymax, ymin)
            return 1

        # if the user clicked between two lines send a list with the names of the two attributes
        elif self.parallelDlg:
            x1 = int(self.invTransform(QwtPlot.xBottom, e.x()))
            axis = self.axisScaleDraw(QwtPlot.xBottom)
            self.parallelDlg.sendShownAttributes([str(axis.label(x1)), str(axis.label(x1+1))])
        return 0

    def removeAllSelections(self, send = 1):
        self.selectionConditions = {}
        self.updateData(self.visualizedAttributes, self.visualizedMidLabels, updateAxisScale = 0)
        if send and self.autoSendSelectionCallback:
            self.autoSendSelectionCallback() # do we want to send new selection

    # draw the curves and the selection conditions
    def drawCanvas(self, painter):
        OWGraph.drawCanvas(self, painter)
        for i in range(int(max(0, math.floor(self.axisScaleDiv(QwtPlot.xBottom).interval().minValue()))), int(min(len(self.visualizedAttributes), math.ceil(self.axisScaleDiv(QwtPlot.xBottom).interval().maxValue())+1))):
            bottom, top = self.selectionConditions.get(self.visualizedAttributes[i], (0, 1))
            painter.drawPixmap(self.transform(QwtPlot.xBottom, i)-self.bottomPixmap.width()/2, self.transform(QwtPlot.yLeft, bottom), self.bottomPixmap)
            painter.drawPixmap(self.transform(QwtPlot.xBottom, i)-self.topPixmap.width()/2, self.transform(QwtPlot.yLeft, top)-self.topPixmap.height(), self.topPixmap)

    # get selected examples
    # this function must be called after calling self.updateGraph
    def getSelectionsAsExampleTables(self):
        if not self.haveData:
            return (None, None)

        selected = self.rawData.getitemsref(self.selectedExamples)
        unselected = self.rawData.getitemsref(self.unselectedExamples)

        if len(selected) == 0: selected = None
        if len(unselected) == 0: unselected = None
        return (selected, unselected)



# ####################################################################
# a curve that is able to draw several series of lines
class ParallelCoordinatesCurve(QwtPlotCurve):
    def __init__(self, attrCount, yData, color, name = ""):
        QwtPlotCurve.__init__(self, name)
        self.setStyle(QwtPlotCurve.Lines)
        self.setItemAttribute(QwtPlotItem.Legend, 0)

        lineCount = len(yData) / attrCount
        self.attrCount = attrCount
        self.xData = range(attrCount) * lineCount
        self.yData = yData
        
#        self._cubic = self.cubicPath(None, None)
        
        self.setData(QPolygonF(map(lambda t:QPointF(*t), zip(self.xData, self.yData))))
        if type(color) == tuple:
            self.setPen(QPen(QColor(*color)))
        else:
            self.setPen(QPen(QColor(color)))


    def drawCurve(self, painter, style, xMap, yMap, iFrom, iTo):
        low = max(0, int(math.floor(xMap.s1())))
        high = min(self.attrCount-1, int(math.ceil(xMap.s2())))
        painter.setPen(self.pen())
        if not self.testCurveAttribute(QwtPlotCurve.Fitted):
            for i in range(self.dataSize() / self.attrCount):
                start = self.attrCount * i + low
                end = self.attrCount * i + high 
                self.drawLines(painter, xMap, yMap, start, end)
        else:
            painter.save()
#            painter.scale(xMap.transform(1.0), yMap.transform(1.0))
            painter.strokePath(self.cubicPath(xMap, yMap), self.pen())
#            painter.strokePath(self._cubic, self.pen())
            painter.restore()

    def cubicPath(self, xMap, yMap):
        path = QPainterPath()
        transform = lambda x, y: QPointF(xMap.transform(x), yMap.transform(y))
#        transform = lambda x, y: QPointF(x, y)
#        data = [QPointF(transform(x, y)) for x, y in zip(self.xData, self.yData)]
        data = [(x, y) for x, y in zip(self.xData, self.yData)]
        for i in range(self.dataSize() / self.attrCount):
            segment = data[i*self.attrCount: (i + 1)*self.attrCount]
            for i, p in enumerate(segment[:-1]):
                x1, y1 = p
                x2, y2 = segment[i + 1]
                path.moveTo(transform(x1, y1))
                path.cubicTo(transform(x1 + 0.5, y1), transform(x2 - 0.5, y2), transform(x2, y2))
        return path        
                
                
            

