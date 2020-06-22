from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rv2.rhino import get_scene

import RV2boundary_supports_cmd
import RV2boundary_openings_cmd
import RV2boundary_boundaries_cmd
import RV2boundary_loads_cmd


__commandname__ = "RV2toolbar_boundary"


def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    pattern = scene.get("pattern")[0]
    if not pattern:
        print("There is no Pattern in the scene.")
        return

    options = ["IdentifySupports", "AddOpenings", "UpdateBoundaries", "DefineLoads"]

    while True:

        option = compas_rhino.rs.GetString("Define boundary conditions:", strings=options)

        if not option:
            return

        elif option == "IdentifySupports":
            RV2boundary_supports_cmd.RunCommand(True)

        elif option == "AddOpenings":
            RV2boundary_openings_cmd.RunCommand(True)

        elif option == "UpdateBoundaries":
            RV2boundary_boundaries_cmd.RunCommand(True)

        elif option == "DefineLoads":
            RV2boundary_loads_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
