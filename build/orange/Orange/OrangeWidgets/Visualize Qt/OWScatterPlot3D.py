'''
<name>Scatterplot 3D</name>
<icon>icons/ScatterPlot.png</icon>
<priority>2001</priority>
'''

from math import log10, ceil, floor

from OWWidget import *
from plot.owplot3d import *
from plot.owtheme import ScatterLightTheme, ScatterDarkTheme
from plot import OWPoint

import orange
Discrete = orange.VarTypes.Discrete
Continuous = orange.VarTypes.Continuous

from Orange.preprocess.scaling import get_variable_values_sorted

import OWGUI
import orngVizRank
from OWkNNOptimization import *
from orngScaleScatterPlotData import *

import numpy

TooltipKind = enum('NONE', 'VISIBLE', 'ALL')
Axis = enum('X', 'Y', 'Z')

class Plane:
    '''Internal convenience class.'''
    def __init__(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def normal(self):
        v1 = self.A - self.B
        v2 = self.A - self.C
        return QVector3D.crossProduct(v1, v2).normalized()

    def visible_from(self, location):
        normal = self.normal()
        loc_plane = (self.A - location).normalized()
        if QVector3D.dotProduct(normal, loc_plane) > 0:
            return False
        return True

class Edge:
    def __init__(self, v0, v1):
        self.v0 = v0
        self.v1 = v1

    def __add__(self, vec):
        return Edge(self.v0 + vec, self.v1 + vec)

def nicenum(x, round):
    if x <= 0.:
        return x # TODO: what to do in such cases?
    expv = floor(log10(x))
    f = x / pow(10., expv)
    if round:
        if f < 1.5: nf = 1.
        elif f < 3.: nf = 2.
        elif f < 7.: nf = 5.
        else: nf = 10.
    else:
        if f <= 1.: nf = 1.
        elif f <= 2.: nf = 2.
        elif f <= 5.: nf = 5.
        else: nf = 10.
    return nf * pow(10., expv)

def loose_label(min_value, max_value, num_ticks):
    '''Algorithm by Paul S. Heckbert (Graphics Gems).
       Generates a list of "nice" values between min and max,
       given the number of ticks. Also returns the number
       of fractional digits to use.
    '''
    range = nicenum(max_value-min_value, False)
    d = nicenum(range / float(num_ticks-1), True)
    if d <= 0.: # TODO
        return numpy.arange(min_value, max_value, (max_value-min_value)/num_ticks), 1
    plot_min = floor(min_value / d) * d
    plot_max = ceil(max_value / d) * d
    num_frac = int(max(-floor(log10(d)), 0))
    return numpy.arange(plot_min, plot_max + 0.5*d, d), num_frac

class ScatterPlot(OWPlot3D, orngScaleScatterPlotData):
    def __init__(self, parent=None):
        self.parent = parent
        OWPlot3D.__init__(self, parent)
        orngScaleScatterPlotData.__init__(self)

        self._theme = ScatterLightTheme()
        self.show_grid = True
        self.show_chassis = True
        self.show_axes = True
        self._build_axes()

        self._x_axis_labels = None
        self._y_axis_labels = None
        self._z_axis_labels = None

        self._x_axis_title = ''
        self._y_axis_title = ''
        self._z_axis_title = ''

        # These are public
        self.show_x_axis_title = self.show_y_axis_title = self.show_z_axis_title = True

        self.animate_plot = False

    def set_data(self, data, subset_data=None, **args):
        if data == None:
            return
        args['skipIfSame'] = False
        orngScaleScatterPlotData.set_data(self, data, subset_data, **args)
        # Optimization: calling set_plot_data here (and not in update_data) because data won't change.
        OWPlot3D.set_plot_data(self, self.scaled_data, self.scaled_subset_data)
        OWPlot3D.initializeGL(self)

    def update_data(self, x_attr, y_attr, z_attr,
                    color_attr, symbol_attr, size_attr, label_attr):
        if self.data == None:
            return
        self.before_draw_callback = self.before_draw

        color_discrete = size_discrete = False

        color_index = -1
        if color_attr != '' and color_attr != '(Same color)':
            color_index = self.attribute_name_index[color_attr]
            if self.data_domain[color_attr].varType == Discrete:
                color_discrete = True
                self.discrete_palette.setNumberOfColors(len(self.data_domain[color_attr].values))

        symbol_index = -1
        num_symbols_used = -1
        if symbol_attr != '' and symbol_attr != 'Same symbol)' and\
           len(self.data_domain[symbol_attr].values) < len(Symbol) and\
           self.data_domain[symbol_attr].varType == Discrete:
            symbol_index = self.attribute_name_index[symbol_attr]
            num_symbols_used = len(self.data_domain[symbol_attr].values)

        size_index = -1
        if size_attr != '' and size_attr != '(Same size)':
            size_index = self.attribute_name_index[size_attr]
            if self.data_domain[size_attr].varType == Discrete:
                size_discrete = True

        label_index = -1
        if label_attr != '' and label_attr != '(No labels)':
            label_index = self.attribute_name_index[label_attr]

        x_index = self.attribute_name_index[x_attr]
        y_index = self.attribute_name_index[y_attr]
        z_index = self.attribute_name_index[z_attr]

        x_discrete = self.data_domain[x_attr].varType == Discrete
        y_discrete = self.data_domain[y_attr].varType == Discrete
        z_discrete = self.data_domain[z_attr].varType == Discrete

        colors = []
        if color_discrete:
            for i in range(len(self.data_domain[color_attr].values)):
                c = self.discrete_palette[i]
                colors.append(c)

        data_scale = [self.attr_values[x_attr][1] - self.attr_values[x_attr][0],
                      self.attr_values[y_attr][1] - self.attr_values[y_attr][0],
                      self.attr_values[z_attr][1] - self.attr_values[z_attr][0]]
        data_translation = [self.attr_values[x_attr][0],
                            self.attr_values[y_attr][0],
                            self.attr_values[z_attr][0]]
        data_scale = 1. / numpy.array(data_scale)
        if x_discrete:
            data_scale[0] = 0.5 / float(len(self.data_domain[x_attr].values))
            data_translation[0] = 1.
        if y_discrete:
            data_scale[1] = 0.5 / float(len(self.data_domain[y_attr].values))
            data_translation[1] = 1.
        if z_discrete:
            data_scale[2] = 0.5 / float(len(self.data_domain[z_attr].values))
            data_translation[2] = 1.

        self.data_scale = QVector3D(*data_scale)
        self.data_translation = QVector3D(*data_translation)

        self._x_axis_labels = None
        self._y_axis_labels = None
        self._z_axis_labels = None

        self.clear()

        attr_indices = [x_index, y_index, z_index]
        if color_index > -1:
            attr_indices.append(color_index)
        if size_index > -1:
            attr_indices.append(size_index)
        if symbol_index > -1:
            attr_indices.append(symbol_index)
        if label_index > -1:
            attr_indices.append(label_index)

        valid_data = self.getValidList(attr_indices)
        self.set_valid_data(valid_data)

        self.set_features(x_index, y_index, z_index,
            color_index, symbol_index, size_index, label_index,
            colors, num_symbols_used,
            x_discrete, y_discrete, z_discrete)

        ## Legend
        def_color = QColor(150, 150, 150)
        def_symbol = 0
        def_size = 10

        if color_discrete:
            num = len(self.data_domain[color_attr].values)
            values = get_variable_values_sorted(self.data_domain[color_attr])
            for ind in range(num):
                self.legend().add_item(color_attr, values[ind], OWPoint(def_symbol, self.discrete_palette[ind], def_size))

        if symbol_index != -1:
            num = len(self.data_domain[symbol_attr].values)
            values = get_variable_values_sorted(self.data_domain[symbol_attr])
            for ind in range(num):
                self.legend().add_item(symbol_attr, values[ind], OWPoint(ind, def_color, def_size))

        if size_discrete:
            num = len(self.data_domain[size_attr].values)
            values = get_variable_values_sorted(self.data_domain[size_attr])
            for ind in range(num):
                self.legend().add_item(size_attr, values[ind], OWPoint(def_symbol, def_color, 6 + round(ind * 5 / len(values))))

        if color_index != -1 and self.data_domain[color_attr].varType == Continuous:
            self.legend().add_color_gradient(color_attr, [("%%.%df" % self.data_domain[color_attr].numberOfDecimals % v) for v in self.attr_values[color_attr]])

        self.legend().max_size = QSize(400, 400)
        self.legend().set_floating(True)
        self.legend().set_orientation(Qt.Vertical)
        if self.legend().pos().x() == 0:
            self.legend().setPos(QPointF(100, 100))
        self.legend().update_items()
        self.legend().setVisible(self.show_legend)

        ## Axes
        self._x_axis_title = x_attr
        self._y_axis_title = y_attr
        self._z_axis_title = z_attr

        if x_discrete:
            self._x_axis_labels = get_variable_values_sorted(self.data_domain[x_attr])
        if y_discrete:
            self._y_axis_labels = get_variable_values_sorted(self.data_domain[y_attr])
        if z_discrete:
            self._z_axis_labels = get_variable_values_sorted(self.data_domain[z_attr])

        self.update()

    def before_draw(self):
        if self.show_grid:
            self._draw_grid()
        if self.show_chassis:
            self._draw_chassis()
        if self.show_axes:
            self._draw_axes()

    def _draw_chassis(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixd(numpy.array(self.projection.data(), dtype=float))
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixd(numpy.array(self.view.data(), dtype=float))
        glMultMatrixd(numpy.array(self.model.data(), dtype=float))

        # TODO: line stipple with shaders?
        self.qglColor(self._theme.axis_values_color)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x00FF)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        edges = [self.x_axis, self.y_axis, self.z_axis,
                 self.x_axis+self.unit_z, self.x_axis+self.unit_y,
                 self.x_axis+self.unit_z+self.unit_y,
                 self.y_axis+self.unit_x, self.y_axis+self.unit_z,
                 self.y_axis+self.unit_x+self.unit_z,
                 self.z_axis+self.unit_x, self.z_axis+self.unit_y,
                 self.z_axis+self.unit_x+self.unit_y]
        glBegin(GL_LINES)
        for edge in edges:
            start, end = edge.v0, edge.v1
            glVertex3f(start.x(), start.y(), start.z())
            glVertex3f(end.x(), end.y(), end.z())
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

    def _map_to_original(self, point, coord_index):
        v = vec_div(self.map_to_data(point), self.data_scale) + self.data_translation
        if coord_index == 0:
            return v.x()
        elif coord_index == 1:
            return v.y()
        elif coord_index == 2:
            return v.z()

    def _draw_grid(self):
        self.renderer.set_transform(self.model, self.view, self.projection)
        cam_in_space = self.camera * self.camera_distance

        def _draw_grid_plane(axis0, axis1, normal0, normal1, i, j):
            for axis, normal, coord_index in zip([axis0, axis1], [normal0, normal1], [i, j]):
                start, end = axis.v0, axis.v1
                start_value = self._map_to_original(start, coord_index)
                end_value = self._map_to_original(end, coord_index)
                values, _ = loose_label(start_value, end_value, 7)
                for value in values:
                    if not (start_value <= value <= end_value):
                        continue
                    position = start + (end-start)*((value-start_value) / float(end_value-start_value))
                    self.renderer.draw_line(
                        position,
                        position - normal*1,
                        color=self._theme.grid_color)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        planes = [self.axis_plane_xy, self.axis_plane_yz,
                  self.axis_plane_xy_back, self.axis_plane_yz_right]
        axes = [[self.x_axis, self.y_axis],
                [self.y_axis, self.z_axis],
                [self.x_axis+self.unit_z, self.y_axis+self.unit_z],
                [self.z_axis+self.unit_x, self.y_axis+self.unit_x]]
        normals = [[QVector3D(0,-1, 0), QVector3D(-1, 0, 0)],
                   [QVector3D(0, 0,-1), QVector3D( 0,-1, 0)],
                   [QVector3D(0,-1, 0), QVector3D(-1, 0, 0)],
                   [QVector3D(0,-1, 0), QVector3D( 0, 0,-1)]]
        coords = [[0, 1],
                  [1, 2],
                  [0, 1],
                  [2, 1]]
        visible_planes = [plane.visible_from(cam_in_space) for plane in planes]
        xz_visible = not self.axis_plane_xz.visible_from(cam_in_space)
        if xz_visible:
            _draw_grid_plane(self.x_axis, self.z_axis, QVector3D(0, 0, -1), QVector3D(-1, 0, 0), 0, 2)
        for visible, (axis0, axis1), (normal0, normal1), (i, j) in\
             zip(visible_planes, axes, normals, coords):
            if not visible:
                _draw_grid_plane(axis0, axis1, normal0, normal1, i, j)

        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

    def _build_axes(self):
        edge_half = 1. / 2.
        self.x_axis = Edge(QVector3D(-edge_half, -edge_half, -edge_half), QVector3D( edge_half, -edge_half, -edge_half))
        self.y_axis = Edge(QVector3D(-edge_half, -edge_half, -edge_half), QVector3D(-edge_half,  edge_half, -edge_half))
        self.z_axis = Edge(QVector3D(-edge_half, -edge_half, -edge_half), QVector3D(-edge_half, -edge_half,  edge_half))

        self.unit_x = unit_x = QVector3D(1, 0, 0)
        self.unit_y = unit_y = QVector3D(0, 1, 0)
        self.unit_z = unit_z = QVector3D(0, 0, 1)
 
        A = self.y_axis.v1
        B = self.y_axis.v1 + unit_x
        C = self.x_axis.v1
        D = self.x_axis.v0

        E = A + unit_z
        F = B + unit_z
        G = C + unit_z
        H = D + unit_z

        self.axis_plane_xy = Plane(A, B, C, D)
        self.axis_plane_yz = Plane(A, D, H, E)
        self.axis_plane_xz = Plane(D, C, G, H)

        self.axis_plane_xy_back = Plane(H, G, F, E)
        self.axis_plane_yz_right = Plane(B, F, G, C)
        self.axis_plane_xz_top = Plane(E, F, B, A)

    def _draw_axes(self):
        self.renderer.set_transform(self.model, self.view, self.projection)

        def _draw_axis(axis):
            glLineWidth(2)
            self.renderer.draw_line(axis.v0,
                                    axis.v1,
                                    color=self._theme.axis_color)
            glLineWidth(1)

        def _draw_discrete_axis_values(axis, coord_index, normal, axis_labels):
            start, end = axis.v0, axis.v1
            start_value = self._map_to_original(start, coord_index)
            end_value = self._map_to_original(end, coord_index)
            length = end_value - start_value
            for i, label in enumerate(axis_labels):
                value = (i + 1) * 2
                if start_value <= value <= end_value:
                    position = start + (end-start)*((value-start_value) / length)
                    self.renderer.draw_line(
                        position,
                        position + normal*0.03,
                        color=self._theme.axis_values_color)
                    position += normal * 0.1
                    self.renderText(position.x(),
                                    position.y(),
                                    position.z(),
                                    label, font=self._theme.labels_font)

        def _draw_values(axis, coord_index, normal, axis_labels):
            glLineWidth(1)
            if axis_labels != None:
                _draw_discrete_axis_values(axis, coord_index, normal, axis_labels)
                return
            start, end = axis.v0, axis.v1
            start_value = self._map_to_original(start, coord_index)
            end_value = self._map_to_original(end, coord_index)
            values, num_frac = loose_label(start_value, end_value, 7)
            for value in values:
                if not (start_value <= value <= end_value):
                    continue
                position = start + (end-start)*((value-start_value) / float(end_value-start_value))
                text = ('%%.%df' % num_frac) % value
                self.renderer.draw_line(
                    position,
                    position+normal*0.03,
                    color=self._theme.axis_values_color)
                position += normal * 0.1
                self.renderText(position.x(),
                                position.y(),
                                position.z(),
                                text, font=self._theme.axis_font)

        def _draw_axis_title(axis, title, normal):
            middle = (axis.v0 + axis.v1) / 2.
            middle += normal * 0.1 if axis.v0.y() != axis.v1.y() else normal * 0.2
            self.renderText(middle.x(), middle.y(), middle.z(),
                            title,
                            font=self._theme.axis_title_font)

        glDisable(GL_DEPTH_TEST)
        glLineWidth(1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        cam_in_space = self.camera * self.camera_distance

        # TODO: the code below is horrible and should be simplified
        planes = [self.axis_plane_xy, self.axis_plane_yz,
                  self.axis_plane_xy_back, self.axis_plane_yz_right]
        normals = [[QVector3D(0,-1, 0), QVector3D(-1, 0, 0)],
                   [QVector3D(0, 0,-1), QVector3D( 0,-1, 0)],
                   [QVector3D(0,-1, 0), QVector3D(-1, 0, 0)],
                   [QVector3D(0,-1, 0), QVector3D( 0, 0,-1)]]
        visible_planes = [plane.visible_from(cam_in_space) for plane in planes]
        xz_visible = not self.axis_plane_xz.visible_from(cam_in_space)

        if visible_planes[0 if xz_visible else 2]:
            _draw_axis(self.x_axis)
            _draw_values(self.x_axis, 0, QVector3D(0, 0, -1), self._x_axis_labels)
            if self.show_x_axis_title:
                _draw_axis_title(self.x_axis, self._x_axis_title, QVector3D(0, 0, -1))
        elif visible_planes[2 if xz_visible else 0]:
            _draw_axis(self.x_axis + self.unit_z)
            _draw_values(self.x_axis + self.unit_z, 0, QVector3D(0, 0, 1), self._x_axis_labels)
            if self.show_x_axis_title:
                _draw_axis_title(self.x_axis + self.unit_z,
                                self._x_axis_title, QVector3D(0, 0, 1))

        if visible_planes[1 if xz_visible else 3]:
            _draw_axis(self.z_axis)
            _draw_values(self.z_axis, 2, QVector3D(-1, 0, 0), self._z_axis_labels)
            if self.show_z_axis_title:
                _draw_axis_title(self.z_axis, self._z_axis_title, QVector3D(-1, 0, 0))
        elif visible_planes[3 if xz_visible else 1]:
            _draw_axis(self.z_axis + self.unit_x)
            _draw_values(self.z_axis + self.unit_x, 2, QVector3D(1, 0, 0), self._z_axis_labels)
            if self.show_z_axis_title:
                _draw_axis_title(self.z_axis + self.unit_x, self._z_axis_title, QVector3D(1, 0, 0))

        try:
            rightmost_visible = visible_planes[::-1].index(True)
        except ValueError:
            return
        if rightmost_visible == 0 and visible_planes[0] == True:
            rightmost_visible = 3
        y_axis_translated = [self.y_axis+self.unit_x,
                             self.y_axis+self.unit_x+self.unit_z,
                             self.y_axis+self.unit_z,
                             self.y_axis]
        normals = [QVector3D(1, 0, 0),
                   QVector3D(0, 0, 1),
                   QVector3D(-1,0, 0),
                   QVector3D(0, 0,-1)]
        axis = y_axis_translated[rightmost_visible]
        normal = normals[rightmost_visible]
        _draw_axis(axis)
        _draw_values(axis, 1, normal, self._y_axis_labels)
        if self.show_y_axis_title:
            _draw_axis_title(axis, self._y_axis_title, normal)

class OWScatterPlot3D(OWWidget):
    settingsList = ['plot.show_legend', 'plot.symbol_size', 'plot.show_x_axis_title', 'plot.show_y_axis_title',
                    'plot.show_z_axis_title', 'plot.show_legend', 'plot.use_2d_symbols', 'plot.symbol_scale',
                    'plot.alpha_value', 'plot.show_grid', 'plot.pitch', 'plot.yaw',
                    'plot.show_chassis', 'plot.show_axes',
                    'auto_send_selection', 'auto_send_selection_update',
                    'plot.jitter_size', 'plot.jitter_continuous', 'dark_theme']
    contextHandlers = {'': DomainContextHandler('', ['x_attr', 'y_attr', 'z_attr'])}
    jitter_sizes = [0.0, 0.1, 0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 40, 50]

    def __init__(self, parent=None, signalManager=None, name='ScatterPlot 3D'):
        OWWidget.__init__(self, parent, signalManager, name, True)

        self.inputs = [('Data', ExampleTable, self.set_data, Default), ('Subset Examples', ExampleTable, self.set_subset_data)]
        self.outputs = [('Selected Data', ExampleTable), ('Other Data', ExampleTable)]

        self.x_attr = ''
        self.y_attr = ''
        self.z_attr = ''

        self.x_attr_discrete = False
        self.y_attr_discrete = False
        self.z_attr_discrete = False

        self.color_attr = ''
        self.size_attr = ''
        self.symbol_attr = ''
        self.label_attr = ''

        self.tabs = OWGUI.tabWidget(self.controlArea)
        self.main_tab = OWGUI.createTabPage(self.tabs, 'Main')
        self.settings_tab = OWGUI.createTabPage(self.tabs, 'Settings', canScroll=True)

        self.x_attr_cb = OWGUI.comboBox(self.main_tab, self, 'x_attr', box='X-axis attribute',
            tooltip='Attribute to plot on X axis.',
            callback=self.on_axis_change,
            sendSelectedValue=1,
            valueType=str)

        self.y_attr_cb = OWGUI.comboBox(self.main_tab, self, 'y_attr', box='Y-axis attribute',
            tooltip='Attribute to plot on Y axis.',
            callback=self.on_axis_change,
            sendSelectedValue=1,
            valueType=str)

        self.z_attr_cb = OWGUI.comboBox(self.main_tab, self, 'z_attr', box='Z-axis attribute',
            tooltip='Attribute to plot on Z axis.',
            callback=self.on_axis_change,
            sendSelectedValue=1,
            valueType=str)

        self.color_attr_cb = OWGUI.comboBox(self.main_tab, self, 'color_attr', box='Point color',
            tooltip='Attribute to use for point color',
            callback=self.on_axis_change,
            sendSelectedValue=1,
            valueType=str)

        # Additional point properties (labels, size, symbol).
        additional_box = OWGUI.widgetBox(self.main_tab, 'Additional Point Properties')
        self.size_attr_cb = OWGUI.comboBox(additional_box, self, 'size_attr', label='Point size:',
            tooltip='Attribute to use for point size',
            callback=self.on_axis_change,
            indent=10,
            emptyString='(Same size)',
            sendSelectedValue=1,
            valueType=str)

        self.symbol_attr_cb = OWGUI.comboBox(additional_box, self, 'symbol_attr', label='Point symbol:',
            tooltip='Attribute to use for point symbol',
            callback=self.on_axis_change,
            indent=10,
            emptyString='(Same symbol)',
            sendSelectedValue=1,
            valueType=str)

        self.label_attr_cb = OWGUI.comboBox(additional_box, self, 'label_attr', label='Point label:',
            tooltip='Attribute to use for pointLabel',
            callback=self.on_axis_change,
            indent=10,
            emptyString='(No labels)',
            sendSelectedValue=1,
            valueType=str)

        self.plot = ScatterPlot(self)
        self.vizrank = OWVizRank(self, self.signalManager, self.plot, orngVizRank.SCATTERPLOT3D, 'ScatterPlot3D')
        self.optimization_dlg = self.vizrank

        self.optimization_buttons = OWGUI.widgetBox(self.main_tab, 'Optimization dialogs', orientation='horizontal')
        OWGUI.button(self.optimization_buttons, self, 'VizRank', callback=self.vizrank.reshow,
            tooltip='Opens VizRank dialog, where you can search for interesting projections with different subsets of attributes',
            debuggingEnabled=0)

        box = OWGUI.widgetBox(self.settings_tab, 'Point properties')
        OWGUI.hSlider(box, self, 'plot.symbol_scale', label='Symbol scale',
            minValue=1, maxValue=20,
            tooltip='Scale symbol size',
            callback=self.on_checkbox_update)

        OWGUI.hSlider(box, self, 'plot.alpha_value', label='Transparency',
            minValue=10, maxValue=255,
            tooltip='Point transparency value',
            callback=self.on_checkbox_update)
        OWGUI.rubber(box)

        box = OWGUI.widgetBox(self.settings_tab, 'Jittering Options')
        self.jitter_size_combo = OWGUI.comboBox(box, self, 'plot.jitter_size', label='Jittering size (% of size)'+'  ',
            orientation='horizontal',
            callback=self.handleNewSignals,
            items=self.jitter_sizes,
            sendSelectedValue=1,
            valueType=float)
        OWGUI.checkBox(box, self, 'plot.jitter_continuous', 'Jitter continuous attributes',
            callback=self.handleNewSignals,
            tooltip='Does jittering apply also on continuous attributes?')

        self.dark_theme = False

        box = OWGUI.widgetBox(self.settings_tab, 'General settings')
        OWGUI.checkBox(box, self, 'plot.show_x_axis_title',   'X axis title',   callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.show_y_axis_title',   'Y axis title',   callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.show_z_axis_title',   'Z axis title',   callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.show_legend',         'Show legend',    callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.use_2d_symbols',      '2D symbols',     callback=self.update_plot)
        OWGUI.checkBox(box, self, 'dark_theme',               'Dark theme',     callback=self.on_theme_change)
        OWGUI.checkBox(box, self, 'plot.show_grid',           'Show grid',      callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.show_axes',           'Show axes',      callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.show_chassis',        'Show chassis',   callback=self.on_checkbox_update)
        OWGUI.checkBox(box, self, 'plot.hide_outside',        'Hide outside',   callback=self.on_checkbox_update)
        OWGUI.rubber(box)

        box = OWGUI.widgetBox(self.settings_tab, 'Mouse', orientation = "horizontal")
        OWGUI.hSlider(box, self, 'plot.mouse_sensitivity', label='Sensitivity', minValue=1, maxValue=10,
                      step=1,
                      callback=self.plot.update,
                      tooltip='Change mouse sensitivity')

        gui = self.plot.gui
        buttons = gui.default_zoom_select_buttons
        buttons.insert(2, (gui.UserButton, 'Rotate', 'state', ROTATING, None, 'Dlg_undo'))
        self.zoom_select_toolbar = gui.zoom_select_toolbar(self.main_tab, buttons=buttons)
        self.connect(self.zoom_select_toolbar.buttons[gui.SendSelection], SIGNAL("clicked()"), self.send_selection)
        self.connect(self.zoom_select_toolbar.buttons[gui.Zoom], SIGNAL("clicked()"), self.plot.unselect_all_points)
        self.plot.set_selection_behavior(OWPlot.ReplaceSelection)

        self.tooltip_kind = TooltipKind.NONE
        box = OWGUI.widgetBox(self.settings_tab, 'Tooltips Settings')
        OWGUI.comboBox(box, self, 'tooltip_kind', items = [
            'Don\'t Show Tooltips', 'Show Visible Attributes', 'Show All Attributes'])

        self.plot.mouseover_callback = self.mouseover_callback

        self.main_tab.layout().addStretch(100)
        self.settings_tab.layout().addStretch(100)

        self.mainArea.layout().addWidget(self.plot)
        self.connect(self.graphButton, SIGNAL('clicked()'), self.plot.save_to_file)

        self.loadSettings()
        self.plot.update_camera()
        self.on_theme_change()

        self.data = None
        self.subset_data = None
        self.resize(1100, 600)

    def mouseover_callback(self, index):
        if self.tooltip_kind == TooltipKind.VISIBLE:
            self.plot.show_tooltip(self.get_example_tooltip(self.data[index], self.shown_attrs))
        elif self.tooltip_kind == TooltipKind.ALL:
            self.plot.show_tooltip(self.get_example_tooltip(self.data[index]))

    def get_example_tooltip(self, example, indices=None, max_indices=20):
        if indices and type(indices[0]) == str:
            indices = [self.plot.attribute_name_index[i] for i in indices]
        if not indices:
            indices = range(len(self.data.domain.attributes))

        if example.domain.classVar:
            classIndex = self.plot.attribute_name_index[example.domain.classVar.name]
            while classIndex in indices:
                indices.remove(classIndex)

        text = '<b>Attributes:</b><br>'
        for index in indices[:max_indices]:
            attr = self.plot.data_domain[index].name
            if attr not in example.domain:  text += '&nbsp;'*4 + '%s = ?<br>' % (attr)
            elif example[attr].isSpecial(): text += '&nbsp;'*4 + '%s = ?<br>' % (attr)
            else:                           text += '&nbsp;'*4 + '%s = %s<br>' % (attr, str(example[attr]))

        if len(indices) > max_indices:
            text += '&nbsp;'*4 + ' ... <br>'

        if example.domain.classVar:
            text = text[:-4]
            text += '<hr><b>Class:</b><br>'
            if example.getclass().isSpecial(): text += '&nbsp;'*4 + '%s = ?<br>' % (example.domain.classVar.name)
            else:                              text += '&nbsp;'*4 + '%s = %s<br>' % (example.domain.classVar.name, str(example.getclass()))

        if len(example.domain.getmetas()) != 0:
            text = text[:-4]
            text += '<hr><b>Meta attributes:</b><br>'
            for key in example.domain.getmetas():
                try: text += '&nbsp;'*4 + '%s = %s<br>' % (example.domain[key].name, str(example[key]))
                except: pass
        return text[:-4]

    def set_data(self, data=None):
        self.closeContext()
        self.vizrank.clearResults()
        same_domain = self.data and data and\
            data.domain.checksum() == self.data.domain.checksum()
        self.data = data
        if not same_domain:
            self.init_attr_values()
        self.openContext('', data)

    def init_attr_values(self):
        self.x_attr_cb.clear()
        self.y_attr_cb.clear()
        self.z_attr_cb.clear()
        self.color_attr_cb.clear()
        self.size_attr_cb.clear()
        self.symbol_attr_cb.clear()
        self.label_attr_cb.clear()

        self.discrete_attrs = {}

        if not self.data:
            return

        self.color_attr_cb.addItem('(Same color)')
        self.label_attr_cb.addItem('(No labels)')
        self.symbol_attr_cb.addItem('(Same symbol)')
        self.size_attr_cb.addItem('(Same size)')

        icons = OWGUI.getAttributeIcons() 
        for metavar in [self.data.domain.getmeta(mykey) for mykey in self.data.domain.getmetas().keys()]:
            self.label_attr_cb.addItem(icons[metavar.varType], metavar.name)

        for attr in self.data.domain:
            if attr.varType in [Discrete, Continuous]:
                self.x_attr_cb.addItem(icons[attr.varType], attr.name)
                self.y_attr_cb.addItem(icons[attr.varType], attr.name)
                self.z_attr_cb.addItem(icons[attr.varType], attr.name)
                self.color_attr_cb.addItem(icons[attr.varType], attr.name)
                self.size_attr_cb.addItem(icons[attr.varType], attr.name)
            if attr.varType == Discrete and len(attr.values) < len(Symbol):
                self.symbol_attr_cb.addItem(icons[attr.varType], attr.name)
            self.label_attr_cb.addItem(icons[attr.varType], attr.name)

        self.x_attr = str(self.x_attr_cb.itemText(0))
        if self.y_attr_cb.count() > 1:
            self.y_attr = str(self.y_attr_cb.itemText(1))
        else:
            self.y_attr = str(self.y_attr_cb.itemText(0))

        if self.z_attr_cb.count() > 2:
            self.z_attr = str(self.z_attr_cb.itemText(2))
        else:
            self.z_attr = str(self.z_attr_cb.itemText(0))

        if self.data.domain.classVar and self.data.domain.classVar.varType in [Discrete, Continuous]:
            self.color_attr = self.data.domain.classVar.name
        else:
            self.color_attr = ''

        self.symbol_attr = self.size_attr = self.label_attr = ''
        self.shown_attrs = [self.x_attr, self.y_attr, self.z_attr, self.color_attr]

    def set_subset_data(self, data=None):
        self.subset_data = data

    def handleNewSignals(self):
        self.plot.set_data(self.data, self.subset_data)
        self.vizrank.resetDialog()
        self.update_plot()
        self.send_selection()

    def saveSettings(self):
        OWWidget.saveSettings(self)

    def sendReport(self):
        self.startReport('%s [%s - %s - %s]' % (self.windowTitle(), self.x_attr, self.y_attr, self.z_attr))
        self.reportSettings('Visualized attributes',
                            [('X', self.x_attr),
                             ('Y', self.y_attr),
                             ('Z', self.z_attr),
                             self.color_attr and ('Color', self.color_attr),
                             self.label_attr and ('Label', self.label_attr),
                             self.symbol_attr and ('Symbol', self.symbol_attr),
                             self.size_attr  and ('Size', self.size_attr)])
        self.reportSettings('Settings',
                            [('Symbol size', self.plot.symbol_scale),
                             ('Transparency', self.plot.alpha_value),
                             ('Jittering', self.jitter_size),
                             ('Jitter continuous attributes', OWGUI.YesNo[self.jitter_continuous])
                             ])
        self.reportSection('Plot')
        self.reportImage(self.plot.save_to_file_direct, QSize(400, 400))

    def send_selection(self):
        if self.data == None:
            return

        selected = None#selected = self.plot.get_selected_indices() # TODO: crash
        if selected == None or len(selected) != len(self.data):
            return

        unselected = numpy.logical_not(selected)
        selected = self.data.selectref(list(selected))
        unselected = self.data.selectref(list(unselected))
        self.send('Selected Data', selected)
        self.send('Other Data', unselected)

    def on_axis_change(self):
        if self.data is not None:
            self.update_plot()

    def on_theme_change(self):
        if self.dark_theme:
            self.plot.theme = ScatterDarkTheme()
        else:
            self.plot.theme = ScatterLightTheme()

    def on_checkbox_update(self):
        self.plot.update()

    def update_plot(self):
        if self.data is None:
            return

        self.plot.update_data(self.x_attr, self.y_attr, self.z_attr,
                              self.color_attr, self.symbol_attr, self.size_attr,
                              self.label_attr)

    def showSelectedAttributes(self):
        val = self.vizrank.getSelectedProjection()
        if not val: return
        if self.data.domain.classVar:
            self.attr_color = self.data.domain.classVar.name
        if not self.plot.have_data:
            return
        attr_list = val[3]
        if attr_list and len(attr_list) == 3:
            self.x_attr = attr_list[0]
            self.y_attr = attr_list[1]
            self.z_attr = attr_list[2]

        self.update_plot()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = OWScatterPlot3D()
    data = orange.ExampleTable('../../doc/datasets/iris')
    w.set_data(data)
    w.handleNewSignals()
    w.show()
    app.exec_()
