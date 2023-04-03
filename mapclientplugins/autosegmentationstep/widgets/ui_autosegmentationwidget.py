# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'autosegmentationwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)

from mapclientplugins.autosegmentationstep.widgets.zinc_scene import ZincScene

class Ui_AutoSegmentationWidget(object):
    def setupUi(self, AutoSegmentationWidget):
        if not AutoSegmentationWidget.objectName():
            AutoSegmentationWidget.setObjectName(u"AutoSegmentationWidget")
        AutoSegmentationWidget.resize(448, 352)
        self.verticalLayout = QVBoxLayout(AutoSegmentationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(AutoSegmentationWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.zincSceneViewer = ZincScene(self.groupBox)
        self.zincSceneViewer.setObjectName(u"zincSceneViewer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.zincSceneViewer.sizePolicy().hasHeightForWidth())
        self.zincSceneViewer.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.zincSceneViewer, 0, 1, 1, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_5.setContentsMargins(5, -1, 5, -1)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)
        self.label.setMinimumSize(QSize(80, 26))
        self.label.setMaximumSize(QSize(80, 26))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.verticalLayout_5.addWidget(self.label)

        self.isoValueSlider = QSlider(self.groupBox)
        self.isoValueSlider.setObjectName(u"isoValueSlider")
        self.isoValueSlider.setMaximum(99)
        self.isoValueSlider.setOrientation(Qt.Vertical)

        self.verticalLayout_5.addWidget(self.isoValueSlider, 0, Qt.AlignHCenter)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)
        self.label_2.setMinimumSize(QSize(90, 26))
        self.label_2.setMaximumSize(QSize(90, 26))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.label_2)

        self.segmentationValueSlider = QSlider(self.groupBox)
        self.segmentationValueSlider.setObjectName(u"segmentationValueSlider")
        self.segmentationValueSlider.setMaximum(10000)
        self.segmentationValueSlider.setOrientation(Qt.Vertical)

        self.verticalLayout_4.addWidget(self.segmentationValueSlider, 0, Qt.AlignHCenter)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.imagePlaneCheckBox = QCheckBox(self.groupBox)
        self.imagePlaneCheckBox.setObjectName(u"imagePlaneCheckBox")
        self.imagePlaneCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.imagePlaneCheckBox)

        self.segmentationCheckBox = QCheckBox(self.groupBox)
        self.segmentationCheckBox.setObjectName(u"segmentationCheckBox")
        self.segmentationCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.segmentationCheckBox)

        self.pointCloudCheckBox = QCheckBox(self.groupBox)
        self.pointCloudCheckBox.setObjectName(u"pointCloudCheckBox")
        self.pointCloudCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.pointCloudCheckBox)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)


        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.doneButton = QPushButton(AutoSegmentationWidget)
        self.doneButton.setObjectName(u"doneButton")

        self.horizontalLayout.addWidget(self.doneButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(AutoSegmentationWidget)

        QMetaObject.connectSlotsByName(AutoSegmentationWidget)
    # setupUi

    def retranslateUi(self, AutoSegmentationWidget):
        AutoSegmentationWidget.setWindowTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Auto Segmentation Viewer", None))
        self.label.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Image Plane Level", None))
        self.label_2.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Segmentation Contour Threshold", None))
        self.imagePlaneCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Image Plane", None))
        self.segmentationCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Segmentation", None))
        self.pointCloudCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Point Cloud", None))
        self.doneButton.setText(QCoreApplication.translate("AutoSegmentationWidget", u"&Done", None))
    # retranslateUi

