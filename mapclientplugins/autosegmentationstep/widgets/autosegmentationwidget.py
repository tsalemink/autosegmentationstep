"""
Created: April, 2023

@author: tsalemink
"""
from PySide6 import QtWidgets, QtCore, QtGui

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

        self._model = AutoSegmentationModel(image_data_location)
        self._scene = AutoSegmentationScene(self._model)
        self._view = self._ui.zincWidget

        self._view.set_context(self._model.get_context())
        self._view.register_handler(SceneManipulation())

        self._setup_tessellation_line_edit()

        self._make_connections()

    def _make_connections(self):
        self._ui.isoValueSlider.valueChanged.connect(self._scene.set_slider_value)
        self._ui.segmentationValueSlider.valueChanged.connect(self._scene.set_segmentation_value)
        self._ui.lineEditTessellationDivisions.editingFinished.connect(self._update_tessellation)
        self._ui.imagePlaneCheckBox.stateChanged.connect(self._scene.set_image_plane_visibility)
        self._ui.segmentationCheckBox.stateChanged.connect(self._scene.set_segmentation_visibility)
        self._ui.pointCloudCheckBox.stateChanged.connect(self._scene.set_point_cloud_visibility)
        self._ui.generatePointsButton.clicked.connect(self._scene.generate_points)
        self._ui.doneButton.clicked.connect(self._done_execution)

    def register_done_execution(self, done_execution):
        self._callback = done_execution

    def _done_execution(self):
        self._model.write_point_cloud()
        self._callback()

    def set_location(self, location):
        self._model.set_location(location)

    def get_output_filename(self):
        return self._model.get_output_filename()

    def _setup_tessellation_line_edit(self):
        divisions = self._scene.get_tessellation_divisions()
        divisions = ",".join([str(i) for i in divisions])
        self._ui.lineEditTessellationDivisions.setText(divisions)

        regex = QtCore.QRegularExpression("^[0-9]{1,3}((, ?[0-9]{1,3}){2})?$")
        validator = QtGui.QRegularExpressionValidator(regex)
        self._ui.lineEditTessellationDivisions.setValidator(validator)

    def _update_tessellation(self):
        text = self._ui.lineEditTessellationDivisions.text()
        divisions_list = [int(x.strip()) for x in text.split(',')]
        self._scene.set_tessellation_divisions(divisions_list)
