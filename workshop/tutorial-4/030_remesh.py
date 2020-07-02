import os
from compas.datastructures import Mesh
from compas_cgal.meshing import remesh
from compas_viewers.objectviewer import ObjectViewer

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'bm_mesh.ply')
FILE_O = os.path.join(HERE, 'bm_remeshed.ply')

mesh = Mesh.from_ply(FILE_I)

lengths = [mesh.edge_length(*edge) for edge in mesh.edges()]
length = sum(lengths) / mesh.number_of_edges()

V, F = remesh(mesh.to_vertices_and_faces(), 0.75 * length)
mesh = Mesh.from_vertices_and_faces(V, F)
mesh.to_ply(FILE_O)

viewer = ObjectViewer()
viewer.add(mesh, settings={'color': '#cccccc'})
viewer.update()
viewer.show()