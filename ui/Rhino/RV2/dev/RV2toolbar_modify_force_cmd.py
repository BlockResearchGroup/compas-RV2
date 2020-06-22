from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rv2.rhino import get_scene

import RV2force_attributes_cmd
import RV2force_modify_vertices_cmd
import RV2force_modify_edges_cmd
import RV2force_move_vertices_cmd

__commandname__ = "RV2toolbar_modify_force"


def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    pattern = scene.get("force")[0]
    if not pattern:
        print("There is no ForceDiagram in the scene.")
        return

    options = ["DiagramAttributes", "VerticesAttributes", "EdgesAttributes", "MoveVertices"]
    option = compas_rhino.rs.GetString("Modify force Diagram:", strings=options)

    if not option:
        return

    elif option == "DiagramAttributes":
        RV2force_attributes_cmd.RunCommand(True)

    elif option == "VerticesAttributes":
        RV2force_modify_vertices_cmd.RunCommand(True)

    elif option == "EdgesAttributes":
        RV2force_modify_edges_cmd.RunCommand(True)

    elif option == "MoveVertices":
        RV2force_move_vertices_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)