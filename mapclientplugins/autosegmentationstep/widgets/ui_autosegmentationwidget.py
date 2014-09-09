# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/autosegmentationwidget.ui'
#
# Created: Tue Jul  2 14:00:30 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AutoSegmentationWidget(object):
    def setupUi(self, AutoSegmentationWidget):
        AutoSegmentationWidget.setObjectName("AutoSegmentationWidget")
        AutoSegmentationWidget.resize(448, 352)
        self.verticalLayout = QtGui.QVBoxLayout(AutoSegmentationWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(AutoSegmentationWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.isoValueSlider = QtGui.QSlider(self.groupBox)
        self.isoValueSlider.setMaximum(99)
        self.isoValueSlider.setOrientation(QtCore.Qt.Vertical)
        self.isoValueSlider.setObjectName("isoValueSlider")
        self.horizontalLayout_2.addWidget(self.isoValueSlider)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.imagePlaneCheckBox = QtGui.QCheckBox(self.groupBox)
        self.imagePlaneCheckBox.setChecked(True)
        self.imagePlaneCheckBox.setObjectName("imagePlaneCheckBox")
        self.verticalLayout_2.addWidget(self.imagePlaneCheckBox)
        self.segmentationCheckBox = QtGui.QCheckBox(self.groupBox)
        self.segmentationCheckBox.setChecked(True)
        self.segmentationCheckBox.setObjectName("segmentationCheckBox")
        self.verticalLayout_2.addWidget(self.segmentationCheckBox)
        self.pointCloudCheckBox = QtGui.QCheckBox(self.groupBox)
        self.pointCloudCheckBox.setChecked(True)
        self.pointCloudCheckBox.setObjectName("pointCloudCheckBox")
        self.verticalLayout_2.addWidget(self.pointCloudCheckBox)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        self.zincSceneViewer = ZincScene(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.zincSceneViewer.sizePolicy().hasHeightForWidth())
        self.zincSceneViewer.setSizePolicy(sizePolicy)
        self.zincSceneViewer.setObjectName("zincSceneViewer")
        self.gridLayout.addWidget(self.zincSceneViewer, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.doneButton = QtGui.QPushButton(AutoSegmentationWidget)
        self.doneButton.setObjectName("doneButton")
        self.horizontalLayout.addWidget(self.doneButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AutoSegmentationWidget)
        QtCore.QMetaObject.connectSlotsByName(AutoSegmentationWidget)

    def retranslateUi(self, AutoSegmentationWidget):
        AutoSegmentationWidget.setWindowTitle(QtGui.QApplication.translate("AutoSegmentationWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("AutoSegmentationWidget", "Auto Segmentation Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.imagePlaneCheckBox.setText(QtGui.QApplication.translate("AutoSegmentationWidget", "Image Plane", None, QtGui.QApplication.UnicodeUTF8))
        self.segmentationCheckBox.setText(QtGui.QApplication.translate("AutoSegmentationWidget", "Segmentation", None, QtGui.QApplication.UnicodeUTF8))
        self.pointCloudCheckBox.setText(QtGui.QApplication.translate("AutoSegmentationWidget", "Point Cloud", None, QtGui.QApplication.UnicodeUTF8))
        self.doneButton.setText(QtGui.QApplication.translate("AutoSegmentationWidget", "&Done", None, QtGui.QApplication.UnicodeUTF8))

from autosegmentationstep.widgets.zinc_scene import ZincScene
