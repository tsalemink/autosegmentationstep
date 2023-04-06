"""
Created: April, 2023

@author: tsalemink
"""
import os
import re

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import FieldImage
from opencmiss.zinc.element import Element, Elementbasis


class AutoSegmentationModel(object):
    def __init__(self, input_image_data):
        self._context = Context('Auto-Segmentation')

        self._input_image_data = input_image_data

        self._image_field = None
        self._segmented_field = None
        self._segmented_image_field = None
        self._smooth_field = None
        self._scalar_field = None
        self._material = None

        self._root_region = self._context.getDefaultRegion()
        self._field_module = self._root_region.getFieldmodule()
        self._scene = self._root_region.getScene()

        self._point_cloud_region = self._root_region.createChild('output')

        self.define_standard_glyphs()
        self.define_standard_materials()

        self._dimensions_px = None

        self.create_material_using_image_field()
        self.create_finite_elements()

        self._segmented_image_field = self._field_module.createFieldImageFromSource(self._segmented_field)

    def get_context(self):
        return self._context

    def get_root_region(self):
        return self._root_region

    def get_point_cloud_region(self):
        return self._point_cloud_region

    def get_field_module(self):
        return self._field_module

    def get_scene(self):
        return self._scene

    def get_material(self):
        return self._material

    def get_image_field(self):
        return self._image_field

    def get_scalar_field(self):
        return self._scalar_field

    def get_dimensions(self):
        return self._dimensions_px

    def define_standard_glyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def define_standard_materials(self):
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def create_finite_elements(self):
        self._field_module.beginChange()

        finite_element_field = self._field_module.createFieldFiniteElement(3)
        finite_element_field.setName('coordinates')
        finite_element_field.setManaged(True)
        finite_element_field.setTypeCoordinate(True)

        dim = self._dimensions_px
        node_coordinate_set = [[0, 0, 0], [dim[0], 0, 0], [0, dim[1], 0], [dim[0], dim[1], 0], [0, 0, dim[2]], [dim[0], 0, dim[2]],
                               [0, dim[1], dim[2]], [dim[0], dim[1], dim[2]]]

        create_3d_finite_element(self._field_module, finite_element_field, node_coordinate_set)

        self._scalar_field = self._field_module.createFieldComponent(finite_element_field, 3)

        self._field_module.defineAllFaces()

        self._field_module.endChange()

    def create_material_using_image_field(self):
        material_module = self._context.getMaterialmodule()
        self._material = material_module.createMaterial()
        self._material.setName('texture_block')

        self._image_field = self._field_module.createFieldImage()

        self._image_field.setFilterMode(FieldImage.FILTER_MODE_LINEAR)
        self._image_field.setWrapMode(FieldImage.WRAP_MODE_CLAMP)

        stream_information = self._image_field.createStreaminformationImage()

        directory = self._input_image_data.location()
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            if filename not in ['.hg', 'annotation.rdf']:
                string_name = str(os.path.join(directory, filename))
                stream_information.createStreamresourceFile(string_name)

        self._image_field.read(stream_information)
        self._material.setTextureField(1, self._image_field)

        self._dimensions_px = self._image_field.getSizeInPixels(3)[1]

        self._smooth_field = self._field_module.createFieldImagefilterCurvatureAnisotropicDiffusion(self._image_field, 0.0625, 2, 5)
        self._segmented_field = self._field_module.createFieldImagefilterConnectedThreshold(self._smooth_field, 0.2, 1.0, 1,
                                                                                            1, [0.5, 0.6111, 0.3889])

    def get_point_cloud(self):
        point_cloud = []
        field_module = self._point_cloud_region.getFieldmodule()
        field_module.beginChange()
        field_cache = field_module.createFieldcache()
        coordinate_field = field_module.findFieldByName('coordinates')
        nodeset = field_module.findNodesetByName('nodes')
        template = nodeset.createNodetemplate()
        template.defineField(coordinate_field)

        node_iterator = nodeset.createNodeiterator()
        node = node_iterator.next()
        while node.isValid():
            field_cache.setNode(node)
            position = coordinate_field.evaluateReal(field_cache, 3)[1]
            node = node_iterator.next()
            point_cloud.append(position)

        field_module.endChange()

        return point_cloud


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


def create_3d_finite_element(fieldmodule, finite_element_field, node_coordinate_set):
    """
    Create a single finite element using the supplied
    finite element field and node coordinate set.
    """
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()

    node_identifiers = []
    # Create eight nodes to define a cube finite element
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        node_identifiers.append(node.getIdentifier())
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        # Pass in floats as an array
        finite_element_field.assignReal(field_cache, node_coordinate)

    # Use a 3D mesh to to create the 3D finite element.
    mesh = fieldmodule.findMeshByDimension(3)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    element_node_count = 8
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]

    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for i, node_identifier in enumerate(node_identifiers):
        node = nodeset.findNodeByIdentifier(node_identifier)
        element_template.setNode(i + 1, node)

    mesh.defineElement(-1, element_template)
