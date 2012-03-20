"""
<name>File</name>
<description>Reads data from a file.</description>
<icon>icons/File.png</icon>
<contact>Janez Demsar (janez.demsar(@at@)fri.uni-lj.si)</contact>
<priority>10</priority>
"""

# Don't move this - the line number of the call is important
def call(f,*args,**keyargs):
    return f(*args, **keyargs)

from OWWidget import *
import OWGUI, string, os, sys, warnings
import orngIO

warnings.filterwarnings("error", ".*" , orange.KernelWarning, "OWFile", 11)


class FileNameContextHandler(ContextHandler):
    def match(self, context, imperfect, filename):
        return context.filename == filename and 2


def addOrigin(examples, filename):
    vars = examples.domain.variables + examples.domain.getmetas().values()
    strings = [var for var in vars if isinstance(var, orange.StringVariable)]
    dirname, basename = os.path.split(filename)
    for var in strings:
        if "type" in var.attributes and "origin" not in var.attributes:
            var.attributes["origin"] = dirname
                 

class OWFile(OWWidget):
    settingsList=["recentFiles", "createNewOn", "showAdvanced"]
    contextHandlers = {"": FileNameContextHandler()}

    registeredFileTypes = [ft for ft in orange.getRegisteredFileTypes() if len(ft)>2 and ft[2]]
    dlgFormats = 'Tab-delimited files (*.tab *.txt)\nC4.5 files (*.data)\nAssistant files (*.dat)\nRetis files (*.rda *.rdo)\nBasket files (*.basket)\n' \
                 + "\n".join("%s (%s)" % (ft[:2]) for ft in registeredFileTypes) \
                 + "\nAll files(*.*)"
                 
    formats = {".tab": "Tab-delimited file", ".txt": "Tab-delimited file", ".data": "C4.5 file",
               ".dat": "Assistant file", ".rda": "Retis file", ".rdo": "Retis file",
               ".basket": "Basket file"}
    formats.update(dict((ft[1][2:], ft[0]) for ft in registeredFileTypes))
     
                 
    def __init__(self, parent=None, signalManager = None):
        OWWidget.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        self.inputs = []
        self.outputs = [("Data", ExampleTable)]

        self.recentFiles=["(none)"]
        self.symbolDC = "?"
        self.symbolDK = "~"
        self.createNewOn = 1
        self.domain = None
        self.loadedFile = ""
        self.showAdvanced = 0
        self.loadSettings()

        box = OWGUI.widgetBox(self.controlArea, "Data File", addSpace = True, orientation=0)
        self.filecombo = QComboBox(box)
        self.filecombo.setMinimumWidth(150)
        box.layout().addWidget(self.filecombo)
        button = OWGUI.button(box, self, '...', callback = self.browseFile, disabled=0)
        button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        
        self.reloadBtn = OWGUI.button(box, self, "Reload", callback = self.reload, default=True)
        self.reloadBtn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.reloadBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, ' ')
        self.warnings = OWGUI.widgetLabel(box, ' ')
        
        #Set word wrap so long warnings won't expand the widget
        self.warnings.setWordWrap(True)
        self.warnings.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.MinimumExpanding)
        
        smallWidget = OWGUI.collapsableWidgetBox(self.controlArea, "Advanced settings", self, "showAdvanced", callback=self.adjustSize0)
        
        box = OWGUI.widgetBox(smallWidget, "Missing Value Symbols")
#        OWGUI.widgetLabel(box, "Symbols for missing values in tab-delimited files (besides default ones)")
        
        hbox = OWGUI.indentedBox(box)
        OWGUI.lineEdit(hbox, self, "symbolDC", "Don't care:", labelWidth=80, orientation="horizontal", tooltip="Default values: '~' or '*'")
        OWGUI.lineEdit(hbox, self, "symbolDK", "Don't know:", labelWidth=80, orientation="horizontal", tooltip="Default values: empty fields (space), '?' or 'NA'")

        smallWidget.layout().addSpacing(8)
        OWGUI.radioButtonsInBox(smallWidget, self, "createNewOn", box="New Attributes",
                       label = "Create a new attribute when existing attribute(s) ...",
                       btnLabels = ["Have mismatching order of values",
                                    "Have no common values with the new (recommended)",
                                    "Miss some values of the new attribute",
                                    "... Always create a new attribute"
                               ])
        
        OWGUI.rubber(smallWidget)
        smallWidget.updateControls()
        
        OWGUI.rubber(self.controlArea)
        
        # remove missing data set names
        def exists(path):
            if not os.path.exists(path):
                dirpath, basename = os.path.split(path)
                return os.path.exists(os.path.join("./", basename))
            else:
                return True
        self.recentFiles = filter(exists, self.recentFiles)
        self.setFileList()

        if len(self.recentFiles) > 0 and exists(self.recentFiles[0]):
            self.openFile(self.recentFiles[0], 0, self.symbolDK, self.symbolDC)

        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)

    def adjustSize0(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

    def setFileList(self):
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            if file == "(none)":
                self.filecombo.addItem("(none)")
            else:
                self.filecombo.addItem(os.path.split(file)[1])
        self.filecombo.addItem("Browse documentation data sets...")
        

    def reload(self):
        if self.recentFiles:
            return self.openFile(self.recentFiles[0], 1, self.symbolDK, self.symbolDC)


    def settingsFromWidgetCallback(self, handler, context):
        context.filename = self.loadedFile
        context.symbolDC, context.symbolDK = self.symbolDC, self.symbolDK

    def settingsToWidgetCallback(self, handler, context):
        self.symbolDC, self.symbolDK = context.symbolDC, context.symbolDK

    def selectFile(self, n):
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(1)

        if len(self.recentFiles) > 0:
            self.setFileList()
            self.openFile(self.recentFiles[0], 0, self.symbolDK, self.symbolDC)

    def browseFile(self, inDemos=0):
        "Display a FileDialog and select a file"
        if inDemos:
            try:
                import orngConfiguration
                startfile = orngConfiguration.datasetsPath
            except:
                startfile = ""
                
            if not startfile or not os.path.exists(startfile):
                try:
                    import win32api, win32con
                    t = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SOFTWARE\\Python\\PythonCore\\%i.%i\\PythonPath\\Orange" % sys.version_info[:2], 0, win32con.KEY_READ)
                    t = win32api.RegQueryValueEx(t, "")[0]
                    startfile = t[:t.find("orange")] + "orange\\doc\\datasets"
                except:
                    startfile = ""

            if not startfile or not os.path.exists(startfile):
                widgetsdir = os.path.dirname(OWGUI.__file__)
                orangedir = os.path.dirname(widgetsdir)
                startfile = os.path.join(orangedir, "doc", "datasets")

            if not startfile or not os.path.exists(startfile):
                d = os.getcwd()
                if os.path.basename(d) == "OrangeCanvas":
                    startfile = os.path.join(os.path.dirname(d), "doc", "datasets")
                else:
                    startfile = os.path.join(d, "doc", "datasets")

            if not os.path.exists(startfile):
                QMessageBox.information( None, "File", "Cannot find the directory with example data sets", QMessageBox.Ok + QMessageBox.Default)
                return
        else:
            if len(self.recentFiles) == 0 or self.recentFiles[0] == "(none)":
                startfile = os.path.expanduser("~/")
            else:
                startfile = self.recentFiles[0]

        filename = str(QFileDialog.getOpenFileName(self, 'Open Orange Data File', startfile, self.dlgFormats))

        if filename == "":
            return
        
        if filename in self.recentFiles:
            self.recentFiles.remove(filename)
        self.recentFiles.insert(0, filename)
        self.setFileList()

        self.openFile(self.recentFiles[0], 0, self.symbolDK, self.symbolDC)


    # Open a file, create data from it and send it over the data channel
    def openFile(self, fn, throughReload, DK=None, DC=None):
        if self.processingHandler: 
            self.processingHandler(self, 1)    # focus on active widget
        self.error()
        self.warning()
        self.information()
        
        if not os.path.exists(fn):
            dirname, basename = os.path.split(fn)
            if os.path.exists(os.path.join("./", basename)):
                fn = os.path.join("./", basename)
                self.information("Loading '%s' from the current directory." % basename)

        self.closeContext()
        self.loadedFile = ""
        
        if fn == "(none)":
            self.send("Data", None)
            self.infoa.setText("No data loaded")
            self.infob.setText("")
            self.warnings.setText("")
            return
            
        self.symbolDK = self.symbolDC = ""
        self.openContext("", fn)

        self.loadedFile = ""

        argdict = {"createNewOn": 3-self.createNewOn}
        if DK:
            argdict["DK"] = str(DK)
        if DC:
            argdict["DC"] = str(DC)

        data = None
        try:
            data = call(orange.ExampleTable, fn, **argdict)
            self.loadedFile = fn
        except Exception, (errValue):
            if "is being loaded as" in str(errValue):
                try:
                    data = orange.ExampleTable(fn, **argdict)
                    self.warning(0, str(errValue))
                except:
                    pass
            if data is None:
                self.error(str(errValue))
                self.dataDomain = None
                self.infoa.setText('Data was not loaded due to an error.')
                self.infob.setText("")
                self.warnings.setText("")
                if self.processingHandler: self.processingHandler(self, 0)    # remove focus from this widget
                return
                        
        self.dataDomain = data.domain

        self.infoa.setText('%d example(s), ' % len(data) + '%d attribute(s), ' % len(data.domain.attributes) + '%d meta attribute(s).' % len(data.domain.getmetas()))
        cl = data.domain.classVar
        if cl:
            if cl.varType == orange.VarTypes.Continuous:
                    self.infob.setText('Regression; Numerical class.')
            elif cl.varType == orange.VarTypes.Discrete:
                    self.infob.setText('Classification; Discrete class with %d value(s).' % len(cl.values))
            else:
                self.infob.setText("Class is neither discrete nor continuous.")
        else:
            self.infob.setText("Data has no dependent variable.")

        warnings = ""
        metas = data.domain.getmetas()
        if hasattr(data, "attribute_load_status"):  # For some file formats, this is not populated
            for status, messageUsed, messageNotUsed in [
                                    (orange.Variable.MakeStatus.Incompatible,
                                     "",
                                     "The following attributes already existed but had a different order of values, so new attributes needed to be created"),
                                    (orange.Variable.MakeStatus.NoRecognizedValues,
                                     "The following attributes were reused although they share no common values with the existing attribute of the same names",
                                     "The following attributes were not reused since they share no common values with the existing attribute of the same names"),
                                    (orange.Variable.MakeStatus.MissingValues,
                                     "The following attribute(s) were reused although some values needed to be added",
                                     "The following attribute(s) were not reused since they miss some values")
                                    ]:
                if self.createNewOn > status:
                    message = messageUsed
                else:
                    message = messageNotUsed
                if not message:
                    continue
                attrs = [attr.name for attr, stat in zip(data.domain, data.attributeLoadStatus) if stat == status] \
                      + [attr.name for id, attr in metas.items() if data.metaAttributeLoadStatus.get(id, -99) == status]
                if attrs:
                    jattrs = ", ".join(attrs)
                    if len(jattrs) > 80:
                        jattrs = jattrs[:80] + "..."
                    if len(jattrs) > 30: 
                        warnings += "<li>%s:<br/> %s</li>" % (message, jattrs)
                    else:
                        warnings += "<li>%s: %s</li>" % (message, jattrs)

        self.warnings.setText(warnings)
        #qApp.processEvents()
        #self.adjustSize()

        addOrigin(data, fn)
        # make new data and send it
        fName = os.path.split(fn)[1]
        if "." in fName:
            data.name = fName[:fName.rfind('.')]
        else:
            data.name = fName

        self.dataReport = self.prepareDataReport(data)
        self.send("Data", data)
        if self.processingHandler: self.processingHandler(self, 0)    # remove focus from this widget

    def sendReport(self):
        if hasattr(self, "dataReport"):
            self.reportSettings("File",
                                [("File name", self.loadedFile),
                                 ("Format", self.formats.get(os.path.splitext(self.loadedFile)[1], "unknown format"))])
            self.reportData(self.dataReport)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFile()
    ow.show()
    a.exec_()
    ow.saveSettings()
