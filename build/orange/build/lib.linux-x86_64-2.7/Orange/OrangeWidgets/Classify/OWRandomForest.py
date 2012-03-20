"""
<name>Random Forest</name>
<description>Random forest learner/classifier.</description>
<icon>icons/RandomForest.png</icon>
<contact>Marko Toplak (marko.toplak(@at@)gmail.com)</contact>
<priority>320</priority>
"""

from OWWidget import *
import orngTree, OWGUI
import orngEnsemble
from exceptions import Exception
from orngWrap import PreprocessedLearner

class OWRandomForest(OWWidget):
    settingsList = ["name", "trees", "attributes", "attributesP", "preNodeInst", "preNodeInstP", "limitDepth", "limitDepthP", "rseed"]

    def __init__(self, parent=None, signalManager = None, name='Random Forest'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea=False, resizingEnabled=False)

        self.inputs = [("Data", ExampleTable, self.setData),
                       ("Preprocess", PreprocessedLearner, self.setPreprocessor)]
        
        self.outputs = [("Learner", orange.Learner),
                        ("Random Forest Classifier", orange.Classifier)]

        self.name = 'Random Forest'
        self.trees = 10
        self.attributes = 0
        self.attributesP = 5
        self.preNodeInst = 1
        self.preNodeInstP = 5
        self.limitDepth = 0
        self.limitDepthP = 3
        self.rseed = 0

        self.maxTrees = 10000

        self.loadSettings()

        self.data = None
        self.preprocessor = None

        OWGUI.lineEdit(self.controlArea, self, 'name', box='Learner/Classifier Name', tooltip='Name to be used by other widgets to identify your learner/classifier.')

        OWGUI.separator(self.controlArea)

        self.bBox = OWGUI.widgetBox(self.controlArea, 'Basic Properties')

        self.treesBox = OWGUI.spin(self.bBox, self, "trees", 1, self.maxTrees, orientation="horizontal", label="Number of trees in forest")
        self.attributesBox, self.attributesPBox = OWGUI.checkWithSpin(self.bBox, self, "Consider exactly", 1, 10000, "attributes", "attributesP", " "+"random attributes at each split.")
        self.rseedBox = OWGUI.spin(self.bBox, self, "rseed", 0, 100000, orientation="horizontal", label="Seed for random generator ")

        OWGUI.separator(self.controlArea)

        self.pBox = OWGUI.widgetBox(self.controlArea, 'Growth Control')

        self.limitDepthBox, self.limitDepthPBox = OWGUI.checkWithSpin(self.pBox, self, "Maximal depth of individual trees", 1, 1000, "limitDepth", "limitDepthP", "")
        self.preNodeInstBox, self.preNodeInstPBox = OWGUI.checkWithSpin(self.pBox, self, "Stop splitting nodes with ", 1, 1000, "preNodeInst", "preNodeInstP", " or fewer instances")

        OWGUI.separator(self.controlArea)

        OWGUI.separator(self.controlArea)

        self.btnApply = OWGUI.button(self.controlArea, self, "&Apply Changes", callback = self.doBoth, disabled=0, default=True)

        self.resize(100,200)

        self.setLearner()

    def sendReport(self):
        self.reportSettings("Learning parameters",
                            [("Number of trees", self.trees),
                             ("Considered number of attributes at each split", self.attributeP if self.attributes else "not set"),
                             ("Seed for random generator", self.rseed),
                             ("Maximal depth of individual trees", self.limitDepthP if self.limitDepth else "not set"),
                             ("Minimal number of instances in a leaf", self.preNodeInstP if self.preNodeInst else "not limited")
                           ])
        self.reportData(self.data)

    def constructLearner(self):
        rand = random.Random(self.rseed)

        attrs = None
        if self.attributes:
            attrs = self.attributesP

        from Orange.classification.tree import SimpleTreeLearner
        
        smallLearner = SimpleTreeLearner()

        if self.preNodeInst:
            smallLearner.min_instances = self.preNodeInstP 
        else:
            smallLearner.min_instances = 0

        if self.limitDepth:
            smallLearner.max_depth = self.limitDepthP 
        
        learner = orngEnsemble.RandomForestLearner(base_learner=smallLearner, 
                            trees=self.trees, rand=rand, attributes=attrs)

        if self.preprocessor:
            learner = self.preprocessor.wrapLearner(learner)
        learner.name = self.name
        return learner

    def setLearner(self):

        if hasattr(self, "btnApply"):
            self.btnApply.setFocus()

        #assemble learner

        self.learner = self.constructLearner()
        self.send("Learner", self.learner)

        self.error()

    def setData(self, data):
        self.data = self.isDataWithClass(data, orange.VarTypes.Discrete, checkMissing=True) and data or None
        
        #self.setLearner()

        if self.data:
            learner = self.constructLearner()
            pb = OWGUI.ProgressBar(self, iterations=self.trees)
            learner.callback = pb.advance
            try:
                self.classifier = learner(self.data)
                self.classifier.name = self.name
            except Exception, (errValue):
                self.error(str(errValue))
                self.classifier = None
            pb.finish()
        else:
            self.classifier = None

        self.send("Random Forest Classifier", self.classifier)
        
    def setPreprocessor(self, pp):
        self.preprocessor = pp
        self.doBoth()

    def doBoth(self):
        self.setLearner()
        self.setData(self.data)



##############################################################################
# Test the widget, run from DOS prompt
# > python OWDataTable.py)
# Make sure that a sample data set (adult_sample.tab) is in the directory

if __name__=="__main__":
    a=QApplication(sys.argv)
    ow=OWRandomForest()
    a.setMainWidget(ow)

    d = orange.ExampleTable('adult_sample')
    ow.setData(d)

    ow.show()
    a.exec_loop()
    ow.saveSettings()
