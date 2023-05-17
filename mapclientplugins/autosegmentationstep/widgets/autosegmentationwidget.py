"""
Created: April, 2023

@author: tsalemink
"""
import os
import json

from PySide6 import QtWidgets, QtCore, QtGui

from cmlibs.zinc.field import Field
from cmlibs.exporter.webgl import ArgonSceneExporter
from cmlibs.importer.webgl import import_data_into_region
from cmlibs.widgets.handlers.scenemanipulation import SceneManipulation

from mapclientplugins.autosegmentationstep.model.autosegmentationmodel import AutoSegmentationModel
from mapclientplugins.autosegmentationstep.scene.autosegmentationscene import AutoSegmentationScene
from mapclientplugins.autosegmentationstep.widgets.ui_autosegmentationwidget import Ui_AutoSegmentationWidget


class AutoSegmentationWidget(QtWidgets.QWidget):

    def __init__(self, image_data_location, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_AutoSegmentationWidget()
        self._ui.setupUi(self)

        self._callback = None
        self._location = None

        self._model = AutoSegmentationModel(image_data_location)
        self._scene = AutoSegmentationScene(self._model)
        self._view = self._ui.zincWidget

        self._view.set_context(self._model.get_context())
        self._view.register_handler(SceneManipulation())

        self._setup_tessellation_line_edit()

        self._make_connections()

    def _make_connections(self):
        self._ui.isoValueSlider.valueChanged.connect(self._scene.set_slider_value)
        self._ui.isoValueSlider.valueChanged.connect(self._set_line_edit_value)
        self._ui.segmentationValueSlider.valueChanged.connect(self._scene.set_segmentation_value)
        self._ui.segmentationValueSlider.valueChanged.connect(self._set_line_edit_value)
        self._ui.tessellationDivisionsLineEdit.editingFinished.connect(self._update_tessellation)
        self._ui.imagePlaneCheckBox.stateChanged.connect(self._scene.set_image_plane_visibility)
        self._ui.segmentationCheckBox.stateChanged.connect(self._scene.set_segmentation_visibility)
        self._ui.pointCloudCheckBox.stateChanged.connect(self._scene.set_point_cloud_visibility)
        self._ui.segmentationAlphaDoubleSpinBox.valueChanged.connect(self._scene.set_contour_alpha)
        self._ui.generatePointsButton.clicked.connect(self.generate_points)
        self._ui.doneButton.clicked.connect(self._done_execution)

    def register_done_execution(self, done_execution):
        self._callback = done_execution

    def _output_file(self):
        return os.path.join(self._location, "point-cloud.exf")

    def _settings_file(self):
        return os.path.join(self._location, 'settings.json')

    def _write_point_cloud(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        self._model.get_output_region().writeFile(self._output_file())

    def _import_segmentation_mesh(self):
        inputs = os.path.join(self._location, "ArgonSceneExporterWebGL_1.json")
        if not os.path.exists(inputs):
            return

        # Import the WebGL JSON file into Zinc.
        output_region = self._model.get_output_region()
        output_field_module = output_region.getFieldmodule()
        mesh_coordinate_field_name = 'mesh_coordinates'
        mesh_coordinates = output_field_module.findFieldByName(mesh_coordinate_field_name)

        mesh_2d = output_field_module.findMeshByDimension(2)
        mesh_2d.destroyAllElements()
        node_set = self._model.get_node_set()
        node_set.destroyNodesConditional(mesh_coordinates)

        import_data_into_region(output_region, inputs, mesh_coordinate_field_name)

        # Delete the WebGL JSON files.
        os.remove(inputs)
        os.remove(os.path.join(self._location, "ArgonSceneExporterWebGL_metadata.json"))

    def _export_segmentation_graphics(self):
        # Export the scene into a WebGL JSON file.
        self._hide_graphics()
        scene = self._model.get_root_scene()
        scene_filter = self._model.get_context().getScenefiltermodule().getDefaultScenefilter()
        scene_exporter = ArgonSceneExporter(self._location)
        scene_exporter.export_webgl_from_scene(scene, scene_filter)
        self._show_graphics()

    def _hide_graphics(self):
        self._scene.set_outline_visibility(0)
        self._scene.set_image_plane_visibility(0)
        self._scene.set_point_cloud_visibility(0)

    def _show_graphics(self):
        self._scene.set_outline_visibility(1)
        self._scene.set_image_plane_visibility(1)
        self._scene.set_point_cloud_visibility(1)

    def _done_execution(self):
        self._save_settings()
        self._import_segmentation_mesh()
        self._write_point_cloud()
        self._callback()

    def load_settings(self):
        if os.path.isfile(self._settings_file()):
            with open(self._settings_file()) as f:
                settings = json.load(f)

            if "iso-value" in settings:
                self._ui.isoValueSlider.setValue(int(settings["iso-value"]))
            if "contour-value" in settings:
                self._ui.segmentationValueSlider.setValue(int(settings["contour-value"]))
            if "image-plane" in settings:
                self._ui.imagePlaneCheckBox.setChecked(settings["image-plane"])
            if "point-cloud" in settings:
                self._ui.pointCloudCheckBox.setChecked(settings["point-cloud"])
            if "segmentation" in settings:
                self._ui.segmentationCheckBox.setChecked(settings["segmentation"])
            if "tessellation" in settings:
                self._ui.tessellationDivisionsLineEdit.setText(settings["tessellation"])
            if "alpha" in settings:
                self._ui.segmentationAlphaDoubleSpinBox.setValue(settings["alpha"])

        if os.path.isfile(self._output_file()):
            self._model.get_output_region().readFile(self._output_file())
            self._export_segmentation_graphics()

    def _save_settings(self):
        if not os.path.exists(self._location):
            os.makedirs(self._location)

        settings = {
            "iso-value": self._ui.isoValueSlider.value(),
            "contour-value": self._ui.segmentationValueSlider.value(),
            "image-plane": self._ui.imagePlaneCheckBox.isChecked(),
            "point-cloud": self._ui.pointCloudCheckBox.isChecked(),
            "segmentation": self._ui.segmentationCheckBox.isChecked(),
            "tessellation": self._ui.tessellationDivisionsLineEdit.text(),
            "alpha": self._ui.segmentationAlphaDoubleSpinBox.value(),
        }

        with open(self._settings_file(), "w") as f:
            json.dump(settings, f)

    def set_location(self, location):
        self._location = location

    def get_output_filename(self):
        return self._output_file()

    def _set_line_edit_value(self, value):
        if self.sender() == self._ui.isoValueSlider:
            z_size = self._model.get_dimensions()[2]
            self._ui.isoValueLineEdit.setText(f"{value * z_size / 100.0}")
        elif self.sender() == self._ui.segmentationValueSlider:
            self._ui.segmentationValueLineEdit.setText(f"{value / 10000.0}")

    def _setup_tessellation_line_edit(self):
        divisions = self._scene.get_tessellation_divisions()
        divisions = ",".join([str(i) for i in divisions])
        self._ui.tessellationDivisionsLineEdit.setText(divisions)

        regex = QtCore.QRegularExpression("^[0-9]{1,3}((, ?[0-9]{1,3}){2})?$")
        validator = QtGui.QRegularExpressionValidator(regex)
        self._ui.tessellationDivisionsLineEdit.setValidator(validator)

    def _update_tessellation(self):
        text = self._ui.tessellationDivisionsLineEdit.text()
        divisions_list = [int(x.strip()) for x in text.split(',')]
        self._scene.set_tessellation_divisions(divisions_list)

    def generate_points(self):
        self._scene.set_image_plane_visibility(0)
        self._scene.set_segmentation_visibility(1)
        self._model.generate_points()
        self._scene.set_image_plane_visibility(self._ui.imagePlaneCheckBox.isChecked())
        self._scene.set_segmentation_visibility(self._ui.segmentationCheckBox.isChecked())
        self._export_segmentation_graphics()
