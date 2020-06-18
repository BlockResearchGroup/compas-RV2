from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh
from compas.datastructures import mesh_smooth_area
from compas_rv2.datastructures.meshmixin import MeshMixin

from compas_singular.algorithms import surface_discrete_mapping
from compas_singular.algorithms import boundary_triangulation
from compas_singular.algorithms import SkeletonDecomposition
from compas_singular.rhino.objects.surface import RhinoSurface


__all__ = ['Pattern']


class Pattern(MeshMixin, Mesh):
    """Customised mesh data structure for RV2.

    Examples
    --------
    A :class:`Pattern` is used to define the geometry and boundary conditions of
    a funicular network in RV2.
    Patterns can be constructed from various inputs.

    >>> pattern = Pattern.from_lines()
    >>> pattern = Pattern.from_mesh()
    >>> pattern = Pattern.from_surface()
    >>> pattern = Pattern.from_skeleton()
    >>> pattern = Pattern.from_features()

    A pattern is essentially a mesh data structure, and therefore supports all operations
    available for meshes. For example,

    """

    def __init__(self, *args, **kwargs):
        super(Pattern, self).__init__(*args, **kwargs)
        self.attributes.update({
            'openings': {}
        })
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'is_fixed': False,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            'lmin': 1e-6,
            'lmax': 1e6
        })

    @classmethod
    def from_surface_and_features(cls, input_subdivision_spacing, mesh_edge_length, srf_guid, crv_guids=[], pt_guids=[]):
        """Get a pattern object from a NURBS surface with optional point and curve features on the surface. 
        The pattern is aligned to the surface boundaries and curve features.
        The pattern contains a pole singularity at the feature points. Pole singularities are a specific type of singularity.

        Parameters
        ----------
        input_subdivision_spacing : float
            The surface boundary and curve feature subdivision spacing. Values between 1% and 5% of the length of the diagonal of the bounding box are recommended.
        mesh_edge_length : float
            The edge target length for densification.
        srf_guid : Rhino surface guid
            A Rhino surface guid.
        crv_guids : list, []
            Optional. A list of Rhino curve guids.
        pt_guids : list, []
            Optional. A list of Rhino point guids. WIP
        
        Returns
        -------
        Pattern
            A Pattern object.

        References
        ----------
        Based on [1]_ and [2]_.

        .. [1] Oval et al. *Feature-based topology finding of patterns for shell structures*. Automation in Construction, 2019.
               Available at: https://www.researchgate.net/publication/331064073_Feature-based_Topology_Finding_of_Patterns_for_Shell_Structures.
        .. [2] Oval. *Topology finding of patterns for structural design*. PhD thesis, Unversité Paris-Est, 2019.
               Available at: https://www.researchgate.net/publication/340096530_Topology_Finding_of_Patterns_for_Structural_Design.

        """        

        outer_boundary, inner_boundaries, polyline_features, point_features = surface_discrete_mapping(srf_guid, discretisation, crv_guids = crv_guids, pt_guids = pt_guids)
        tri_mesh = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features, src='numpy')
        decomposition = SkeletonDecomposition.from_mesh(tri_mesh)
        coarse_mesh = decomposition.decomposition_mesh(point_features)
        RhinoSurface.from_guid(srf_guid).mesh_uv_to_xyz(coarse_mesh)

        coarse_mesh.collect_strips()
        coarse_mesh.set_strips_density_target(target_length)
        coarse_mesh.densification()

        dense_mesh = coarse_mesh.get_quad_mesh()
        vertices, faces = dense_mesh.to_vertices_and_faces()
        return cls.from_vertices_and_faces(vertices.values(), faces.values())

    def collapse_small_edges(self, tol=1e-2):
        for key in list(self.edges()):
            if self.has_edge(key):
                u, v = key
                l = self.edge_length(u, v)
                if l < tol:
                    mesh_collapse_edge(self, u, v, t=0.5, allow_boundary=True)

    def smooth(self, fixed, kmax=10):
        mesh_smooth_area(self, fixed=fixed, kmax=kmax)

    def relax(self):
        from compas.numerical import fd_numpy
        key_index = self.key_index()
        xyz = self.vertices_attributes('xyz')
        loads = [[0.0, 0.0, 0.0] for _ in xyz]
        fixed = [key_index[key] for key in self.vertices_where({'is_fixed': True})]
        edges = [(key_index[u], key_index[v]) for u, v in self.edges()]
        q = self.edges_attribute('q')
        xyz, q, f, l, r = fd_numpy(xyz, edges, fixed, q, loads)
        for key in self.vertices():
            index = key_index[key]
            self.vertex_attributes(key, 'xyz', xyz[index])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    import json
    from compas_plotters.meshplotter import MeshPlotter
    filepath = '../../../data/pattern_from_features.json'
    with open(filepath, 'r') as fp:
        data = json.load(fp)
    outer_boundary, inner_boundaries, polyline_features, point_features = data
    pattern = Pattern.from_surface_and_features(.25, outer_boundary, inner_boundaries, polyline_features, point_features)
    plotter = MeshPlotter(pattern, figsize=(5, 5))
    plotter.draw_edges(width=.1)
    plotter.draw_faces()
    plotter.show()
