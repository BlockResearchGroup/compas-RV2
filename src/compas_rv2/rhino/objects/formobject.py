from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import i_to_rgb
from compas.geometry import Point
from compas.geometry import Scale
from compas.geometry import Translation
from compas.geometry import Rotation

import compas_rhino

from .meshobject import MeshObject


__all__ = ["FormObject"]


class FormObject(MeshObject):
    """Scene object for RV2 form diagrams.
    """

    SETTINGS = {
        'layer': "RV2::FormDiagram",
        'show.vertices': True,
        'show.edges': True,
        'color.vertices': [0, 255, 0],
        'color.vertices:is_fixed': [0, 0, 255],
        'color.vertices:is_anchor': [255, 0, 0],
        'color.edges': [0, 127, 0],
    }

    @property
    def vertex_xyz(self):
        """dict : The view coordinates of the mesh object."""
        origin = Point(0, 0, 0)
        if self.anchor is not None:
            xyz = self.mesh.vertex_attributes(self.anchor, 'xyz')
            point = Point(* xyz)
            T1 = Translation.from_vector(origin - point)
            S = Scale.from_factors([self.scale] * 3)
            R = Rotation.from_euler_angles(self.rotation)
            T2 = Translation.from_vector(self.location)
            X = T2 * R * S * T1
        else:
            S = Scale.from_factors([self.scale] * 3)
            R = Rotation.from_euler_angles(self.rotation)
            T = Translation.from_vector(self.location)
            X = T * R * S
        mesh = self.mesh.transformed(X)
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, 'xy') + [0.0] for vertex in mesh.vertices()}
        return vertex_xyz

    def draw(self):
        """Draw the objects representing the force diagram.
        """
        layer = self.settings['layer']
        self.artist.layer = layer
        self.artist.clear_layer()
        # self.clear()
        # if not self.visible:
        #     return
        self.artist.vertex_xyz = self.vertex_xyz

        # ======================================================================
        # Groups
        # ------
        # Create groups for vertices and edges.
        # These groups will be turned on/off based on the visibility settings of the diagram
        # ======================================================================

        group_vertices = "{}::vertices".format(layer)
        group_edges = "{}::edges".format(layer)

        if not compas_rhino.rs.IsGroup(group_vertices):
            compas_rhino.rs.AddGroup(group_vertices)

        if not compas_rhino.rs.IsGroup(group_edges):
            compas_rhino.rs.AddGroup(group_edges)

        # ======================================================================
        # Vertices
        # --------
        # Draw the vertices and add them to the vertex group.
        # ======================================================================

        guids = list(self.guid_vertex)
        compas_rhino.delete_objects(guids, purge=True)

        vertices = list(self.mesh.vertices())
        color = {vertex: self.settings['color.vertices'] for vertex in vertices}
        color_fixed = self.settings['color.vertices:is_fixed']
        color_anchor = self.settings['color.vertices:is_anchor']
        color.update({vertex: color_fixed for vertex in self.mesh.vertices_where({'is_fixed': True}) if vertex in vertices})
        color.update({vertex: color_anchor for vertex in self.mesh.vertices_where({'is_anchor': True}) if vertex in vertices})

        guids = self.artist.draw_vertices(vertices, color)
        self.guid_vertex = zip(guids, vertices)
        compas_rhino.rs.AddObjectsToGroup(guids, group_vertices)

        if self.settings['show.vertices']:
            compas_rhino.rs.ShowGroup(group_vertices)
        else:
            compas_rhino.rs.HideGroup(group_vertices)

        # ======================================================================
        # Edges
        # --------
        # Draw the edges and add them to the edge group.
        # ======================================================================

        guids = list(self.guid_edge)
        compas_rhino.delete_objects(guids, purge=True)

        edges = list(self.mesh.edges_where({'_is_edge': True}))
        color = {edge: self.settings['color.edges'] for edge in edges}

        # color analysis
        if self.scene.settings['RV2']['show.forces']:
            if self.mesh.dual:
                _edges = list(self.mesh.dual.edges())
                lengths = [self.mesh.dual.edge_length(*edge) for edge in _edges]
                edges = [self.mesh.dual.primal_edge(edge) for edge in _edges]
                lmin = min(lengths)
                lmax = max(lengths)
                for edge, length in zip(edges, lengths):
                    if lmin != lmax:
                        color[edge] = i_to_rgb((length - lmin) / (lmax - lmin))

        guids = self.artist.draw_edges(edges, color)
        self.guid_edge = zip(guids, edges)
        compas_rhino.rs.AddObjectsToGroup(guids, group_edges)

        if self.settings['show.edges']:
            compas_rhino.rs.ShowGroup(group_edges)
        else:
            compas_rhino.rs.HideGroup(group_edges)

        # ======================================================================
        # Labels
        # ------
        # Add labels for the angle deviations.
        # ======================================================================

        guids = list(self.guid_edgelabel)
        compas_rhino.delete_objects(guids, purge=True)

        if self.scene.settings['RV2']['show.angles']:
            tol = self.scene.settings['RV2']['tol.angles']
            edges = list(self.mesh.edges_where({'_is_edge': True}))
            angles = self.mesh.edges_attribute('_a', keys=edges)
            amin = min(angles)
            amax = max(angles)
            if (amax - amin)**2 > 0.001**2:
                text = {}
                color = {}
                for edge, angle in zip(edges, angles):
                    if angle > tol:
                        text[edge] = "{:.0f}".format(angle)
                        color[edge] = i_to_rgb((angle - amin) / (amax - amin))
                guids = self.artist.draw_edgelabels(text, color)
                self.guid_edgelabel = zip(guids, edges)

        # self.redraw()
