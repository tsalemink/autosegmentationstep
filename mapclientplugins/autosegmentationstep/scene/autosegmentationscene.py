"""
Created: April, 2023

@author: tsalemink
"""
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph


class AutoSegmentationScene(object):
    def __init__(self, model):
        self._model = model
        self._context = model.get_context()

        self._iso_graphic = None
        self._segmentation_contour = None
        self._point_cloud = None

        tessellation_module = self._context.getTessellationmodule()
        tessellation = tessellation_module.createTessellation()
        tessellation.setMinimumDivisions([64])

        scene = self._model.get_scene()

        scene.beginChange()

        field_module = self._model.get_field_module()
        xi_field = field_module.findFieldByName('xi')

        # Visualise the outline.
        self._create_outline_graphics(scene)

        image_field = self._model.get_image_field()
        self._segmentation_contour = scene.createGraphicsContours()
        self._segmentation_contour.setCoordinateField(xi_field)
        self._segmentation_contour.setTessellation(tessellation)
        self._segmentation_contour.setIsoscalarField(image_field)
        self._segmentation_contour.setListIsovalues([0.0])

        self._node_set, self._output_coordinates = self.setup_output_region()

        # Set the scene to our scene viewer.
        self.create_surface_graphics(self._model.get_root_region())

        scene.endChange()

    def set_image_plane_visibility(self, state):
        self._iso_graphic.setVisibilityFlag(state != 0)

    def set_segmentation_visibility(self, state):
        self._segmentation_contour.setVisibilityFlag(state != 0)

    def set_point_cloud_visibility(self, state):
        self._point_cloud.setVisibilityFlag(state != 0)

    def set_slider_value(self, value):
        self._iso_graphic.setListIsovalues([value / 100.0])

    def set_segmentation_value(self, value):
        self._segmentation_contour.setListIsovalues([value / 10000.0])

    def generate_points(self):
        self._node_set.destroyAllNodes()
        self.set_image_plane_visibility(0)
        scene = self._context.getDefaultRegion().getScene()
        graphics_filter = self._context.getScenefiltermodule().getDefaultScenefilter()
        scene.convertToPointCloud(graphics_filter, self._node_set, self._output_coordinates, 0.0, 0.0, 10000.0, 1.0)
        self.set_image_plane_visibility(1)

    def create_surface_graphics(self, region):
        scene = region.getScene()
        field_module = region.getFieldmodule()
        finite_element_field = field_module.findFieldByName('coordinates')

        material = self._model.get_material()
        scalar_field = self._model.get_scalar_field()

        self._iso_graphic = scene.createGraphicsContours()
        self._iso_graphic.setCoordinateField(finite_element_field)
        self._iso_graphic.setMaterial(material)
        xi_field = field_module.findFieldByName('xi')
        self._iso_graphic.setTextureCoordinateField(xi_field)
        self._iso_graphic.setIsoscalarField(scalar_field)
        self._iso_graphic.setListIsovalues([0.0])

    def _create_outline_graphics(self, scene):
        field_module = self._model.get_field_module()
        finite_element_field = field_module.findFieldByName('coordinates')

        scene.beginChange()
        outline = scene.createGraphicsLines()
        outline.setCoordinateField(finite_element_field)
        outline.setName('element_outline')
        scene.endChange()

        return outline

    # TODO: Part of this should be done in the model.
    def setup_output_region(self):
        point_cloud_region = self._model.get_point_cloud_region()
        field_module = point_cloud_region.getFieldmodule()
        finite_element_field = field_module.createFieldFiniteElement(3)
        # Set the name of the field, we give it label to help us understand it's purpose
        finite_element_field.setName('coordinates')
        # Set the attribute is managed to 1 so the field module will manage the field for us
        finite_element_field.setManaged(True)

        nodeset = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)

        scene = point_cloud_region.getScene()
        self._point_cloud = scene.createGraphicsPoints()
        self._point_cloud.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        self._point_cloud.setCoordinateField(finite_element_field)
        attributes = self._point_cloud.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize([0.01])

        return nodeset, finite_element_field
