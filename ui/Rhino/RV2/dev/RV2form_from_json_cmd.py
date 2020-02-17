from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rv2.diagrams import FormDiagram
from compas_rv2.rhino import RhinoFormDiagram
from compas_rv2.rhino import RhinoThrustDiagram
from compas_rv2.rhino import select_filepath_open
from compas_rv2.rhino import get_rv2

__commandname__ = "RV2form_from_json"


HERE = compas_rhino.get_document_dirname()


def RunCommand(is_interactive):
    RV2 = get_rv2()
    if not RV2:
        return

    session = RV2["session"]
    settings = RV2["settings"]
    scene = RV2["scene"]

    root = session["cwd"] or HERE

    filepath = select_filepath_open(root, 'json')
    if not filepath:
        return

    form = FormDiagram.from_json(filepath)

    # scene.clear()
    # scene.add(form)
    # scene.add(thrust)
    # scene.update()

    # maybe the RV2 scene can be specialised for RV2

    # add form to data
    # store guids in scene nodes

    # adding data to a scene creates
    # node.artist
    # node.data
    # node.objects
    # => objects are created with artist based on data

    rhinoform = RhinoFormDiagram(form)
    rhinothrust = RhinoThrustDiagram(form)

    rhinoform.draw(settings)

    scene["form"] = rhinoform
    scene["force"] = None
    scene["thrust"] = rhinothrust


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)