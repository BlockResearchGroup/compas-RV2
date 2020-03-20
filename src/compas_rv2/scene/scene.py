from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_rhino
import uuid

from compas_rv2.rhino import SettingsForm


__all__ = ['Scene']


_ITEM_WRAPPER = {}


# eventually, this should inherit from the base scene object in COMPAS
class Scene(object):

    def __init__(self, settings={}):
        self.nodes = {}
        self.settings = settings

    def add(self, item, **kwargs):
        node = Scene.build(self, item, **kwargs)
        _id = uuid.uuid4()
        self.nodes[_id] = node
        return node

    def get(self, name):
        selected = []
        for _id in self.nodes:
            if name == self.nodes[_id].name:
                selected.append(self.nodes[_id])
        if len(selected) == 0:
            return None
        else:
            return selected

    def update(self):
        compas_rhino.rs.EnableRedraw(False)
        for key in self.nodes:
            node = self.nodes[key]
            if node.visible:
                node.draw(self.settings)
        compas_rhino.rs.EnableRedraw(True)

    # this should be related to clearing objects by GUID
    # layer clearing should be deferred to the objects/artists
    def clear(self):
        layers = [self.settings[name] for name in self.settings if name.startswith("layers")]
        compas_rhino.clear_layers(layers)
        # TODO: maybe clear and dispose each nodes first
        self.nodes = {}

    def update_settings(self, settings=None):
        # return compas_rhino.update_settings(settings or self.settings)
        SettingsForm.from_settings(scene.settings)

    # register object_type AND artist_type (or register artist_type with object_type)
    @staticmethod
    def register(item_type, wrapper_type):
        _ITEM_WRAPPER[item_type] = wrapper_type

    @staticmethod
    def build(scene, item, **kwargs):
        wrapper = _ITEM_WRAPPER[type(item)]
        return wrapper(scene, item, **kwargs)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas.geometry import Point
    from compas.geometry import Line
    from compas.geometry import Frame

    from compas.datastructures import Mesh

    scene = Scene()

    a = Point(1.0, 1.0, 0.0)
    b = Point(5.0, 5.0, 0.0)
    ab = Line(a, b)
    world = Frame.worldXY()

    mesh = Mesh.from_polyhedron(6)

    scene.add(a, name="A", color=(0, 0, 0), layer="A")
    scene.add(b, name="B", color=(255, 255, 255), layer="B")
    scene.add(ab, name="AB", color=(128, 128, 128), layer="AB")
    scene.add(world, name="World", layer="World")
    scene.add(mesh, name="Cube", layer="Cube")

    scene.update()
