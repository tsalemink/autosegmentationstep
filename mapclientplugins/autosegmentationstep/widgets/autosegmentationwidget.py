"""
Created: April, 2023

@author: tsalemink
"""
from PySide6 import QtWidgets

from opencmiss.zincwidgets.handlers.scenemanipulation import SceneManipulation

from mapclientplugins.autosegmentationstep.model.autosegmentationmodel import AutoSegmentationModel
from mapclientplugins.autosegmentationstep.scene.autosegmentationscene import AutoSegmentationScene
from mapclientplugins.autosegmentationstep.widgets.ui_autosegmentationwidget import Ui_AutoSegmentationWidget


class AutoSegmentationWidget(QtWidgets.QWidget):
    """
    About dialog to display program about information.
    """

    def __init__(self, image_data_location, parent=None):
        """
        Constructor
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_AutoSegmentationWidget()
        self._ui.setupUi(self)

        self._model = AutoSegmentationModel(image_data_location)
        self._scene = AutoSegmentationScene(self._model)
        self._view = self._ui.zincWidget

        self._view.set_context(self._model.get_context())
        self._view.register_handler(SceneManipulation())

        self._make_connections()

    def _make_connections(self):
        self._ui.isoValueSlider.valueChanged.connect(self._scene.set_slider_value)
        self._ui.segmentationValueSlider.valueChanged.connect(self._scene.set_segmentation_value)
        self._ui.imagePlaneCheckBox.stateChanged.connect(self._scene.set_image_plane_visibility)
        self._ui.segmentationCheckBox.stateChanged.connect(self._scene.set_segmentation_visibility)
        self._ui.pointCloudCheckBox.stateChanged.connect(self._scene.set_point_cloud_visibility)
        self._ui.generatePointsButton.clicked.connect(self._scene.generate_points)

    def register_done_execution(self, callback):
        self._ui.doneButton.clicked.connect(callback)

    def get_point_cloud(self):
        return self._model.get_point_cloud()
