from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rv2.rhino import get_scene
from compas.utilities import flatten
from compas_rv2.rhino import rv2_undo


__commandname__ = "RV2thrust_modify_vertices"


@rv2_undo
def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    form = scene.get("form")[0]
    if not form:
        print("There is no FormDiagram in the scene.")
        return

    thrust = scene.get("thrust")[0]
    if not thrust:
        print("There is no ThrustDiagram in the scene.")
        return

    # hide the form vertices
    form_vertices = "{}::vertices".format(form.settings['layer'])
    compas_rhino.rs.HideGroup(form_vertices)

    # show the thrust vertices
    thrust_vertices_free = "{}::vertices_free".format(thrust.settings['layer'])
    thrust_vertices_anchor = "{}::vertices_anchor".format(thrust.settings['layer'])
    compas_rhino.rs.ShowGroup(thrust_vertices_free)
    compas_rhino.rs.ShowGroup(thrust_vertices_anchor)
    compas_rhino.rs.Redraw()

    # selection options
    options = ["Continuous", "Manual"]
    option = compas_rhino.rs.GetString("Selection Type.", strings=options)
    if not option:
        scene.update()
        return

    if option == "Continuous":
        temp = thrust.select_edges()
        keys = list(set(flatten([thrust.datastructure.vertices_on_edge_loop(key) for key in temp])))

    elif option == "Manual":
        keys = thrust.select_vertices()

    if keys:
        public = [name for name in thrust.datastructure.default_vertex_attributes.keys() if not name.startswith('_')]
        defaults = [thrust.datastructure.default_vertex_attributes[name] for name in public]
        if thrust.update_vertices_attributes(keys, names=public):
            for key in keys:
                # update the corresponding form diagram vertices
                for name, default in zip(public, defaults):
                    value = thrust.datastructure.vertex_attribute(key, name)
                    # if value != default:
                    form.datastructure.vertex_attribute(key, name, value)

            thrust.settings['_is.valid'] = False

    # the scene needs to be updated
    # even if the vertices where not modified
    # to reset group visibility to the configuration of settings
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
