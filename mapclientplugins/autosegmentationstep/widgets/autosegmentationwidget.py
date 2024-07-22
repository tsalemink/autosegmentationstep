"""
Created: April, 2023

@author: tsalemink
"""
import os
import json
import pathlib
import hashlib

# import matplotlib.pyplot as plt

from PySide6 import QtWidgets, QtCore, QtGui

from cmlibs.exporter.stl import ArgonSceneExporter as STLExporter
from cmlibs.importer.stl import import_data_into_region as stl_import_data_into_region
from cmlibs.utils.zinc.field import create_field_coordinates
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.zinc.mesh import find_connected_mesh_elements_0d
from cmlibs.widgets.handlers.scenemanipulation import SceneManipulation
from cmlibs.widgets.handlers.orientation import Orientation
from cmlibs.widgets.handlers.fixedaxistranslation import FixedAxisTranslation

from mapclientplugins.autosegmentationstep.model.autosegmentationmodel import AutoSegmentationModel
from mapclientplugins.autosegmentationstep.scene.autosegmentationscene import AutoSegmentationScene
from mapclientplugins.autosegmentationstep.widgets.ui_autosegmentationwidget import Ui_AutoSegmentationWidget


def _set_double_validator(editor):
    editor.setValidator(QtGui.QDoubleValidator())


def _set_vector_validator(editor, regex):
    validator = QtGui.QRegularExpressionValidator(regex)
    editor.setValidator(validator)


class AutoSegmentationWidget(QtWidgets.QWidget):

    def __init__(self, image_data, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_AutoSegmentationWidget()
        self._ui.setupUi(self)

        self._ui.histogramPushButton.setVisible(False)

        self._callback = None
        self._location = None
        self._input_hash = None
        self._detection_current = False

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
        self._ui.comboBoxConnectedSurfaces.setEnabled(self._ui.checkBoxToggleDetection.isChecked())

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
        self._ui.comboBoxConnectedSurfaces.currentIndexChanged.connect(self._connected_subgroup_changed)
        self._ui.checkBoxTargetSpecificValue.stateChanged.connect(self._target_specific_value_changed)

    def register_done_execution(self, done_execution):
        self._callback = done_execution

    def _create_mesh_field_group(self):
        field = self._model.get_mesh_coordinates()
        field_module = field.getFieldmodule()
        return field_module.createFieldGroup()

    def _update_connected_groups(self, result):
        self._ui.comboBoxConnectedSurfaces.clear()
        field = self._model.get_mesh_coordinates()
        field_module = field.getFieldmodule()
        with ChangeManager(field_module):
            mesh = field_module.findMeshByDimension(2)
            self._ui.comboBoxConnectedSurfaces.addItem("--", field_module.createFieldGroup())
            for i, r in enumerate(result):
                field_group = field_module.createFieldGroup()
                field_group.setName(f"el_group_{i + 1:02}")
                mesh_group = field_group.createMeshGroup(mesh)
                for e_id in r:
                    e = mesh.findElementByIdentifier(e_id)
                    mesh_group.addElement(e)
                self._ui.comboBoxConnectedSurfaces.addItem(field_group.getName(), field_group)

    def _connected_subgroup_changed(self, value):
        group = self._ui.comboBoxConnectedSurfaces.currentData() if value >= 0 else self._create_mesh_field_group()
        if group:
            self._scene.set_mesh_group(group, value > 0)

    def _target_specific_value_changed(self, state):
        self._model.set_targeted_mode(state == 2)
        self._scene.targeted_mode_changed()

    def _toggle_detection_mode(self, checked):
        if checked and not self._detection_current:
            self._detection_current = True
            self._ui.comboBoxConnectedSurfaces.clear()
            self._ui.comboBoxConnectedSurfaces.addItem("Pending")
            self._ui.comboBoxConnectedSurfaces.setEnabled(False)
            self._model.clear_segmentation_mesh()
            self._transform_contours_to_mesh()
            self._generate_segmentation_mesh(self._model.get_mesh_coordinates())

            connected_elements = find_connected_mesh_elements_0d(self._model.get_mesh_coordinates(), 2, True)
            self._update_connected_groups(connected_elements)

        self._scene.set_mesh_visibility(checked)
        self._scene.set_detection_plane_visibility(checked)
        self._scene.set_segmentation_visibility(not checked)
        self._scene.set_point_cloud_visibility(not checked)

        # Enable/disable relevant UI elements.
        self._ui.segmentationCheckBox.setEnabled(not checked)
        self._ui.pointCloudCheckBox.setEnabled(not checked)
        self._ui.generatePointsButton.setEnabled(not checked)
        self._ui.comboBoxConnectedSurfaces.setEnabled(checked)

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
        self._ui.checkBoxTargetSpecificValue.setChecked(settings.get("target-specific", False))

        dimensions = self._model.get_dimensions()
        min_dim = max(1, min(dimensions))
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
            "target-specific": self._ui.checkBoxTargetSpecificValue.isChecked(),
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
            self._detection_current = False

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
        if size:
            self._scene.set_point_size(float(size))

    def _update_scale(self):
        text = self._ui.scalingLineEdit.text()
        if text:
            scale = [float(x.strip()) for x in text.split(',')]
            self._model.set_scale(scale)
            self._scene.update_scale()

    def _generate_points(self):
        self._scene.set_image_plane_visibility(0)
        self._scene.set_segmentation_visibility(1)
        self._model.generate_points(float(self._ui.pointDensityLineEdit.text()))
        # After the segmentation has been exported the graphics
        # will be re-instated to the correct state.
        self._export_segmentation_graphics()

    def _histogram_clicked(self):
        data = self._model.get_histogram_data()
        plt.hist(data, bins=len(data))
        plt.gca().set(title='Frequency Histogram', ylabel='Frequency')
        plt.show()
