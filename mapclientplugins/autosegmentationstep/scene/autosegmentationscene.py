"""
Created: April, 2023

@author: tsalemink
"""
from cmlibs.zinc.field import Field
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.material import Material


class AutoSegmentationScene(object):
    def __init__(self, model):
        self._model = model
        self._context = model.get_context()
        self._root_scene = model.get_root_scene()
        self._mesh_scene = model.get_mesh_scene()
        self._detection_scene = model.get_detection_scene()
        self._output_scene = model.get_output_scene()
        self._dimensions = model.get_dimensions()
        self._output_coordinates = model.get_output_coordinates()
        self._node_set = model.get_node_set()
        self._scale_field = model.get_field_module().createFieldConstant(model.get_scale())

        # Initialize the graphics.
        self._outline_graphics = self._create_outline_graphics()
        self._iso_graphic = self._create_surface_graphics()
        self._segmentation_contour = self._create_segmentation_graphics()
        self._segmentation_contour_material = model.get_contour_material()
        self._segmentation_contour.setMaterial(self._segmentation_contour_material)
        self._point_cloud = self._create_point_cloud_graphics()
        self._point_cloud.setMaterial(model.get_point_cloud_material())
        self._segmentation_mesh = self._create_mesh_graphics()
        self._segmentation_mesh_material = model.get_mesh_material()
        self._segmentation_mesh.setMaterial(self._segmentation_mesh_material)
        self._detection_plane = self._create_detection_plane()
        self._detection_plane_material = model.get_plane_material()
        self._detection_plane.setMaterial(self._detection_plane_material)

    def _create_outline_graphics(self):
        field_module = self._model.get_field_module()
        finite_element_field = field_module.findFieldByName('coordinates')

        self._root_scene.beginChange()
        outline = self._root_scene.createGraphicsLines()
        outline.setCoordinateField(finite_element_field)
        outline.setName('element_outline')
        self._root_scene.endChange()

        return outline

    def _create_surface_graphics(self):
        field_module = self._model.get_field_module()
        finite_element_field = field_module.findFieldByName('coordinates')
        xi_field = field_module.findFieldByName('xi')
        scalar_field = self._model.get_scalar_field()
        image_field = self._model.get_source_image_field()

        material_module = self._context.getMaterialmodule()
        material = material_module.createMaterial()
        material.setName('texture_block')
        material.setTextureField(1, image_field)

        self._root_scene.beginChange()
        iso_graphic = self._root_scene.createGraphicsContours()
        iso_graphic.setCoordinateField(finite_element_field)
        iso_graphic.setMaterial(material)
        iso_graphic.setTextureCoordinateField(xi_field)
        iso_graphic.setIsoscalarField(scalar_field)
        iso_graphic.setListIsovalues([0.0])
        self._root_scene.endChange()

        return iso_graphic

    def _create_segmentation_graphics(self):
        field_module = self._model.get_field_module()
        dimension_field = field_module.createFieldConstant(self._dimensions)
        xi_field = field_module.findFieldByName('xi')
        scaled_xi_field = xi_field * self._scale_field * dimension_field
        image_field = self._model.get_image_field()

        tessellation_module = self._context.getTessellationmodule()
        tessellation = tessellation_module.createTessellation()
        tessellation.setMinimumDivisions([int(d / 2 + 0.5) for d in self._dimensions])

        self._root_scene.beginChange()
        segmentation_contour = self._root_scene.createGraphicsContours()
        segmentation_contour.setCoordinateField(scaled_xi_field)
        segmentation_contour.setTessellation(tessellation)
        segmentation_contour.setIsoscalarField(image_field)
        segmentation_contour.setListIsovalues([0.0])
        self._root_scene.endChange()

        return segmentation_contour

    def _create_point_cloud_graphics(self):
        self._output_scene.beginChange()
        point_cloud = self._output_scene.createGraphicsPoints()
        point_cloud.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        point_cloud.setCoordinateField(self._output_coordinates)
        attributes = point_cloud.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        # attributes.setBaseSize([min(self._dimensions) / 100])
        self._output_scene.endChange()

        return point_cloud

    def _create_mesh_graphics(self):
        mesh_coordinates = self._model.get_mesh_coordinates()

        material_module = self._mesh_scene.getMaterialmodule()
        green = material_module.findMaterialByName("blue")

        self._mesh_scene.beginChange()
        segmentation_mesh = self._mesh_scene.createGraphicsSurfaces()
        segmentation_mesh.setCoordinateField(mesh_coordinates)
        segmentation_mesh.setMaterial(green)
        segmentation_mesh.setVisibilityFlag(True)
        visibility_field = self._model.get_visibility_field()
        segmentation_mesh.setSubgroupField(visibility_field)
        self._mesh_scene.endChange()

        return segmentation_mesh

    def _create_detection_plane(self):
        coordinate_field = self._model.get_detection_coordinates()

        material_module = self._detection_scene.getMaterialmodule()
        green = material_module.findMaterialByName("green")

        self._detection_scene.beginChange()
        detection_plane = self._detection_scene.createGraphicsSurfaces()
        detection_plane.setCoordinateField(coordinate_field)
        detection_plane.setMaterial(green)
        detection_plane.setVisibilityFlag(False)
        self._detection_scene.endChange()

        return detection_plane

    def set_point_size(self, value):
        attributes = self._point_cloud.getGraphicspointattributes()
        attributes.setBaseSize(value)

    def set_contour_alpha(self, value):
        self._segmentation_contour_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, value)

    def set_mesh_alpha(self, value):
        self._segmentation_mesh_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, value)

    def set_plane_alpha(self, value):
        self._detection_plane_material.setAttributeReal(Material.ATTRIBUTE_ALPHA, value)

    def set_outline_visibility(self, state):
        self._outline_graphics.setVisibilityFlag(state != 0)

    def set_image_plane_visibility(self, state):
        self._iso_graphic.setVisibilityFlag(state != 0)

    def set_segmentation_visibility(self, state):
        self._segmentation_contour.setVisibilityFlag(state != 0)

    def set_point_cloud_visibility(self, state):
        self._point_cloud.setVisibilityFlag(state != 0)

    def set_mesh_visibility(self, state):
        self._segmentation_mesh.setVisibilityFlag(state != 0)

    def set_detection_plane_visibility(self, state):
        self._detection_plane.setVisibilityFlag(state != 0)

    def set_slider_value(self, value):
        z_scale = self._model.get_scale()[2]
        self._iso_graphic.setListIsovalues([value * self._dimensions[2] * z_scale / 100])

    def set_segmentation_value(self, value):
        self._segmentation_contour.setListIsovalues([value / 10000.0])

    def get_tessellation_divisions(self):
        return self._segmentation_contour.getTessellation().getMinimumDivisions(3)[1]

    def set_tessellation_divisions(self, divisions):
        self._segmentation_contour.getTessellation().setMinimumDivisions(divisions)

    def update_scale(self):
        field_module = self._model.get_field_module()
        field_cache = field_module.createFieldcache()
        self._scale_field.assignReal(field_cache, self._model.get_scale())
