"""
<name>Polyviz (Qt)</name>
<description>Polyviz (multiattribute) visualization.</description>
<contact>Gregor Leban (gregor.leban@fri.uni-lj.si)</contact>
<icon>icons/Polyviz.png</icon>
<priority>160</priority>
"""
# Polyviz.py
#
# Show data using Polyviz visualization method
#
from OWLinProjQt import *
from OWPolyvizGraphQt import *


###########################################################################################
##### WIDGET : Polyviz visualization
###########################################################################################
class OWPolyvizQt(OWLinProjQt):
    settingsList = ["graph.pointWidth", "graph.jitterSize", "graph.scaleFactor", "graph.useAntialiasing",
                    "graph.showLegend", "graph.showFilledSymbols", "graph.optimizedDrawing", "graph.useDifferentSymbols", "autoSendSelection",
                    "graph.useDifferentColors", "graph.tooltipKind", "graph.tooltipValue", "toolbarSelection", "VizRankLearnerName",
                    "colorSettings", "selectedSchemaIndex", "addProjectedPositions", "showAllAttributes", "graph.lineLength"]

    def __init__(self,parent=None, signalManager = None):
        OWLinProjQt.__init__(self, parent, signalManager, "Polyviz (qt)", graphClass = OWPolyvizGraphQt)

        self.inputs = [("Data", ExampleTable, self.setData, Default), ("Data Subset", ExampleTable, self.setSubsetData), ("Features", AttributeList, self.setShownAttributes), ("Evaluation Results", orngTest.ExperimentResults, self.setTestResults), ("VizRank Learner", orange.Learner, self.setVizRankLearner)]
        self.outputs = [("Selected Data", ExampleTable), ("Other Data", ExampleTable), ("Features", AttributeList)]

        # SETTINGS TAB
        self.extraTopBox.show()
        OWGUI.hSlider(self.extraTopBox, self, 'graph.lineLength', box='Line length: ', minValue=0, maxValue=10, step=1, callback = self.updateGraph)




#test widget appearance
if __name__=="__main__":
    a=QApplication(sys.argv)
    ow=OWPolyvizQt()
    ow.show()
    a.exec_()

    #save settings
    ow.saveSettings()
