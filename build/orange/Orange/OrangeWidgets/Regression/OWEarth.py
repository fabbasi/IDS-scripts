"""
<name>Earth</name>
<description>Multivariate Adaptive Regression Splines (MARS)</description>
<category>Regression</category>
<icon>icons/Earth.png<icon>
<priority>100</priority>
<keywords>MARS, Multivariate, Adaptive, Regression, Splines</keywords>
"""

from OWWidget import *
import OWGUI
import Orange

from Orange.regression import earth
from orngWrap import PreprocessedLearner
 
class OWEarth(OWWidget):
    settingsList = ["name", "degree", "terms", "penalty"]
    
    def __init__(self, parent=None, signalManager=None,
                 title="Earth"):
        OWWidget.__init__(self, parent, signalManager, title, wantMainArea=False)
        
        self.inputs = [("Data", Orange.data.Table, self.set_data), ("Preprocessor", PreprocessedLearner, self.set_preprocessor)]
        self.outputs = [("Learner", earth.EarthLearner), ("Predictor", earth.EarthClassifier)]
        
        self.name = "Earth Learner"
        self.degree = 1
        self.terms = 21
        self.penalty = 2
        
        self.loadSettings()
        
        #####
        # GUI
        #####
        
        OWGUI.lineEdit(self.controlArea, self, "name", 
                       box="Learner/Classifier Name",
                       tooltip="Name for the learner/predictor")
        
        box = OWGUI.widgetBox(self.controlArea, "Forward Pass", addSpace=True)
        OWGUI.spin(box, self, "degree", 1, 3, step=1,
                   label="Max. term degree", 
                   tooltip="Maximum degree of the terms derived (number of hinge functions).")
        s = OWGUI.spin(box, self, "terms", 1, 200, step=1,
                       label="Max. terms",
                       tooltip="Maximum number of terms derived in the forward pass.")
        s.control.setSpecialValueText("Automatic")
        
        box = OWGUI.widgetBox(self.controlArea, "Pruning Pass", addSpace=True)
        OWGUI.doubleSpin(box, self, "penalty", min=0.0, max=10.0, step=0.25,
                   label="Knot penalty")
        
        OWGUI.button(self.controlArea, self, "&Apply",
                     callback=self.apply)
        
        self.data = None
        self.preprocessor = None
        self.resize(300, 200)
        
        self.apply()
        
    def set_data(self, data=None):
        self.data = data
            
    def set_preprocessor(self, pproc=None):
        self.preprocessor = pproc
        
    def handleNewSignals(self):
        self.apply()
            
    def apply(self):
        learner = earth.EarthLearner(degree=self.degree,
                                    terms=self.terms if self.terms >= 2 else None,
                                    penalty=self.penalty,
                                    name=self.name)
        predictor = None
        if self.preprocessor:
            learner = self.preprocessor.wrapLearner(learner)
        
        self.error(0)
        if self.data is not None:
            try:
                predictor = learner(self.data)
                predictor.name = self.name
            except Exception, ex:
                self.error(0, "An error during learning: %r" % ex)
            
        self.send("Learner", learner)
        self.send("Predictor", predictor)
        
    def sendReport(self):
        self.reportSettings("Learning parameters", 
                            [("Degree", self.degree),
                             ("Terms", self.terms if self.terms >= 2 else "Automatic"),
                             ("Knot penalty", "%.2f" % self.penalty)
                             ])
        self.reportData(self.data)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWEarth()
    w.set_data(Orange.data.Table("auto-mpg"))
    w.show()
    app.exec_()
    w.saveSettings()
            
            
        
        
        
        