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
import os

from PySide6 import QtGui

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint
from mapclientplugins.autosegmentationstep.widgets.autosegmentationwidget import AutoSegmentationWidget


class AutoSegmentationStep(WorkflowStepMountPoint):
    def __init__(self, location):
        super(AutoSegmentationStep, self).__init__('Automatic Segmenter', location)
        self._configured = True
        self._category = 'Segmentation'
        self._icon = QtGui.QImage(':/autosegmentation/images/autoseg.png')
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#images'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        self.addPort([('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#exf_file'),
                      ('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location')
                      ])
        self._config = {
            'identifier': ''
        }

        self._widget = None
        self._input_image_data = None

    def configure(self):
        return self._configured

    def getIdentifier(self):
        return self._config['identifier']

    def setIdentifier(self, identifier):
        self._config['identifier'] = identifier

    def serialize(self):
        pass

    def deserialize(self, string):
        pass

    def execute(self):
        if not self._widget:
            self._widget = AutoSegmentationWidget(self._input_image_data)
            self._widget.set_location(os.path.join(self._location, self._config['identifier']))
            self._widget.register_done_execution(self._doneExecution)

        self._widget.load_settings()
        self._setCurrentWidget(self._widget)

    def setPortData(self, port_id, data_in):
        self._input_image_data = data_in

    def getPortData(self, index):
        if index == 2:
            return self._widget.get_segmentation_graphics_filename()

        return self._widget.get_output_filename()
