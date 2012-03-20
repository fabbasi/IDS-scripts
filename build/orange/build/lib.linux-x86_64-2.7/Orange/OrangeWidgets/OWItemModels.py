from __future__ import with_statement

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from functools import wraps, partial
from collections import defaultdict
from contextlib import contextmanager

class _store(dict):
    pass

def _argsort(seq, cmp=None, key=None, reverse=False):
    if key is not None:
        items = sorted(zip(range(len(seq)), seq), key=lambda i,v: key(v))
    elif cmp is not None:
        items = sorted(zip(range(len(seq)), seq), cmp=lambda a,b: cmp(a[1], b[1]))
    else:
        items = sorted(zip(range(len(seq)), seq), key=seq.__getitem__)
    if reverse:
        items = reversed(items)
    return items


@contextmanager
def signal_blocking(object):
    blocked = object.signalsBlocked()
    object.blockSignals(True)
    yield
    object.blockSignals(blocked)

    
class PyListModel(QAbstractListModel):
    """ A model for displaying python list like objects in Qt item view classes
    """
    MIME_TYPES = ["application/x-Orange-PyListModelData"]
    
    def __init__(self, iterable=[], parent=None,
                 flags=Qt.ItemIsSelectable | Qt.ItemIsEnabled,
                 list_item_role=Qt.DisplayRole,
                 supportedDropActions=Qt.MoveAction):
        QAbstractListModel.__init__(self, parent)
        self._list = []
        self._other_data = []
        self._flags = flags
        self.list_item_role = list_item_role
        
        self._supportedDropActions = supportedDropActions
        self.extend(iterable)
        
    def wrap(self, list):
        """ Wrap the list with this model. All changes to the model
        are done in place on the passed list
        """
        self._list = list
        self._other_data = [_store() for _ in list]
        self.reset()
    
    def index(self, row, column=0, parent=QModelIndex()):
        return QAbstractListModel.createIndex(self, row, column, parent)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return QVariant(str(section))
    
    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self)
    
    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else 1
    
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role in [self.list_item_role, Qt.EditRole]:
            return QVariant(self[index.row()])
        else:
            return QVariant(self._other_data[index.row()].get(role, QVariant()))
    
    def itemData(self, index):
        map = QAbstractListModel.itemData(self, index)
        for key, value in self._other_data[index.row()].items():
            map[key] = QVariant(value)
        return map
    
    def parent(self, index=QModelIndex()):
        return QModelIndex()
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            obj = value.toPyObject()
            self[index.row()] = obj
        else:
            self._other_data[index.row()][role] = value
            self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        return True
        
    def setItemData(self, index, data):
        data = dict(data)
        with signal_blocking(self):
            for role, value in data.items():
                if role == Qt.EditRole:
                    self[index.row()] = value.toPyObject()
                else:
                    self._other_data[index.row()][role] = value
                    
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
        return True
#        return QAbstractListModel.setItemData(self, index, data)
    
    def flags(self, index):
        if index.isValid():
            return self._other_data[index.row()].get("flags", self._flags)
        else:
            return self._flags | Qt.ItemIsDropEnabled
        
    def insertRows(self, row, count, parent=QModelIndex()):
        """ Insert ``count`` rows at ``row``, the list fill be filled 
        with ``None`` 
        """
#        print "Insert", row, count
        if not parent.isValid():
            self.__setslice__(row, row, [None] * count)
            return True
        else:
            return False
        
    def removeRows(self, row, count, parent=QModelIndex()):
        """
        """
#        print "Remove", row, count
        if not parent.isValid():
            self.__delslice__(row, row + count)
            return True
        else:
            return False
    
    def extend(self, iterable):
        list_ = list(iterable)
        self.beginInsertRows(QModelIndex(), len(self), len(self) + len(list_) - 1)
        self._list.extend(list_)
        self._other_data.extend([_store() for _ in list_])
        self.endInsertRows()
    
    def append(self, item):
        self.extend([item])
        
    def insert(self, i, val):
        self.beginInsertRows(QModelIndex(), i, i)
        self._list.insert(i, val)
        self._other_data.insert(i, _store())
        self.endInsertRows()
        
    def remove(self, val):
        i = self._list.index(val)
        self.__delitem__(i)
        
    def pop(self, i):
        item = self._list[i]
        self.__delitem__(i)
        return item
    
    def __len__(self):
        return len(self._list)
    
    def __iter__(self):
        return iter(self._list)
    
    def __getitem__(self, i):
        return self._list[i]
    
    def __getslice__(self, i, j):
        return self._list[i:j]
        
    def __add__(self, iterable):
        # Does not preserve flags or other data.
        return PyListModel(self._list + iterable, self.parent())
    
    def __iadd__(self, iterable):
        self.extend(iterable)
        
    def __delitem__(self, i):
        self.beginRemoveRows(QModelIndex(), i, i)
        del self._list[i]
        del self._other_data[i]
        self.endRemoveRows()
        
    def __delslice__(self, i, j):
        if j > i:
            self.beginRemoveRows(QModelIndex(), i, j - 1)
            del self._list[i:j]
            del self._other_data[i:j]
            self.endRemoveRows()
        
    def __setitem__(self, i, value):
        self._list[i] = value
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.index(i), self.index(i))
        
    def __setslice__(self, i, j, iterable):
        self.__delslice__(i, j)
        all = list(iterable)
        if len(all):
            self.beginInsertRows(QModelIndex(), i, i + len(all) - 1)
            self._list[i:i] = all
            self._other_data[i:i] = [_store() for _ in all]
            self.endInsertRows()
        
    def reverse(self):
        self._list.reverse()
        self._other_data.reverse()
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.index(0), self.index(len(self) -1))
        
    def sort(self, *args, **kwargs):
        indices = _argsort(self._list, *args, **kwargs)
        list = [self._list[i] for i in indices]
        other = [self._other_data[i] for i in indices]
        for i, new_l, new_o in enumerate(zip(list, other)):
            self._list[i] = new_l
            self._other_data[i] = new_o
#        self._list.sort(*args, **kwargs)
        self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.index(0), self.index(len(self) -1))
        
    def __repr__(self):
        return "PyListModel(%s)" % repr(self._list)
    
    def __nonzero__(self):
        return len(self) != 0
    
    #for Python 3000
    def __bool__(self):
        return len(self) != 0
    
    def emitDataChanged(self, indexList):
        if isinstance(indexList, int):
            indexList = [indexList]
        for ind in indexList:
            self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self.index(ind), self.index(ind))
            
    ###########
    # Drag/drop
    ###########
    
    def supportedDropActions(self):
        return self._supportedDropActions
    
    def decode_qt_data(self, data):
        """ Decode internal Qt 'application/x-qabstractitemmodeldatalist'
        mime data 
        """
        stream = QDataStream(data)
        items = []
        while not stream.atEnd():
            row = ds.readInt()
            col = ds.readInt()
            item_count = ds.readInt()
            item = {}
            for i in range(item_count):
                role = ds.readInt()
                value = ds.readQVariant()
                item[role] = value
            items.append((row, column, item))
        return items
    
    def mimeTypes(self):
        return self.MIME_TYPES + list(QAbstractListModel.mimeTypes(self))
    
    def mimeData(self, indexlist):
        if len(indexlist) <= 0:
            return None
        
        items = [self[i.row()] for i in indexlist]
        mime = QAbstractListModel.mimeData(self, indexlist)
        data = cPickle.dumps(vars)
        mime.setData(self.MIME_TYPE, QByteArray(data))
        mime._items = items
        return mime
    
    def dropMimeData(self, mime, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True
        
        if not mime.hasFormat(self.MIME_TYPE):
            return False
        
        if hasattr(mime, "_vars"):
            vars = mime._vars
        else:
            desc = str(mime.data(self.MIME_TYPE))
            vars = cPickle.loads(desc)
        
        return QAbstractListModel.dropMimeData(self, mime, action, row, column, parent)
    
    
import OWGUI
import orange
import Orange
import cPickle

class VariableListModel(PyListModel):
    
    MIME_TYPE = "application/x-Orange-VariableList"
    
    def data(self, index, role=Qt.DisplayRole):
        i = index.row()
        var = self[i]
        if role == Qt.DisplayRole:
            return QVariant(var.name)
        elif role == Qt.DecorationRole:
            return QVariant(OWGUI.getAttributeIcons().get(var.varType, -1))
        elif role == Qt.ToolTipRole:
            return QVariant(self.variable_tooltip(var))
        else:
            return PyListModel.data(self, index, role)
        
    def variable_tooltip(self, var):
        if isinstance(var, Orange.feature.Discrete):
            return self.discrete_variable_tooltip(var)
        elif isinstance(var, Orange.feature.Continuous):
            return self.continuous_variable_toltip(var)
        elif isinstance(var, Orange.feature.String):
            return self.string_variable_tooltip(var)
        
    def variable_labels_tooltip(self, var):
        text = ""
        if var.attributes:
            items = var.attributes.items()
            items = [(safe_text(key), safe_text(value)) for key, value in items]
            labels = map("%s = %s".__mod__, items)
            text += "<br/>Variable Labels:<br/>"
            text += "<br/>".join(labels)
        return text
            
    def discrete_variable_tooltip(self, var):
        text = "<b>%s</b><br/>Discrete with %i values: " % (safe_text(var.name), len(var.values))
        text += ", ".join("%r" % safe_text(v) for v in var.values)
        text += self.variable_labels_tooltip(var)
        return text
            
    def continuous_variable_toltip(self, var):
        text = "<b>%s</b><br/>Continuous" % safe_text(var.name)
        text += self.variable_labels_tooltip(var)
        return text
    
    def string_variable_tooltip(self, var):
        text = "<b>%s</b><br/>String" % safe_text(var.name)
        text += self.variable_labels_tooltip(var)
        return text
    
    def python_variable_tooltip(self, var):
        text = "<b>%s</b><br/>Python" % safe_text(var.name)
        text += self.variable_labels_tooltip(var)
        return text
    
_html_replace = [("<", "&lt;"), (">", "&gt;")]

def safe_text(text):
    for old, new in _html_replace:
        text = text.replace(old, new)
    return text

class VariableEditor(QWidget):
    def __init__(self, var, parent):
        QWidget.__init__(self, parent)
        self.var = var
        layout = QHBoxLayout()
        self._attrs = OWGUI.getAttributeIcons()
        self.type_cb = QComboBox(self)
        for attr, icon in self._attrs.items():
            if attr != -1:
                self.type_cb.addItem(icon, str(attr))
        layout.addWidget(self.type_cb)
        
        self.name_le = QLineEdit(self)
        layout.addWidget(self.name_le)
        
        self.setLayout(layout)
        
        self.connect(self.type_cb, SIGNAL("currentIndexChanged(int)"), self.edited)
        self.connect(self.name_le, SIGNAL("editingFinished()"), self.edited)
    
    def edited(self, *args):
        self.emit(SIGNAL("edited()"))
         
    def setData(self, type, name):
        self.type_cb.setCurrentIndex(self._attr.keys().index(type))
        self.name_le.setText(name)
        
class EnumVariableEditor(VariableEditor):
    def __init__(self, var, parent):
        VariableEditor.__init__(self, var, parent)
        
class FloatVariableEditor(QLineEdit):
    
    def setVariable(self, var):
        self.setText(str(var.name))
        
    def getVariable(self):
        return orange.FloatVariable(str(self.text()))

    
class StringVariableEditor(QLineEdit):
    def setVariable(self, var):
        self.setText(str(var.name))
        
    def getVariable(self):
        return orange.StringVariable(str(self.text()))
        
class VariableDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        var = index.data(Qt.EditRole).toPyObject()
        if isinstance(var, orange.EnumVariable):
            return EnumVariableEditor(parent)
        elif isinstance(var, orange.FloatVariable):
            return FloatVariableEditor(parent)
        elif isinstance(var, orange.StringVariable):
            return StringVariableEditor(parent)
#        return VariableEditor(var, parent)
    
    def setEditorData(self, editor, index):
        var = index.data(Qt.EditRole).toPyObject()
        editor.variable = var
        
    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(editor.variable), Qt.EditRole)
        
#    def displayText(self, value, locale):
#        return value.toPyObject().name
        
class ListSingleSelectionModel(QItemSelectionModel):
    """ Item selection model for list item models with single selection.
    
    Defines signal:
        - selectedIndexChanged(QModelIndex)
        
    """
    def __init__(self, model, parent=None):
        QItemSelectionModel.__init__(self, model, parent)
        self.connect(self, SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.onSelectionChanged)
        
    def onSelectionChanged(self, new, old):
        index = list(new.indexes())
        if index:
            index = index.pop()
        else:
            index = QModelIndex()
        self.emit(SIGNAL("selectedIndexChanged(QModelIndex)"), index)
        
    def selectedRow(self):
        """ Return QModelIndex of the selected row or invalid if no selection. 
        """
        rows = self.selectedRows()
        if rows:
            return rows[0]
        else:
            return QModelIndex()
        
    def select(self, index, flags=QItemSelectionModel.ClearAndSelect):
        if isinstance(index, int):
            index = self.model().index(index)
        return QItemSelectionModel.select(self, index, flags)
    
        
class ModelActionsWidget(QWidget):
    def __init__(self, actions=[], parent=None, direction=QBoxLayout.LeftToRight):
        QWidget.__init__(self, parent)
        self.actions = []
        self.buttons = []
        layout = QBoxLayout(direction)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        for action in actions:
            self.addAction(action)
        self.setLayout(layout)
            
    def actionButton(self, action):
        if isinstance(action, QAction):
            button = QToolButton(self)
            button.setDefaultAction(action)
            return button
        elif isinstance(action, QAbstractButton):
            return action
            
    def insertAction(self, ind, action, *args):
        button = self.actionButton(action)
        self.layout().insertWidget(ind, button, *args)
        self.buttons.insert(ind, button)
        self.actions.insert(ind, action)
        return button
        
    def addAction(self, action, *args):
        return self.insertAction(-1, action, *args)

    
