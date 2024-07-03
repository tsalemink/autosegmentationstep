"""
Created: April, 2023

@author: tsalemink
"""
import os
import json
import pathlib
import hashlib
import time

# import matplotlib.pyplot as plt

from PySide6 import QtWidgets, QtCore, QtGui

from cmlibs.exporter.stl import ArgonSceneExporter as STLExporter
from cmlibs.importer.stl import import_data_into_region as stl_import_data_into_region
from cmlibs.utils.zinc.field import create_field_coordinates
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.widgets.handlers.scenemanipulation import SceneManipulation
from cmlibs.widgets.handlers.orientation import Orientation
from cmlibs.widgets.handlers.fixedaxistranslation import FixedAxisTranslation
from cmlibs.zinc.field import FieldGroup

from mapclientplugins.autosegmentationstep.model.autosegmentationmodel import AutoSegmentationModel
from mapclientplugins.autosegmentationstep.scene.autosegmentationscene import AutoSegmentationScene
from mapclientplugins.autosegmentationstep.widgets.ui_autosegmentationwidget import Ui_AutoSegmentationWidget


def _set_double_validator(editor):
    editor.setValidator(QtGui.QDoubleValidator())


def _set_vector_validator(editor, regex):
    validator = QtGui.QRegularExpressionValidator(regex)
    editor.setValidator(validator)


def _get_element_identifiers(mesh):
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    element_identifiers = []
    while element.isValid():
        element_identifiers.append(element.getIdentifier())
        element = element_iterator.next()

    return element_identifiers


def _calculate_connected_elements(mesh, seed_element_identifier):
    field_module = mesh.getFieldmodule()
    element = mesh.findElementByIdentifier(seed_element_identifier)

    with ChangeManager(field_module):
        field_group = field_module.createFieldGroup()
        field_group.setName('the_group')
        field_group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)
        mesh_group = field_group.createMeshGroup(mesh)

        old_size = mesh_group.getSize()
        mesh_group.addElement(element)
        new_size = mesh_group.getSize()

        while new_size > old_size:
            old_size = new_size
            mesh_group.addAdjacentElements(1)
            new_size = mesh_group.getSize()

        element_identifiers = _get_element_identifiers(mesh_group)

        del mesh_group
        del field_group

    return element_identifiers


def _transform_mesh_to_list_form(mesh, mesh_field):
    """
    Transform a mesh to a list of element identifiers and a list of node identifiers.

    :param mesh: The mesh to transform.
    :param mesh_field: A field defined over the elements in the mesh.
    :return: A list of element identifiers, a list of lists of node identifiers.
    """
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    element_nodes = []
    element_identifiers = []
    while element.isValid():
        eft = element.getElementfieldtemplate(mesh_field, -1)
        local_node_count = eft.getNumberOfLocalNodes()
        node_identifiers = []
        for index in range(local_node_count):
            node = element.getNode(eft, index + 1)
            node_identifiers.append(node.getIdentifier())

        element_identifiers.append(element.getIdentifier())
        element_nodes.append(node_identifiers)

        element = element_iterator.next()

    return element_identifiers, element_nodes


def _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh):
    repeats = _find_duplicates(element_nodes)
    for repeat in repeats:
        repeated_element = mesh.findElementByIdentifier(element_identifiers[repeat])
        mesh.destroyElement(repeated_element)
        del element_identifiers[repeat]
        del element_nodes[repeat]


def _find_connected_mesh_elements_0d(mesh_coordinate_field):
    field_module = mesh_coordinate_field.getFieldmodule()

    mesh = field_module.findMeshByDimension(2)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_coordinate_field)
    _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh)

    initial_element_index = 0
    connected_sets = _find_connected(initial_element_index, element_nodes)
    if connected_sets is None:
        return

    el_ids = []
    for connected_set in connected_sets:
        el_ids.append([element_identifiers[index] for index in connected_set])

    return el_ids


def _find_connected_mesh_elements_1d(mesh_coordinate_field):
    field_module = mesh_coordinate_field.getFieldmodule()

    mesh = field_module.findMeshByDimension(2)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_coordinate_field)
    _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh)
    field_module.defineAllFaces()
    remainder_element_identifiers = element_identifiers[:]

    connected_sets = []
    while len(remainder_element_identifiers):
        connected_element_identifiers = _calculate_connected_elements(mesh, remainder_element_identifiers.pop(0))
        connected_sets.append(connected_element_identifiers)
        remainder_element_identifiers = list(set(remainder_element_identifiers) - set(connected_element_identifiers))

    return connected_sets


def _find_connected(seed_index, element_nodes):
    connected_elements = [[seed_index]]
    connected_nodes = [set(element_nodes[seed_index])]
    for element_index, element in enumerate(element_nodes):
        if element_index == seed_index:
            continue

        connected_elements.append([element_index])
        connected_nodes.append(set(element_nodes[element_index]))

        index = 0
        while index < len(connected_elements):
            connection_found = False
            next_index = index + 1
            base_connected_node_set = connected_nodes[index]
            while next_index < len(connected_elements):
                current_connected_node_set = connected_nodes[next_index]
                intersection = base_connected_node_set.intersection(current_connected_node_set)
                if len(intersection):
                    connection_found = True
                    connected_elements[index].extend(connected_elements[next_index])
                    connected_nodes[index].update(connected_nodes[next_index])
                    del connected_elements[next_index]
                    del connected_nodes[next_index]
                    index = 0
                    # next_index = 0
                else:
                    next_index += 1

            if not connection_found:
                index += 1

    return connected_elements


def _find_duplicates(element_nodes):
    """
    Given a list of integers, returns a list of all duplicate elements (with multiple duplicities).
    """
    num_count = {}
    duplicates = []

    for index, nodes in enumerate(element_nodes):
        sorted_nodes = tuple(sorted(nodes))
        if sorted_nodes in num_count:
            num_count[sorted_nodes].append(index)
        else:
            num_count[sorted_nodes] = [index]

    # Add duplicates to the result list
    for num, count in num_count.items():
        if len(count) > 1:
            duplicates.extend(count[1:])

    return sorted(duplicates, reverse=True)


class AutoSegmentationWidget(QtWidgets.QWidget):

    def __init__(self, image_data, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_AutoSegmentationWidget()
        self._ui.setupUi(self)

        self._ui.histogramPushButton.setVisible(False)

        self._callback = None
        self._location = None
        self._input_hash = None

        self._image_data = image_data
        self._model = AutoSegmentationModel(image_data)
        self._scene = AutoSegmentationScene(self._model)
        self._view = self._ui.zincWidget

        self._set_point_density_validator()
        self._set_point_size_validator()

        self._view.set_context(self._model.get_context())
        self._view.register_handler(SceneManipulation())

        orientation_handler = Orientation(QtCore.Qt.Key.Key_O)
        orientation_handler.set_model(self._model)
        self._view.register_handler(orientation_handler)

        normal_handler = FixedAxisTranslation(QtCore.Qt.Key.Key_T)
        normal_handler.set_model(self._model)
        self._view.register_handler(normal_handler)

        self._setup_tessellation_line_edit()
        self._set_scale_validator()
        display_dimensions = ", ".join([f"{d}" for d in self._model.get_dimensions()])
        self._ui.imagePixelOutputLabel.setText(f"{display_dimensions} px")

        self._make_connections()

    def _make_connections(self):
        self._ui.isoValueSlider.valueChanged.connect(self._scene.set_slider_value)
        self._ui.isoValueSlider.valueChanged.connect(self._set_line_edit_value)
        self._ui.segmentationValueSlider.valueChanged.connect(self._scene.set_segmentation_value)
        self._ui.segmentationValueSlider.valueChanged.connect(self._set_line_edit_value)
        self._ui.tessellationDivisionsLineEdit.editingFinished.connect(self._update_tessellation)
        self._ui.pointSizeLineEdit.editingFinished.connect(self._update_point_size)
        self._ui.scalingLineEdit.editingFinished.connect(self._update_scale)
        self._ui.allowHighTessellationsCheckBox.stateChanged.connect(self._set_tessellation_validator)
        self._ui.imagePlaneCheckBox.stateChanged.connect(self._scene.set_image_plane_visibility)
        self._ui.segmentationCheckBox.stateChanged.connect(self._scene.set_segmentation_visibility)
        self._ui.pointCloudCheckBox.stateChanged.connect(self._scene.set_point_cloud_visibility)
        self._ui.outlineCheckBox.stateChanged.connect(self._scene.set_outline_visibility)
        self._ui.segmentationAlphaDoubleSpinBox.valueChanged.connect(self._scene.set_contour_alpha)
        self._ui.generatePointsButton.clicked.connect(self._generate_points)
        self._ui.histogramPushButton.clicked.connect(self._histogram_clicked)
        self._ui.checkBoxToggleDetection.stateChanged.connect(self._toggle_detection_mode)
        self._ui.checkBoxReverseField.stateChanged.connect(self._model.reverse_visibility_field_direction)
        self._ui.segmentationMeshAlphaDoubleSpinBox.valueChanged.connect(self._scene.set_mesh_alpha)
        self._ui.detectionPlaneAlphaDoubleSpinBox.valueChanged.connect(self._scene.set_plane_alpha)
        self._ui.doneButton.clicked.connect(self._done_execution)

    def register_done_execution(self, done_execution):
        self._callback = done_execution

    # TODO: Check if segmentation threshold has actually changed or if we can just show the same mesh.
    def _toggle_detection_mode(self, checked):
        if checked:
            self._model.clear_segmentation_mesh()
            self._transform_contours_to_mesh()
            self._generate_segmentation_mesh(self._model.get_mesh_coordinates())
            connected_elements = _find_connected_mesh_elements_0d(self._model.get_mesh_coordinates())
            # connected_elements = self._find_connected_mesh_elements_1d(self._model.get_mesh_coordinates())
        self._scene.set_mesh_visibility(checked)
        self._scene.set_detection_plane_visibility(checked)
        self._scene.set_segmentation_visibility(not checked)
        self._scene.set_point_cloud_visibility(not checked)

        # Enable/disable relevant UI elements.
        self._ui.segmentationCheckBox.setEnabled(not checked)
        self._ui.pointCloudCheckBox.setEnabled(not checked)
        self._ui.generatePointsButton.setEnabled(not checked)

    def _settings_file(self):
        return os.path.join(self._location, 'settings.json')

    def _write_point_cloud(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        self._model.get_output_region().writeFile(self.get_output_filename())

    def _transform_exported_mesh_to_exf(self):
        root_region = self._model.get_root_region()
        temp_region = root_region.createChild("__temp")
        field_module = temp_region.getFieldmodule()
        coordinate_field = create_field_coordinates(field_module)

        self._generate_segmentation_mesh(coordinate_field)

        temp_region.writeFile(self.get_segmentation_graphics_filename())
        root_region.removeChild(temp_region)

    def _generate_segmentation_mesh(self, coordinate_field):
        inputs_stl = os.path.join(self._location, "ArgonSceneExporterSTL_zinc_graphics.stl")
        if not os.path.exists(inputs_stl):
            return

        region = coordinate_field.getFieldmodule().getRegion()
        stl_import_data_into_region(region, inputs_stl)

        # output_exf = os.path.join(self._location, "mesh_of_stl.exf")
        # region.writeFile(output_exf)

        # Delete the WebGL JSON files.
        os.remove(inputs_stl)

    def _export_segmentation_graphics(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        self._transform_contours_to_mesh()
        self._transform_exported_mesh_to_exf()

    def _transform_contours_to_mesh(self):
        # Export the scene into an STL file.
        self._hide_graphics()
        scene = self._model.get_root_scene()
        scene_filter = self._model.get_context().getScenefiltermodule().getDefaultScenefilter()
        alt_scene_exporter = STLExporter(self._location)
        alt_scene_exporter.export_stl_from_scene(scene, scene_filter)
        self._reinstate_graphics()

    def _generate_input_hash(self):
        normalised_file_paths = [pathlib.PureWindowsPath(os.path.relpath(file_path, self._location)).as_posix()
                                 for file_path in self._image_data.image_files()]
        return hashlib.md5(json.dumps(normalised_file_paths).encode('utf-8')).hexdigest()

    def _hide_graphics(self):
        self._scene.set_outline_visibility(0)
        self._scene.set_image_plane_visibility(0)
        self._scene.set_point_cloud_visibility(0)
        self._scene.set_detection_plane_visibility(0)
        self._scene.set_mesh_visibility(0)

    def _reinstate_graphics(self):
        self._scene.set_outline_visibility(1 if self._ui.outlineCheckBox.isChecked() else 0)
        self._scene.set_segmentation_visibility(1 if self._ui.segmentationCheckBox.isChecked() else 0)
        self._scene.set_image_plane_visibility(1 if self._ui.imagePlaneCheckBox.isChecked() else 0)
        self._scene.set_point_cloud_visibility(1 if self._ui.pointCloudCheckBox.isChecked() else 0)
        self._scene.set_detection_plane_visibility(1 if self._ui.checkBoxToggleDetection.isChecked() else 0)
        self._scene.set_mesh_visibility(1 if self._ui.checkBoxToggleDetection.isChecked() else 0)

    def _done_execution(self):
        self._save_settings()
        # self._import_segmentation_mesh()
        self._write_point_cloud()
        self._callback()

    def load_settings(self):
        self._input_hash = self._generate_input_hash()
        if os.path.isfile(self._settings_file()):
            with open(self._settings_file()) as f:
                settings = json.load(f)
        else:
            settings = {}

        if "input-hash" in settings:
            if self._input_hash != settings["input-hash"]:
                return

        self._ui.isoValueSlider.setValue(int(settings.get("iso-value", "0")))
        self._ui.segmentationValueSlider.setValue(int(settings.get("contour-value", "0")))
        self._ui.segmentationValueLineEdit.setText(f"{self._ui.segmentationValueSlider.value() / 10000.0}")
        self._ui.imagePlaneCheckBox.setChecked(settings.get("image-plane", True))
        self._ui.pointCloudCheckBox.setChecked(settings.get("point-cloud", True))
        self._ui.segmentationCheckBox.setChecked(settings.get("segmentation", True))
        self._ui.outlineCheckBox.setChecked(settings.get("outline", True))
        self._ui.segmentationAlphaDoubleSpinBox.setValue(settings.get("alpha", 1.0))
        self._ui.allowHighTessellationsCheckBox.setChecked(settings.get("tessellation-override", False))
        self._ui.overrideScalingCheckBox.setChecked(settings.get("scaling-override", False))
        self._ui.scalingLineEdit.setText(settings.get("scaling", "1, 1, 1"))
        self._ui.segmentationMeshAlphaDoubleSpinBox.setValue(settings.get("mesh-alpha", 1.0))
        self._ui.detectionPlaneAlphaDoubleSpinBox.setValue(settings.get("plane-alpha", 1.0))

        dimensions = self._model.get_dimensions()
        min_dim = min(dimensions)
        self._ui.tessellationDivisionsLineEdit.setText(settings.get("tessellation", ", ".join([str(int(d / 2 + 0.5)) for d in dimensions])))
        self._ui.pointDensityLineEdit.setText(settings.get("point-density", f'{10000 / min_dim ** 2}'))
        self._ui.pointSizeLineEdit.setText(settings.get("point-size", f'{min_dim / 100}'))

        z_size = dimensions[2]
        z_scale = self._model.get_scale()[2]
        self._ui.isoValueLineEdit.setText(f"{self._ui.isoValueSlider.value() * z_size * z_scale / 100.0}")

        if os.path.isfile(self.get_output_filename()):
            self._model.get_output_region().readFile(self.get_output_filename())

        self._update_point_size()
        self._update_scale()

    def _save_settings(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        settings = {
            "input-hash": self._input_hash,
            "iso-value": self._ui.isoValueSlider.value(),
            "contour-value": self._ui.segmentationValueSlider.value(),
            "image-plane": self._ui.imagePlaneCheckBox.isChecked(),
            "point-cloud": self._ui.pointCloudCheckBox.isChecked(),
            "segmentation": self._ui.segmentationCheckBox.isChecked(),
            "outline": self._ui.outlineCheckBox.isChecked(),
            "tessellation": self._ui.tessellationDivisionsLineEdit.text(),
            "alpha": self._ui.segmentationAlphaDoubleSpinBox.value(),
            "tessellation-override": self._ui.allowHighTessellationsCheckBox.isChecked(),
            "scaling-override": self._ui.overrideScalingCheckBox.isChecked(),
            "scaling": self._ui.scalingLineEdit.text(),
            "point-density": self._ui.pointDensityLineEdit.text(),
            "point-size": self._ui.pointSizeLineEdit.text(),
            "mesh-alpha": self._ui.segmentationMeshAlphaDoubleSpinBox.value(),
            "plane-alpha": self._ui.detectionPlaneAlphaDoubleSpinBox.value(),
        }

        with open(self._settings_file(), "w") as f:
            json.dump(settings, f)

    def set_location(self, location):
        self._location = location

    def get_output_filename(self):
        return os.path.join(self._location, "point-cloud.exf")

    def get_segmentation_graphics_filename(self):
        return os.path.join(self._location, "segmentation-graphics.exf")

    def _set_line_edit_value(self, value):
        if self.sender() == self._ui.isoValueSlider:
            z_size = self._model.get_dimensions()[2]
            z_scale = self._model.get_scale()[2]
            self._ui.isoValueLineEdit.setText(f"{value * z_size * z_scale / 100.0}")
        elif self.sender() == self._ui.segmentationValueSlider:
            self._ui.segmentationValueLineEdit.setText(f"{value / 10000.0}")

    def _setup_tessellation_line_edit(self):
        divisions = self._scene.get_tessellation_divisions()
        divisions = ", ".join([str(i) for i in divisions])
        self._ui.tessellationDivisionsLineEdit.setText(divisions)

        self._set_tessellation_validator()

    def _set_scale_validator(self):
        regex = QtCore.QRegularExpression("^[0-9.]+((, ?[0-9.]+){2})?$")
        _set_vector_validator(self._ui.scalingLineEdit, regex)

    def _set_tessellation_validator(self):
        size = 5 if self._ui.allowHighTessellationsCheckBox else 3
        regex = QtCore.QRegularExpression(f"^[0-9]{{1,{size}}}((, ?[0-9]{{1,{size}}}){{2}})?$")
        _set_vector_validator(self._ui.tessellationDivisionsLineEdit, regex)

    def _set_point_size_validator(self):
        _set_double_validator(self._ui.pointSizeLineEdit)

    def _set_point_density_validator(self):
        _set_double_validator(self._ui.pointDensityLineEdit)

    def _update_tessellation(self):
        text = self._ui.tessellationDivisionsLineEdit.text()
        divisions_list = [int(x.strip()) for x in text.split(',')]
        self._scene.set_tessellation_divisions(divisions_list)

    def _update_point_size(self):
        size = self._ui.pointSizeLineEdit.text()
        self._scene.set_point_size(float(size))

    def _update_scale(self):
        text = self._ui.scalingLineEdit.text()
        scale = [float(x.strip()) for x in text.split(',')]
        self._model.set_scale(scale)
        self._scene.update_scale()

    def _generate_points(self):
        self._scene.set_image_plane_visibility(0)
        self._scene.set_segmentation_visibility(1)
        self._model.generate_points(float(self._ui.pointDensityLineEdit.text()))
        # After the segmentation have been exported the graphics
        # will be re-instated to the correct state.
        self._export_segmentation_graphics()

    def _histogram_clicked(self):
        data = self._model.get_histogram_data()
        plt.hist(data, bins=len(data))
        plt.gca().set(title='Frequency Histogram', ylabel='Frequency')
        plt.show()
