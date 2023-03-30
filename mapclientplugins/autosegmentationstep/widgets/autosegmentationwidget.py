"""
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland

This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
"""
from PySide6 import QtWidgets

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
        self._ui.zincSceneViewer.set_image_data_location(image_data_location)

        self._make_connections()

    def _make_connections(self):
        self._ui.isoValueSlider.valueChanged.connect(self._ui.zincSceneViewer.set_slider_value)
        self._ui.imagePlaneCheckBox.stateChanged.connect(self._ui.zincSceneViewer.set_image_plane_visibility)
        self._ui.segmentationCheckBox.stateChanged.connect(self._ui.zincSceneViewer.set_segmentation_visibility)
        self._ui.pointCloudCheckBox.stateChanged.connect(self._ui.zincSceneViewer.set_point_cloud_visibility)

    def register_done_execution(self, callback):
        self._ui.doneButton.clicked.connect(callback)

    def get_point_cloud(self):
        return self._ui.zincSceneViewer.get_point_cloud()
