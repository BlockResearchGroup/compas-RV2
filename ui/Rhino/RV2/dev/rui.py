import os
import json
import inspect

import uuid
from xml.etree import ElementTree as ET
from xml.dom import minidom

TPL_RUI = """<?xml version="1.0" encoding="utf-8"?>
<RhinoUI major_ver="2"
         minor_ver="0"
         guid="{0}"
         localize="False"
         default_language_id="1033">
    <extend_rhino_menus>
        <menu guid="{1}">
          <text>
            <locale_1033>Extend Rhino Menus</locale_1033>
          </text>
        </menu>
    </extend_rhino_menus>
    <menus />
    <tool_bar_groups />
    <tool_bars />
    <macros />
    <bitmaps>
        <small_bitmap item_width="16" item_height="16">
          <bitmap>iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6Q
AAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAATSURBVDhPYxgFo2AUjAIwYGAAAA
QQAAGnRHxjAAAAAElFTkSuQmCCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </small_bitmap>
        <normal_bitmap item_width="24" item_height="24">
          <bitmap>iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6Q
AAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYSURBVEhL7cEBAQAAAIIg/6+uIU
AAAFwNCRgAAdACW14AAAAASUVORK5CYIIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </normal_bitmap>
        <large_bitmap item_width="32" item_height="32">
          <bitmap>iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6Q
AAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAaSURBVFhH7cEBAQAAAIIg/69uSE
AAAADAuRoQIAABnXhJQwAAAABJRU5ErkJgggAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </large_bitmap>
    </bitmaps>
    <scripts />
</RhinoUI>
"""

TPL_MACRO = """
<macro_item guid="{0}">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
    <script>{2}</script>
    <tooltip>
        <locale_1033>{3}</locale_1033>
    </tooltip>
    <help_text>
        <locale_1033>{4}</locale_1033>
    </help_text>
    <button_text>
        <locale_1033>{5}</locale_1033>
    </button_text>
    <menu_text>
        <locale_1033>{6}</locale_1033>
    </menu_text>
</macro_item>
"""

TPL_MENUITEM = """
<menu_item guid="{0}" item_type="normal">
    <macro_id>{1}</macro_id>
</menu_item>
"""

TPL_MENUSEPARATOR = """
<menu_item guid="{0}" item_type="separator"></menu_item>
"""

TPL_TOOLBARITEM = """
<tool_bar_item guid="{0}" button_display_mode="control_only" button_style="normal">
    <left_macro_id>{1}</left_macro_id>
    <right_macro_id>{2}</right_macro_id>
</tool_bar_item>
"""

TPL_TOOLBARSEPARATOR = """
<tool_bar_item guid="{0}" button_display_mode="control_only" button_style="spacer">
</tool_bar_item>
"""

TPL_TOOLBAR = """
<tool_bar guid="{0}" item_display_style="{2[item_display_style]}">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
</tool_bar>
"""

TPL_TOOLBARGROUP = """
<tool_bar_group guid="{0}"
                dock_bar_guid32=""
                dock_bar_guid64=""
                active_tool_bar_group=""
                single_file="{2[single_file]}"
                hide_single_tab="{2[hide_single_tab]}"
                point_floating="0,0">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
</tool_bar_group>
"""

TPL_TOOLBARGROUPITEM = """
<tool_bar_group_item guid="{0}" major_version="1" minor_version="1">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
    <tool_bar_id>{2}</tool_bar_id>
</tool_bar_group_item>
"""


class Rui(object):
    """Class for generating *.rui files.

    Parameters
    ----------
    filepath : str
        Path to the *.rui file.

    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.macros = {}
        self.toolbars = {}
        self.xml = None
        self.root = None
        self.root_macros = []
        self.root_menus = []
        self.root_toolbargroups = []
        self.root_toolbars = []
        self.check()

    def check(self):
        if not os.path.exists(os.path.dirname(self.filepath)):
            try:
                os.makedirs(os.path.dirname(self.filepath))
            except OSError as e:
                if e.errno != os.errno.EEXIST:
                    raise e
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w+"):
                pass

    def init(self):
        with open(self.filepath, "w+") as f:
            f.write(TPL_RUI.format(uuid.uuid4(), uuid.uuid4()))
        self.xml = ET.parse(self.filepath)
        self.root = self.xml.getroot()
        self.root_macros = self.root.find("macros")
        self.root_menus = self.root.find("menus")
        self.root_toolbargroups = self.root.find("tool_bar_groups")
        self.root_toolbars = self.root.find("tool_bars")

    def parse(self):
        raise NotImplementedError

    def write(self):
        root = ET.tostring(self.root)
        xml = minidom.parseString(root).toprettyxml(indent="  ")
        xml = "\n".join([line for line in xml.split("\n") if line.strip()])
        with open(self.filepath, "w+") as fh:
            fh.write(xml)

    # --------------------------------------------------------------------------
    # add macros
    # --------------------------------------------------------------------------

    def add_macros(self, macros):
        for macro in macros:
            guid = str(uuid.uuid4())
            name = macro["name"]
            script = macro["script"]
            tooltip = macro.get("tooltip", "")
            help_text = macro.get("help_text", "")
            button_text = macro.get("button_text", name)
            menu_text = macro.get("menu_text", name.replace("_", " "))
            self.add_macro(name, guid, script, tooltip, help_text, button_text, menu_text)

    def add_macro(self, name, guid, script, tooltip, help_text, button_text, menu_text):
        s_macro = TPL_MACRO.format(guid, name, script, tooltip, help_text, button_text, menu_text)
        e_macro = ET.fromstring(s_macro)
        self.root_macros.append(e_macro)
        self.macros[name] = e_macro

    # --------------------------------------------------------------------------
    # add menus
    # --------------------------------------------------------------------------

    def add_menus(self, menus):
        for menu in menus:
            self.add_menu(menu)

    def add_menu(self, menu, root=None):
        if root is None:
            root = self.root_menus
        e_menu = ET.SubElement(root, "menu")
        e_menu.set("guid", str(uuid.uuid4()))
        e_text = ET.SubElement(e_menu, "text")
        e_locale = ET.SubElement(e_text, "locale_1033")
        e_locale.text = menu["name"]
        for item in menu["items"]:
            if item["type"] == "normal":
                e_macro = self.macros[item["macro"]]
                macro_guid = e_macro.attrib["guid"]
                self.add_menuitem(e_menu, macro_guid)
                continue
            if item["type"] == "separator":
                self.add_menuseparator(e_menu)
                continue
            if item["type"] == "submenu":
                self.add_menu(item, root=e_menu)
                continue

    def add_menuitem(self, root, macro_id):
        guid = uuid.uuid4()
        s_item = TPL_MENUITEM.format(guid, macro_id)
        e_item = ET.fromstring(s_item)
        root.append(e_item)

    def add_menuseparator(self, root):
        guid = uuid.uuid4()
        s_sep = TPL_MENUSEPARATOR.format(guid)
        e_sep = ET.fromstring(s_sep)
        root.append(e_sep)

    # --------------------------------------------------------------------------
    # add toolbars
    # --------------------------------------------------------------------------

    def add_toolbars(self, toolbars):
        for toolbar in toolbars:
            self.add_toolbar(toolbar)

    def add_toolbar(self, toolbar):
        options = {
            "item_display_style": "text_only"
        }
        guid = uuid.uuid4()
        s_tb = TPL_TOOLBAR.format(guid, toolbar["name"], options)
        e_tb = ET.fromstring(s_tb)
        self.root_toolbars.append(e_tb)
        self.toolbars[toolbar["name"]] = e_tb
        for item in toolbar["items"]:
            if item.get("type", "normal") == "normal":
                left_guid = None
                left_macro = item.get("left_macro", item.get("left"))
                if left_macro:
                    e_left = self.macros[left_macro]
                    left_guid = e_left.attrib["guid"]
                right_guid = None
                right_macro = item.get("right_macro", item.get("right"))
                if right_macro:
                    e_right = self.macros[right_macro]
                    right_guid = e_right.attrib["guid"]
                self.add_toolbaritem(e_tb, left_guid, right_guid)
                continue
            if item["type"] == "separator":
                self.add_toolbarseparator(e_tb)
                continue

    def add_toolbaritem(self, root, left_macro_id, right_macro_id):
        guid = uuid.uuid4()
        s_item = TPL_TOOLBARITEM.format(guid, left_macro_id, right_macro_id)
        e_item = ET.fromstring(s_item)
        root.append(e_item)

    def add_toolbarseparator(self, root):
        guid = uuid.uuid4()
        s_sep = TPL_TOOLBARSEPARATOR.format(guid)
        e_sep = ET.fromstring(s_sep)
        root.append(e_sep)

    # --------------------------------------------------------------------------
    # add toolbargroups
    # --------------------------------------------------------------------------

    def add_toolbargroups(self, toolbargroups):
        for tbg in toolbargroups:
            self.add_toolbargroup(tbg)

    def add_toolbargroup(self, tbg):
        options = {
            "single_file": "False",
            "hide_single_tab": "False",
        }
        guid = uuid.uuid4()
        s_tbg = TPL_TOOLBARGROUP.format(guid, tbg["name"], options)
        e_tbg = ET.fromstring(s_tbg)
        self.root_toolbargroups.append(e_tbg)
        for tb_name in tbg["toolbars"]:
            e_tb = self.toolbars[tb_name]
            tb_guid = e_tb.attrib["guid"]
            self.add_toolbargroupitem(e_tbg, tb_name, tb_guid)

    def add_toolbargroupitem(self, root, tb_name, tb_guid):
        guid = uuid.uuid4()
        s_item = TPL_TOOLBARGROUPITEM.format(guid, tb_name, tb_guid)
        e_item = ET.fromstring(s_item)
        root.append(e_item)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    HERE = os.path.dirname(__file__)
    FILE = os.path.join(HERE, "config.json")

    with open(FILE, "r") as f:
        config = json.load(f)

    macros = []
    for name in config["rui"]["macros"]:
        macros.append({
            "name": name,
            "script": "-_{}".format(name),
            "tooltip": "",
            "help_text": "",
            "button_text": name,
            "menu_text": name
        })

    rui = Rui(os.path.join(HERE, "RV2.rui"))

    rui.init()
    rui.add_macros(macros)
    rui.add_menus(config["rui"]["menus"])
    rui.add_toolbars(config["rui"]["toolbars"])
    rui.add_toolbargroups(config["rui"]["toolbargroups"])
    rui.write()
