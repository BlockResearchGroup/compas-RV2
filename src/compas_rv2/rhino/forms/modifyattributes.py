from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


import compas
import ast
import compas_rhino
from compas_rhino import delete_objects
from compas.utilities import i_to_rgb
from compas_rv2.rhino import get_scene
from compas_rv2.rhino.forms.settings import Settings_Tab

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    find_object = sc.doc.Objects.Find
    import Eto.Drawing as drawing
    import Eto.Forms as forms
    import Rhino
except Exception:
    compas.raise_if_ironpython()


__all__ = ["ModifyAttributesForm"]


class Tree_Table(forms.TreeGridView):
    def __init__(self, ShowHeader=True, sceneNode=None, table_type=None):
        self.ShowHeader = ShowHeader
        self.Height = 300
        self.last_sorted_to = None
        self.table_type = table_type
        self.sceneNode = sceneNode
        self.to_update = {}
        self._guid_lable = {}
        # self.AllowMultipleSelection=True

        # give colors to each item cells according to object settings
        color = {}
        if sceneNode and table_type:
            settings = sceneNode.settings

            # update general color settings for this table
            general_setting_key = "color.%s" % table_type

            if getattr(sceneNode.datastructure, table_type):
                color.update({str(key): settings.get(general_setting_key) for key in getattr(sceneNode.datastructure, table_type)()})

            # gather and update subsettings
            for full_setting_key in settings:
                sub_setting_str = full_setting_key.split(":")
                if len(sub_setting_str) > 1 and sub_setting_str[0] == general_setting_key:
                    sub_setting_key = sub_setting_str[-1]
                    items_where = getattr(sceneNode.datastructure, '%s_where' % table_type)
                    color.update({str(key): settings.get(full_setting_key) for key in items_where({sub_setting_key: True})})
                    color.update({str(key): settings.get(full_setting_key) for key in items_where({'_'+sub_setting_key: True})})  # including read-only ones

        def OnCellFormatting(sender, e):
            try:
                attr = e.Column.HeaderText

                if not e.Column.Editable and attr != 'key':
                    e.ForegroundColor = drawing.Colors.DarkGray

                if attr == 'key':
                    key = e.Item.Values[0]
                    if key in color:
                        rgb = color[key]
                        rgb = [c/255. for c in rgb]
                        e.BackgroundColor = drawing.Color(*rgb)

            except Exception as exc:
                print('formating error', exc)

        self.CellFormatting += OnCellFormatting

    @property
    def guid_lable(self):
        return self._guid_lable

    @guid_lable.setter
    def guid_lable(self, values):
        self._guid_lable = dict(values)

    @classmethod
    def create_edges_table(cls, sceneNode, edges):

        datastructure = sceneNode.datastructure
        table = cls(sceneNode=sceneNode, table_type='edges')
        table.add_column('Name')
        table.add_column('Value', Editable=True)
        attributes = list(datastructure.default_edge_attributes.keys())
        attributes = table.sort_attributes(attributes)

        treecollection = forms.TreeGridItemCollection()
        edge = edges[0]
        for attr in attributes:
            if attr[0] != '_':
                values = [str(attr), datastructure.edge_attribute(edge, attr)]
                edge_item = forms.TreeGridItem(Values=tuple(values))
                treecollection.Add(edge_item)

        table.DataStore = treecollection
        table.Activated += table.SelectEvent(sceneNode, edges)
        table.ColumnHeaderClick += table.HeaderClickEvent()
        table.CellEdited += table.EditEvent(sceneNode, edges)
        return table

    def sort_attributes(self, attributes):
        sorted_attributes = attributes[:]
        sorted_attributes.sort()

        switch = len(sorted_attributes)
        for i, attr in enumerate(sorted_attributes):
            if attr[0] != '_':
                switch = i
                break
        sorted_attributes = sorted_attributes[switch:] + sorted_attributes[:switch]

        return sorted_attributes

    def SelectEvent(self, sceneNode, edges):
        def on_selected(sender, event):
            attr = event.Item.Values[0]
            self.draw_values(sceneNode, edges, attr)

        return on_selected

    def EditEvent(self, sceneNode, edges):
        def on_edited(sender, event):
            try:
                keys = edges
                attr = event.Item.Values[0]
                value = event.Item.Values[1]

                if self.table_type == 'vertices':
                    get_set_attributes = getattr(self.sceneNode.datastructure, 'vertex_attribute')
                if self.table_type == 'edges':
                    get_set_attributes = getattr(self.sceneNode.datastructure, 'edge_attribute')
                if self.table_type == 'faces':
                    get_set_attributes = getattr(self.sceneNode.datastructure, 'face_attribute')

                try:
                    new_value = ast.literal_eval(str(value))  # checkboxes value type is bool, turn them into str first to be parsed back to bool
                except Exception:
                    new_value = str(value)

                for key in keys:
                # convert key from str to original type: int,tuple...
                    try:
                        key = ast.literal_eval(key)
                    except Exception:
                        pass

                    original_value = get_set_attributes(key, attr)

                    if type(original_value) == float and type(new_value) == int:
                        new_value = float(new_value)
                    if new_value != original_value:
                        if type(new_value) == type(original_value):
                            print('will update key: %s, attr: %s, value: %s' % (key, attr, new_value))
                            self.to_update[(key, attr)] = (get_set_attributes, new_value)
                        else:
                            print('invalid value type, needs: %s, got %s instead' % (type(original_value), type(new_value)))
                            event.Item.Values[event.Column] = original_value
                    else:
                        print('value not changed from', original_value)

                    get_set_attributes(key, attr, new_value)
                self.draw_values(sceneNode, keys, attr)

            except Exception as e:
                print("cell edit failed:", type(e), e)
        return on_edited

    def HeaderClickEvent(self):
        def on_hearderClick(sender, event):
            try:
                # print(event.Column.HeaderText)
                sender.sort(event.Column.HeaderText)
            except Exception as e:
                print(e)
        return on_hearderClick

    def add_column(self, HeaderText=None, Editable=False, checkbox=False):
        column = forms.GridColumn()
        if self.ShowHeader:
            column.HeaderText = HeaderText
        column.Editable = Editable
        if not checkbox:
            column.DataCell = forms.TextBoxCell(self.Columns.Count)
        else:
            column.DataCell = forms.CheckBoxCell(self.Columns.Count)
        column.Sortable = True
        self.Columns.Add(column)

    def sort(self, key):
        headerTexts = [column.HeaderText for column in self.Columns]
        index = headerTexts.index(key)
        print(key, index)

        def getValue(item):
            try:
                value = ast.literal_eval(item.Values[index])
            except (ValueError, TypeError):
                value = item.Values[index]
            return value

        items = sorted(self.DataStore, key=getValue, reverse=True)
        if self.last_sorted_to == key:
            items.reverse()
            self.last_sorted_to = None
        else:
            self.last_sorted_to = key

        self.DataStore = forms.TreeGridItemCollection(items)

    def apply(self):
        for _key in self.to_update:
            get_set_attributes, new_value = self.to_update[_key]
            key, attr = _key
            get_set_attributes(key, attr, new_value)

    def draw_values(self, sceneNode, edges, attr):

        self.clear_label()

        datastructure = sceneNode.datastructure
        is_not_edge = list(datastructure.edges_where({'_is_edge': False}))
        edges_to_draw = list(set(list(datastructure.edges())) - set(is_not_edge))
        edges_selected = list(set(edges) & set(edges_to_draw))
        edges_unselected = list(set(edges_to_draw) - set(edges_selected))  # noqa E501

        labels = []
        for edge in edges_selected:
            color = [0, 0, 0]
            pos = datastructure.edge_midpoint(*edge)
            value = round(datastructure.edge_attribute(edge, attr), 2)
            labels.append({'pos': pos, 'text': str(value), 'color': color})

        guids = compas_rhino.draw_labels(labels, layer='Default', clear=False, redraw=True) # noqa E501
        guid_lable = dict(zip(guids, edges_selected))
        self._guid_lable.update(guid_lable)

        labels = []
        values = [datastructure.edge_attribute(edge, attr) for edge in edges_to_draw]
        v_max = max(values)
        v_min = min(values)
        v_range = v_max - v_min or v_max or 1
        for edge in edges_unselected:
            pos = datastructure.edge_midpoint(*edge)
            value = round(datastructure.edge_attribute(edge, attr), 2)
            color = i_to_rgb(value/v_range)
            labels.append({'pos': pos, 'text': str(value), 'color': color})

        guids = compas_rhino.draw_labels(labels, layer='Default', clear=False, redraw=True) # noqa E501
        guid_lable = dict(zip(guids, edges_unselected))
        self._guid_lable.update(guid_lable)

    def clear_label(self):
        guid = list(self._guid_lable.keys())
        delete_objects(guid, purge=True)
        self._guid_lable = {}


class Tree_Tab(forms.TabPage):

    @classmethod
    def from_sceneNode(cls, sceneNode, tab_type, edges):
        tab = cls()
        tab.Text = tab_type
        create_table = getattr(Tree_Table, "create_%s_table" % tab_type)
        tab.Content = create_table(sceneNode, edges)
        return tab

    def apply(self):
        self.Content.apply()

    def clear_label(self):
        self.Content.clear_label()


class ModifyAttributesForm(forms.Dialog[bool]):

    @classmethod
    def from_sceneNode(cls, sceneNode, edges):
        attributesForm = cls()
        attributesForm.setup(sceneNode, edges)
        Rhino.UI.EtoExtensions.ShowSemiModal(attributesForm, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        return attributesForm

    def setup(self, sceneNode, edges):
        self.Title = "Property - " + sceneNode.name
        self.sceneNode = sceneNode

        control = forms.TabControl()
        control.TabPosition = forms.DockPosition.Top

        tab = Tree_Tab.from_sceneNode(sceneNode, 'edges', edges)
        control.Pages.Add(tab)

        self.TabControl = control

        tab_items = forms.StackLayoutItem(self.TabControl, True)
        layout = forms.StackLayout()
        layout.Spacing = 5
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        layout.Items.Add(tab_items)

        sub_layout = forms.DynamicLayout()
        sub_layout.Spacing = drawing.Size(5, 0)
        sub_layout.AddRow(None, self.ok, self.cancel, self.apply)
        layout.Items.Add(forms.StackLayoutItem(sub_layout))

        self.Content = layout
        self.Padding = drawing.Padding(12)
        self.Resizable = True
        self.ClientSize = drawing.Size(400, 600)
        self.Closing += self.on_close

    @property
    def ok(self):
        self.DefaultButton = forms.Button(Text='OK')
        self.DefaultButton.Click += self.on_ok
        return self.DefaultButton

    @property
    def cancel(self):
        self.AbortButton = forms.Button(Text='Cancel')
        self.AbortButton.Click += self.on_cancel
        return self.AbortButton

    @property
    def apply(self):
        self.ApplyButton = forms.Button(Text='Apply')
        self.ApplyButton.Click += self.on_apply
        return self.ApplyButton

    def on_close(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                page.clear_label()
        except Exception as e:
            print(e)

    def on_ok(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                if hasattr(page, 'apply'):
                    page.apply()
                page.clear_label()
            get_scene().update()
        except Exception as e:
            print(e)
        self.Close()

    def on_apply(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                if hasattr(page, 'apply'):
                    page.apply()
            get_scene().update()
        except Exception as e:
            print(e)

    def on_cancel(self, sender, event):
        try:
            for page in self.TabControl.Pages:
                page.clear_label()
        except Exception as e:
            print(e)
        self.Close()


if __name__ == "__main__":

    scene = get_scene()

    node = scene.get("form")[0]
    ModifyAttributesForm.from_sceneNode(node, edges=None)