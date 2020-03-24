from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rv2.rhino import get_scene


__commandname__ = "RV2form_modify_vertices"


HERE = compas_rhino.get_document_dirname()


def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    form = scene.get("form")[0]
    if not form:
        return

    options = ['Manual', 'All', 'Openings', 'Holes', 'Continuous', 'Fixed', 'Anchors']
    option = compas_rhino.rs.GetString("Select Faces.", options[0], options)

    if option == 'All':
        keys = list(form.datastructure.vertices())

    elif option == 'Openings':
        # select the vertices around an opening
        # draw dots in openings
        # allow user to select dots
        raise NotImplementedError

    elif option == 'Holes':
        # select the vertices around a hole
        # draw dots in holes
        # allow user to select dots
        raise NotImplementedError

    elif option == 'Continuous':
        temp = form.select_edges()
        keys = list(set(flatten([form.datastructure.continuous_vertices(key) for key in temp])))

    elif option == 'Fixed':
        keys = list(form.datastructure.vertices_where({'is_fixed': True}))

    elif option == 'Anchors':
        keys = list(form.datastructure.vertices_where({'is_anchor': True}))

    else:
        keys = form.select_vertices()

    public = [name for name in form.datastructure.default_vertex_attributes.keys() if not name.startswith('_')]
    if form.update_vertices_attributes(keys, names=public):
        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)