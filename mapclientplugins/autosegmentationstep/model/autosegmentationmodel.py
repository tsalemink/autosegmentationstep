"""
Created: April, 2023

@author: tsalemink
"""
import math

from cmlibs.zinc.context import Context
from cmlibs.zinc.field import Field, FieldImage

from cmlibs.utils.zinc.finiteelement import create_cube_element, create_square_element
from cmlibs.utils.zinc.field import create_field_coordinates, create_field_visibility_for_plane
from cmlibs.utils.zinc.node import get_field_values
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.geometry.plane import ZincPlane

from cmlibs.maths.vectorops import add, cross, matrix_vector_mult, angle, axis_angle_to_rotation_matrix
from cmlibs.maths.algorithms import calculate_centroid
from cmlibs.zinc.result import RESULT_OK


class AutoSegmentationModel(object):
    def __init__(self, input_image_data):
        self._context = Context('Auto-Segmentation')

        self._root_region = self._context.getDefaultRegion()
        self._mesh_region = self._root_region.createChild("segmentation_mesh")
        self._detection_region = self._root_region.createChild('detection')
        self._output_region = self._root_region.createChild('output')
        self._root_scene = self._root_region.getScene()
        self._mesh_scene = self._mesh_region.getScene()
        self._detection_scene = self._detection_region.getScene()
        self._output_scene = self._output_region.getScene()
        self._field_module = self._root_region.getFieldmodule()

        self._input_image_data = input_image_data
        self._output_filename = None

        self._source_image_field = self._initialise_image_field()
        self._dimensions_px = self._source_image_field.getSizeInPixels(3)[1]
        self._scale = [1, 1, 1]
        self._segmentation_value_field = self._field_module.createFieldConstant(0.0)
        self._threshold_field = self._field_module.createFieldConstant(0.0)
        self._targeted_mode = False
        self._image_field, self._filtered_image_field = self._create_value_image_field()

        self._scalar_field = self._create_finite_elements()

        self._output_coordinates, self._node_set = self._setup_output_region()
        self._do_histo_calc = False
        self._histogram = self._calculate_histo_data()

        self._detection_coordinates = self._setup_detection_region()
        self._mesh_coordinates = self._setup_mesh_region()

        self._detection_plane = self._create_detection_plane()
        self._visibility_field = self._create_visibility_field()

        self._define_standard_glyphs()
        self._point_cloud_material = None
        self._contour_material = None
        self._mesh_material = None
        self._plane_material = None
        self._define_materials()

    def get_context(self):
        return self._context

    def get_root_region(self):
        return self._root_region

    def get_mesh_region(self):
        return self._mesh_region

    def get_detection_region(self):
        return self._detection_region

    def get_output_region(self):
        return self._output_region

    def get_field_module(self):
        return self._field_module

    def get_root_scene(self):
        return self._root_scene

    def get_mesh_scene(self):
        return self._mesh_scene

    def get_detection_scene(self):
        return self._detection_scene

    def get_output_scene(self):
        return self._output_scene

    def get_image_field(self):
        return self._filtered_image_field if self._targeted_mode else self._image_field

    def get_targeted_adjustment_value(self):
        return 0.01 if self._targeted_mode else 0.0

    def get_source_image_field(self):
        return self._source_image_field

    def get_scalar_field(self):
        return self._scalar_field

    def get_dimensions(self):
        return self._dimensions_px

    def set_targeted_mode(self, state):
        self._targeted_mode = state

    def set_scale(self, scale):
        self._scale = scale
        self._update_mesh_nodes()

    def get_scale(self):
        return self._scale

    def get_output_coordinates(self):
        return self._output_coordinates

    def get_mesh_coordinates(self):
        return self._mesh_coordinates

    def get_detection_coordinates(self):
        return self._detection_coordinates

    def get_node_set(self):
        return self._node_set

    def get_detection_plane(self):
        return self._detection_plane

    def get_visibility_field(self):
        return self._visibility_field

    def get_point_cloud_material(self):
        return self._point_cloud_material

    def get_contour_material(self):
        return self._contour_material

    def get_mesh_material(self):
        return self._mesh_material

    def get_plane_material(self):
        return self._plane_material

    def _define_standard_glyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def _define_materials(self):
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()
        self._point_cloud_material = material_module.findMaterialByName("yellow")
        self._contour_material = material_module.findMaterialByName("white")
        self._mesh_material = material_module.findMaterialByName("blue")
        self._plane_material = material_module.findMaterialByName("green")

    def _create_finite_elements(self):
        self._field_module.beginChange()

        node_coordinate_set = self._define_node_positions()
        finite_element_field = create_field_coordinates(self._field_module, managed=True)
        mesh = self._field_module.findMeshByDimension(3)
        create_cube_element(mesh, finite_element_field, node_coordinate_set)
        scalar_field = self._field_module.createFieldComponent(finite_element_field, 3)

        self._field_module.defineAllFaces()
        self._field_module.endChange()

        return scalar_field

    def _define_node_positions(self):
        a, b, c = self._dimensions_px
        # Set a stretch factor to centre pixels at integer values.
        s = 0.5
        sx, sy, sz = tuple(self._scale)
        return [[sx * (0 - s), sy * (0 - s), sz * (0 - s)], [sx * (a - s), sy * (0 - s), sz * (0 - s)], [sx * (0 - s), sy * (b - s), sz * (0 - s)], [sx * (a - s), sy * (b - s), sz * (0 - s)],
                [sx * (0 - s), sy * (0 - s), sz * (c - s)], [sx * (a - s), sy * (0 - s), sz * (c - s)], [sx * (0 - s), sy * (b - s), sz * (c - s)], [sx * (a - s), sy * (b - s), sz * (c - s)]]

    def _update_mesh_nodes(self):
        node_set = self._field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        field_cache = self._field_module.createFieldcache()
        coordinate_field = self._field_module.findFieldByName('coordinates')
        node_positions = self._define_node_positions()
        node_iterator = node_set.createNodeiterator()
        node = node_iterator.next()
        while node.isValid():
            index = node.getIdentifier() - 1
            field_cache.setNode(node)
            coordinate_field.assignReal(field_cache, node_positions[index])
            node = node_iterator.next()

    def _initialise_image_field(self):
        with ChangeManager(self._field_module):
            image_field = self._field_module.createFieldImage()
            image_field.setFilterMode(FieldImage.FILTER_MODE_NEAREST)
            image_field.setWrapMode(FieldImage.WRAP_MODE_CLAMP)

            stream_information = image_field.createStreaminformationImage()
            for image_name in self._input_image_data.image_files():
                stream_information.createStreamresourceFile(image_name)

            image_field.read(stream_information)

        return image_field

    def _create_value_image_field(self):
        with ChangeManager(self._field_module):
            # threshold_segmentation_value_field = self._segmentation_value_field + self._threshold_field
            # const_two_field = self._field_module.createFieldConstant(2)
            const_zero_field = self._field_module.createFieldConstant(0.0)
            # double_segmentation_value_field = const_two_field * threshold_segmentation_value_field
            image_field = self._source_image_field
            if image_field.getNumberOfComponents() == 3:
                # Convert to intensity/grayscale image.
                component_1 = self._field_module.createFieldComponent(image_field, 1)
                component_2 = self._field_module.createFieldComponent(image_field, 2)
                component_3 = self._field_module.createFieldComponent(image_field, 3)
                # PAL, NTSC scaling.
                scale_1 = self._field_module.createFieldConstant(0.299)
                scale_2 = self._field_module.createFieldConstant(0.587)
                scale_3 = self._field_module.createFieldConstant(0.114)
                luminance_field = scale_1 * component_1 + scale_2 * component_2 + scale_3 * component_3
                # image_field = self._field_module.createFieldImageFromSource(luminance_field)
                image_field = luminance_field

            greater_than_field = image_field > self._segmentation_value_field
            filtered_image_field = self._field_module.createFieldIf(greater_than_field, const_zero_field, image_field)
            # value_diff_field = image_field - threshold_segmentation_value_field
            # abs_diff_field = self._field_module.createFieldAbs(value_diff_field)
            #
            # image_field = double_segmentation_value_field - abs_diff_field

        return image_field, filtered_image_field

    def _setup_output_region(self):
        field_module = self._output_region.getFieldmodule()

        output_coordinates = create_field_coordinates(field_module)

        node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)

        return output_coordinates, node_set

    def _setup_detection_region(self):
        field_module = self._detection_region.getFieldmodule()
        detection_coordinates = create_field_coordinates(field_module, managed=True)

        return detection_coordinates

    def _setup_mesh_region(self):
        field_module = self._mesh_region.getFieldmodule()
        mesh_coordinates = create_field_coordinates(field_module, managed=True)

        return mesh_coordinates

    def _create_detection_plane(self):
        node_coordinate_set = self._define_node_positions()
        point_on_plane = calculate_centroid(node_coordinate_set)
        plane_normal = [1.0, 0.0, 0.0]

        field_module = self._mesh_region.getFieldmodule()
        plane = ZincPlane(field_module)
        plane.setPlaneEquation(plane_normal, point_on_plane)

        max_dimension = max(self._dimensions_px)
        half_max_dimension = max_dimension / 2
        p_h_m_d = half_max_dimension
        n_h_m_d = -half_max_dimension
        element_points = [[n_h_m_d, n_h_m_d, 0], [p_h_m_d, n_h_m_d, 0], [n_h_m_d, p_h_m_d, 0], [p_h_m_d, p_h_m_d, 0]]
        element_normal = [0, 0, 1.0]

        theta = angle(plane_normal, element_normal)
        rot_mx = axis_angle_to_rotation_matrix(cross(element_normal, plane_normal), theta)
        rot_element_points = [add(matrix_vector_mult(rot_mx, pt), point_on_plane) for pt in element_points]

        field_module = self._detection_region.getFieldmodule()
        with ChangeManager(field_module):
            mesh = field_module.findMeshByDimension(2)
            create_square_element(mesh, self._detection_coordinates, rot_element_points)

        return plane

    def _create_visibility_field(self):
        field_module = self._mesh_region.getFieldmodule()
        coordinate_field = field_module.findFieldByName('coordinates')
        visibility_field = create_field_visibility_for_plane(field_module, coordinate_field, self._detection_plane)

        return visibility_field

    def clear_segmentation_mesh(self):
        field_module = self._mesh_region.getFieldmodule()
        mesh = field_module.findMeshByDimension(2)
        mesh.destroyAllElements()
        node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        node_set.destroyAllNodes()

    def reverse_visibility_field_direction(self):
        normal = self._detection_plane.getNormal()
        reverse_normal = [-component for component in normal]
        self._detection_plane.setNormal(reverse_normal)

    def plane_nodes_coordinates(self):
        field_module = self._detection_region.getFieldmodule()
        coordinate_field_name = self._detection_coordinates.getName()
        coordinate_field = field_module.findFieldByName(coordinate_field_name).castFiniteElement()
        return get_field_values(self._detection_region, coordinate_field)

    def _calculate_histo_data(self):
        bins = None
        if self._do_histo_calc:
            with ChangeManager(self._field_module):
                field_cache = self._field_module.createFieldcache()
                mesh = self._field_module.findMeshByDimension(3)
                element_iterator = mesh.createElementiterator()
                element = element_iterator.next()
                dim = self._dimensions_px

                bin_count = 100
                total = dim[0] * dim[1] * dim[2]
                bins = [0] * bin_count
                vals = [0] * bin_count

                data = {"bins": [0] * bin_count}
                max_value = -math.inf
                min_value = math.inf
                for i in range(dim[0]):
                    for j in range(dim[1]):
                        for k in range(dim[2]):
                            xi = [(i + 0.5) / dim[0], (j + 0.5) / dim[1], (k + 0.5) / dim[2]]
                            field_cache.setMeshLocation(element, xi)
                            result, value = self._image_field.evaluateReal(field_cache, 1)
                            max_value = max(max_value, value)
                            min_value = min(min_value, value)
                            # Assuming data is already scaled between 0.0 and 1.0.
                            binned_value = int(bin_count * value)
                            # Include max_value (currently assuming that this is 1.0) into last bin.
                            binned_value = binned_value if binned_value < bin_count else bin_count - 1
                            data["bins"][binned_value] += 1
                            str_value = f"{value}"
                            if str_value not in data:
                                data[str_value] = 0
                            data[str_value] += 1
                            # value_index = int(value * (bin_count - 1) + 0.5)
                            # bins[value_index] += 1
                            # vals[value_index] = value

                print(data)
                # print([b for b in bins if b > 0.0])
                # print([v for v in vals if v != 0.0])
                # bins = [b / total for b in bins]
                # print(bins)
                # print([(bins.index(b), b) for b in bins if b > 0.0])
        return bins

    def get_histogram_data(self):
        return self._histogram

    def generate_points(self, point_density=100):
        self._node_set.destroyAllNodes()
        graphics_filter = self._context.getScenefiltermodule().getDefaultScenefilter()
        self._root_scene.convertToPointCloud(graphics_filter, self._node_set, self._output_coordinates, 0.0, 0.0, point_density, 1.0)

    def get_output_filename(self):
        return self._output_filename

    def print_messages(self):
        logger = self._context.getLogger()
        for i in range(1, logger.getNumberOfMessages() + 1):
            print(f"{i} - {logger.getMessageTextAtIndex(i)}")

    def set_segmentation_value(self, value):
        field_cache = self._field_module.createFieldcache()
        self._segmentation_value_field.assignReal(field_cache, value)
        self._calculate_histo_data()

    def get_segmentation_value(self):
        field_cache = self._field_module.createFieldcache()
        result, value = self._segmentation_value_field.evaluateReal(field_cache, 1)
        if result == RESULT_OK:
            return value

        return 0.0

    # Map methods required for Orientation and Translation handlers.
    get_plane = get_detection_plane
    get_plane_region = get_detection_region
