from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rv2.rhino import get_scene


__commandname__ = "RV2pattern_modify_edges"


HERE = compas_rhino.get_document_dirname()


def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    pattern = scene.get("pattern")[0]
    if not pattern:
        return

    options = ['Manual', 'All', 'Openings', 'Holes', 'Continuous', 'Parallel']
    option = compas_rhino.rs.GetString("Select Edges", options[0], options)

    if option == 'All':
        keys = list(pattern.datastructure.edges())

    elif option == 'Openings':
        # draw a dot for every opening
        # allow user to select dots
        # find edges related to opening
        # pass on the keys
        raise NotImplementedError

    elif option == 'Holes':
        # draw a dot for every opening
        # allow user to select dots
        # find edges related to hole
        # pass on the keys
        raise NotImplementedError

    elif option == 'Continuous':
        temp = pattern.select_edges()
        keys = list(set(flatten([pattern.datastructure.continuous_edges(key) for key in temp])))

    elif option == 'Parallel':
        temp = pattern.select_edges()
        keys = list(set(flatten([pattern.datastructure.parallel_edges(key) for key in temp])))

    else:
        keys = pattern.select_edges()

    # is this necessary with the special update dialogs?
    public = [name for name in pattern.datastructure.default_edge_attributes.keys() if not name.startswith('_')]
    if pattern.update_edges_attributes(keys, names=public):
        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)