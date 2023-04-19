"""
Created: April, 2023

@author: tsalemink
"""
import os
import re

from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field, FieldImage

from cmlibs.utils.zinc.finiteelement import create_cube_element


# TODO: Also, should the material and glyph methods go in the scene...?
class AutoSegmentationModel(object):
    def __init__(self, input_image_data):
        self._context = Context('Auto-Segmentation')

        self._root_region = self._context.getDefaultRegion()
        self._point_cloud_region = self._root_region.createChild('output')
        self._root_scene = self._root_region.getScene()
        self._output_scene = self._point_cloud_region.getScene()
        self._field_module = self._root_region.getFieldmodule()

        self._input_image_data = input_image_data
        self._output_filename = None

        self._image_field = self._initialise_image_field()
        self._dimensions_px = self._image_field.getSizeInPixels(3)[1]
        self._scalar_field = self._create_finite_elements()

        self._output_coordinates, self._node_set = self._setup_output_region()

        self._define_standard_glyphs()
        self._point_cloud_material = None
        self._contour_material = None
        self._define_materials()

    def get_context(self):
        return self._context

    def get_root_region(self):
        return self._root_region

    def get_point_cloud_region(self):
        return self._point_cloud_region

    def get_field_module(self):
        return self._field_module

    def get_root_scene(self):
        return self._root_scene

    def get_output_scene(self):
        return self._output_scene

    def get_image_field(self):
        return self._image_field

    def get_scalar_field(self):
        return self._scalar_field

    def get_dimensions(self):
        return self._dimensions_px

    def get_output_coordinates(self):
        return self._output_coordinates

    def get_node_set(self):
        return self._node_set

    def get_point_cloud_material(self):
        return self._point_cloud_material

    def get_contour_material(self):
        return self._contour_material

    def _define_standard_glyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def _define_materials(self):
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()
        self._point_cloud_material = material_module.findMaterialByName("yellow")
        self._contour_material = material_module.findMaterialByName("white")

    def _create_finite_elements(self):
        self._field_module.beginChange()

        finite_element_field = self._field_module.createFieldFiniteElement(3)
        finite_element_field.setName('coordinates')
        finite_element_field.setManaged(True)
        finite_element_field.setTypeCoordinate(True)

        a, b, c = self._dimensions_px
        node_coordinate_set = [[0, 0, 0], [a, 0, 0], [0, b, 0], [a, b, 0], [0, 0, c], [a, 0, c], [0, b, c], [a, b, c]]
        mesh = self._field_module.findMeshByDimension(3)
        create_cube_element(mesh, finite_element_field, node_coordinate_set)
        scalar_field = self._field_module.createFieldComponent(finite_element_field, 3)

        self._field_module.defineAllFaces()
        self._field_module.endChange()

        return scalar_field

    def _initialise_image_field(self):
        image_field = self._field_module.createFieldImage()
        image_field.setFilterMode(FieldImage.FILTER_MODE_LINEAR)
        image_field.setWrapMode(FieldImage.WRAP_MODE_CLAMP)

        stream_information = image_field.createStreaminformationImage()
        directory = self._input_image_data.location()
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            if filename not in ['.hg', 'annotation.rdf']:
                string_name = str(os.path.join(directory, filename))
                stream_information.createStreamresourceFile(string_name)
        image_field.read(stream_information)

        return image_field

    def _setup_output_region(self):
        field_module = self._point_cloud_region.getFieldmodule()

        output_coordinates = field_module.createFieldFiniteElement(3)
        output_coordinates.setName('coordinates')
        output_coordinates.setManaged(True)

        node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)

        return output_coordinates, node_set

    def generate_points(self):
        self._node_set.destroyAllNodes()
        graphics_filter = self._context.getScenefiltermodule().getDefaultScenefilter()
        surface_density = 10000 / min(self._dimensions_px) ** 2
        self._root_scene.convertToPointCloud(graphics_filter, self._node_set, self._output_coordinates, 0.0, 0.0, surface_density, 1.0)

    def get_output_filename(self):
        return self._output_filename


def try_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return s


def alphanum_key(s):
    """
    Turn a string into a list of string and number chunks.
    "z23a" -> ["z", 23, "a"]
    """
    return [try_int(c) for c in re.split('([0-9]+)', s)]
