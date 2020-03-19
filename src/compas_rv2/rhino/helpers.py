from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
from ast import literal_eval
import compas_rhino
from compas_rhino.etoforms import TextForm


__all__ = [
    "is_valid_file",
    "select_filepath_open",
    "select_filepath_save",
    "get_rv2",
    "get_scene",
    "get_proxy",
    "get_system",
    "select_vertices",
    "select_edges",
    "select_faces",
    "select_boundary_vertices",
    "select_continuous_vertices",
    "select_boundary_edges",
    "select_continuous_edges",
    "select_parallel_edges",
    "select_boundary_faces",
    "select_parallel_faces",
]


def match_vertices(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.vertex.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def match_edges(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')[2].split('-')
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def match_faces(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.face.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def select_vertices(diagram, keys):
    guids = match_vertices(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def select_edges(diagram, keys):
    guids = match_edges(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def select_faces(diagram, keys):
    guids = match_faces(diagram, keys)
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.SelectObjects(guids)
    compas_rhino.rs.EnableRedraw(True)


def select_boundary_vertices(rhinodiagram):
    vertices = rhinodiagram.diagram.vertices_on_boundary()
    select_vertices(rhinodiagram.diagram, vertices)


def select_boundary_edges(rhinodiagram):
    edges = rhinodiagram.diagram.edges_on_boundary()
    select_edges(rhinodiagram.diagram, edges)


def select_boundary_faces(rhinodiagram):
    faces = rhinodiagram.diagram.faces_on_boundary()
    select_faces(rhinodiagram.diagram, faces)


def select_continuous_edges(rhinodiagram):
    selected = rhinodiagram.select_edges()
    edges = []
    for edge in selected:
        continuous = rhinodiagram.diagram.continuous_edges(edge)
        edges.extend(continuous)
    select_edges(rhinodiagram.diagram, edges)


def select_continuous_vertices(rhinodiagram):
    edges = rhinodiagram.select_edges()
    vertices = []
    for edge in edges:
        continuous = rhinodiagram.diagram.continuous_vertices(edge)
        vertices.extend(continuous)
    select_vertices(rhinodiagram.diagram, vertices)


def select_parallel_edges(rhinodiagram):
    selected = rhinodiagram.select_edges()
    edges = []
    for edge in selected:
        parallel = rhinodiagram.diagram.parallel_edges(edge)
        edges.extend(parallel)
    select_edges(rhinodiagram.diagram, edges)


def select_parallel_faces(rhinodiagram):
    selected = rhinodiagram.select_edges()
    faces = []
    for edge in selected:
        parallel = rhinodiagram.diagram.parallel_faces(edge)
        faces.extend(parallel)
    select_faces(rhinodiagram.diagram, faces)


def is_valid_file(filepath, ext):
    """Is the selected path a valid file.

    Parameters
    ----------
    filepath
    """
    if not filepath:
        return False
    if not os.path.exists(filepath):
        return False
    if not os.path.isfile(filepath):
        return False
    if not filepath.endswith(".{}".format(ext)):
        return False
    return True


def select_filepath_open(root, ext):
    """Select a filepath for opening a session.

    Parameters
    ----------
    root : str
        Base directory from where the file selection is started.
        If no directory is provided, the parent folder of the current
        Rhino document will be used
    ext : str
        The type of file that can be openend.

    Returns
    -------
    tuple
        The parent directory.
        The file name.
    None
        If the procedure fails.

    Notes
    -----
    The file extension is only used to identify the type of session file.
    Regardless of the provided extension, the file contents should be in JSON format.

    """
    ext = ext.split('.')[-1]

    filepath = compas_rhino.select_file(folder=root, filter=ext)

    if not is_valid_file(filepath, ext):
        print("This is not a valid session file: {}".format(filepath))
        return

    return filepath


def select_filepath_save(root, ext):
    """Select a filepath for saving a session."""
    if not root:
        root = HERE

    dirname = compas_rhino.select_folder(default=root)
    filename = compas_rhino.rs.GetString('File name (w/o extension!)')

    if not filename:
        return

    basename = "{}.{}".format(filename, ext)
    filepath = os.path.join(dirname, basename)

    return filepath


def get_rv2():
    if "RV2" not in compas_rhino.sc.sticky:
        form = TextForm('Initialise the plugin first!', 'RV2')
        form.show()
        return None
    return compas_rhino.sc.sticky["RV2"]


def get_scene():
    rv2 = get_rv2()
    return rv2['scene']


def get_proxy():
    if "RV2.proxy" not in compas_rhino.sc.sticky:
        form = TextForm('Initialise the plugin first!', 'RV2')
        form.show()
        return None
    return compas_rhino.sc.sticky["RV2.proxy"]


def get_system():
    if "RV2.system" not in compas_rhino.sc.sticky:
        form = TextForm('Initialise the plugin first!', 'RV2')
        form.show()
        return None
    return compas_rhino.sc.sticky["RV2.system"]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
