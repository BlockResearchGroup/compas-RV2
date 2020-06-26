from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rv2.rhino import get_scene
from compas_rv2.rhino import get_proxy


__commandname__ = "RV2pattern_delete"


def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    proxy = get_proxy()
    if not proxy:
        return

    pattern = scene.get("pattern")[0]
    if not pattern:
        print("There is no Pattern in the scene.")
        return

    options = ["Vertices", "Faces"]

    while True:
        option = compas_rhino.rs.GetString("Element type", strings=options)

        if not option:
            break

        if option == "Vertices":
            keys = pattern.select_vertices()
            for key in keys:
                if pattern.datastructure.has_vertex(key):
                    pattern.datastructure.delete_vertex(key)
            scene.update()

        elif option == "Faces":
            raise NotImplementedError

        else:
            raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
