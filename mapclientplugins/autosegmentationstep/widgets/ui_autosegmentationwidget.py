# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'autosegmentationwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)

from mapclientplugins.autosegmentationstep.widgets.zincautosegmentationwidget import ZincAutoSegmentationWidget

class Ui_AutoSegmentationWidget(object):
    def setupUi(self, AutoSegmentationWidget):
        if not AutoSegmentationWidget.objectName():
            AutoSegmentationWidget.setObjectName(u"AutoSegmentationWidget")
        AutoSegmentationWidget.resize(820, 659)
        self.verticalLayout = QVBoxLayout(AutoSegmentationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(AutoSegmentationWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
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
        self.verticalLayout_5.setContentsMargins(10, -1, 10, -1)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
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

        self.isoValueLineEdit = QLineEdit(self.groupBox)
        self.isoValueLineEdit.setObjectName(u"isoValueLineEdit")
        self.isoValueLineEdit.setReadOnly(True)

        self.verticalLayout_5.addWidget(self.isoValueLineEdit)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setMinimumSize(QSize(100, 26))
        self.label_2.setMaximumSize(QSize(100, 26))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.label_2)

        self.segmentationValueSlider = QSlider(self.groupBox)
        self.segmentationValueSlider.setObjectName(u"segmentationValueSlider")
        self.segmentationValueSlider.setMaximum(10000)
        self.segmentationValueSlider.setOrientation(Qt.Vertical)

        self.verticalLayout_4.addWidget(self.segmentationValueSlider, 0, Qt.AlignHCenter)

        self.segmentationValueLineEdit = QLineEdit(self.groupBox)
        self.segmentationValueLineEdit.setObjectName(u"segmentationValueLineEdit")
        self.segmentationValueLineEdit.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.segmentationValueLineEdit)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.groupBoxImage = QGroupBox(self.groupBox)
        self.groupBoxImage.setObjectName(u"groupBoxImage")
        self.formLayout_2 = QFormLayout(self.groupBoxImage)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_7 = QLabel(self.groupBoxImage)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_7)

        self.imagePixelOutputLabel = QLabel(self.groupBoxImage)
        self.imagePixelOutputLabel.setObjectName(u"imagePixelOutputLabel")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.imagePixelOutputLabel)

        self.overrideScalingCheckBox = QCheckBox(self.groupBoxImage)
        self.overrideScalingCheckBox.setObjectName(u"overrideScalingCheckBox")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.overrideScalingCheckBox)

        self.scalingLineEdit = QLineEdit(self.groupBoxImage)
        self.scalingLineEdit.setObjectName(u"scalingLineEdit")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.scalingLineEdit)

        self.label_6 = QLabel(self.groupBoxImage)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_6)


        self.verticalLayout_3.addWidget(self.groupBoxImage)

        self.groupBoxSegmentation = QGroupBox(self.groupBox)
        self.groupBoxSegmentation.setObjectName(u"groupBoxSegmentation")
        self.formLayout = QFormLayout(self.groupBoxSegmentation)
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(self.groupBoxSegmentation)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_3)

        self.segmentationAlphaDoubleSpinBox = QDoubleSpinBox(self.groupBoxSegmentation)
        self.segmentationAlphaDoubleSpinBox.setObjectName(u"segmentationAlphaDoubleSpinBox")
        self.segmentationAlphaDoubleSpinBox.setDecimals(3)
        self.segmentationAlphaDoubleSpinBox.setMaximum(1.000000000000000)
        self.segmentationAlphaDoubleSpinBox.setSingleStep(0.010000000000000)
        self.segmentationAlphaDoubleSpinBox.setValue(1.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.segmentationAlphaDoubleSpinBox)

        self.allowHighTessellationsCheckBox = QCheckBox(self.groupBoxSegmentation)
        self.allowHighTessellationsCheckBox.setObjectName(u"allowHighTessellationsCheckBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.allowHighTessellationsCheckBox)

        self.label_4 = QLabel(self.groupBoxSegmentation)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.tessellationDivisionsLineEdit = QLineEdit(self.groupBoxSegmentation)
        self.tessellationDivisionsLineEdit.setObjectName(u"tessellationDivisionsLineEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.tessellationDivisionsLineEdit)

        self.label_5 = QLabel(self.groupBoxSegmentation)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.pointDensityLineEdit = QLineEdit(self.groupBoxSegmentation)
        self.pointDensityLineEdit.setObjectName(u"pointDensityLineEdit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.pointDensityLineEdit)

        self.label_8 = QLabel(self.groupBoxSegmentation)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_8)

        self.pointSizeLineEdit = QLineEdit(self.groupBoxSegmentation)
        self.pointSizeLineEdit.setObjectName(u"pointSizeLineEdit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.pointSizeLineEdit)


        self.verticalLayout_3.addWidget(self.groupBoxSegmentation)

        self.groupBoxVisibility = QGroupBox(self.groupBox)
        self.groupBoxVisibility.setObjectName(u"groupBoxVisibility")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxVisibility)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.imagePlaneCheckBox = QCheckBox(self.groupBoxVisibility)
        self.imagePlaneCheckBox.setObjectName(u"imagePlaneCheckBox")
        self.imagePlaneCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.imagePlaneCheckBox)

        self.segmentationCheckBox = QCheckBox(self.groupBoxVisibility)
        self.segmentationCheckBox.setObjectName(u"segmentationCheckBox")
        self.segmentationCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.segmentationCheckBox)

        self.pointCloudCheckBox = QCheckBox(self.groupBoxVisibility)
        self.pointCloudCheckBox.setObjectName(u"pointCloudCheckBox")
        self.pointCloudCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.pointCloudCheckBox)

        self.outlineCheckBox = QCheckBox(self.groupBoxVisibility)
        self.outlineCheckBox.setObjectName(u"outlineCheckBox")
        self.outlineCheckBox.setChecked(True)

        self.verticalLayout_2.addWidget(self.outlineCheckBox)


        self.verticalLayout_3.addWidget(self.groupBoxVisibility)

        self.groupBoxDetectionPlane = QGroupBox(self.groupBox)
        self.groupBoxDetectionPlane.setObjectName(u"groupBoxDetectionPlane")
        self.gridLayout = QGridLayout(self.groupBoxDetectionPlane)
        self.gridLayout.setObjectName(u"gridLayout")
        self.radioButtonToggleDetection = QRadioButton(self.groupBoxDetectionPlane)
        self.radioButtonToggleDetection.setObjectName(u"radioButtonToggleDetection")

        self.gridLayout.addWidget(self.radioButtonToggleDetection, 0, 0, 1, 1)

        self.label_10 = QLabel(self.groupBoxDetectionPlane)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 1, 0, 1, 1)

        self.segmentationMeshAlphaDoubleSpinBox = QDoubleSpinBox(self.groupBoxDetectionPlane)
        self.segmentationMeshAlphaDoubleSpinBox.setObjectName(u"segmentationMeshAlphaDoubleSpinBox")
        self.segmentationMeshAlphaDoubleSpinBox.setDecimals(3)
        self.segmentationMeshAlphaDoubleSpinBox.setMaximum(1.000000000000000)
        self.segmentationMeshAlphaDoubleSpinBox.setSingleStep(0.010000000000000)
        self.segmentationMeshAlphaDoubleSpinBox.setValue(1.000000000000000)

        self.gridLayout.addWidget(self.segmentationMeshAlphaDoubleSpinBox, 1, 1, 1, 1)

        self.label_9 = QLabel(self.groupBoxDetectionPlane)
        self.label_9.setObjectName(u"label_9")
        sizePolicy3 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.label_9, 2, 0, 1, 1)

        self.detectionPlaneAlphaDoubleSpinBox = QDoubleSpinBox(self.groupBoxDetectionPlane)
        self.detectionPlaneAlphaDoubleSpinBox.setObjectName(u"detectionPlaneAlphaDoubleSpinBox")
        self.detectionPlaneAlphaDoubleSpinBox.setDecimals(3)
        self.detectionPlaneAlphaDoubleSpinBox.setMaximum(1.000000000000000)
        self.detectionPlaneAlphaDoubleSpinBox.setSingleStep(0.010000000000000)
        self.detectionPlaneAlphaDoubleSpinBox.setValue(1.000000000000000)

        self.gridLayout.addWidget(self.detectionPlaneAlphaDoubleSpinBox, 2, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBoxDetectionPlane)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.zincWidget = ZincAutoSegmentationWidget(self.groupBox)
        self.zincWidget.setObjectName(u"zincWidget")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.zincWidget.sizePolicy().hasHeightForWidth())
        self.zincWidget.setSizePolicy(sizePolicy4)

        self.horizontalLayout_3.addWidget(self.zincWidget)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.generatePointsButton = QPushButton(AutoSegmentationWidget)
        self.generatePointsButton.setObjectName(u"generatePointsButton")

        self.horizontalLayout.addWidget(self.generatePointsButton)

        self.histogramPushButton = QPushButton(AutoSegmentationWidget)
        self.histogramPushButton.setObjectName(u"histogramPushButton")

        self.horizontalLayout.addWidget(self.histogramPushButton)

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
        AutoSegmentationWidget.setWindowTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Auto Segmentation", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Auto Segmentation Viewer", None))
        self.label.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Image Plane Level", None))
        self.label_2.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Segmentation Contour Threshold", None))
        self.groupBoxImage.setTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Image", None))
        self.label_7.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Dimensions:", None))
        self.imagePixelOutputLabel.setText(QCoreApplication.translate("AutoSegmentationWidget", u"AxBxC px", None))
        self.overrideScalingCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Override pre-dertermined scaling", None))
        self.label_6.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Scaling:", None))
        self.groupBoxSegmentation.setTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Segmentation", None))
        self.label_3.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Contour Alpha:", None))
#if QT_CONFIG(tooltip)
        self.allowHighTessellationsCheckBox.setToolTip(QCoreApplication.translate("AutoSegmentationWidget", u"High tessellations are turned off by default because it may take the contour calcuation en exceedingly long time", None))
#endif // QT_CONFIG(tooltip)
        self.allowHighTessellationsCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Allow high tessellations", None))
        self.label_4.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Tessellation Divisions:", None))
        self.tessellationDivisionsLineEdit.setText("")
        self.label_5.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Point Density:", None))
        self.label_8.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Point Size:", None))
        self.groupBoxVisibility.setTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Visibility", None))
        self.imagePlaneCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Image Plane", None))
        self.segmentationCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Segmentation", None))
        self.pointCloudCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Point Cloud", None))
        self.outlineCheckBox.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Outline", None))
        self.groupBoxDetectionPlane.setTitle(QCoreApplication.translate("AutoSegmentationWidget", u"Detection Mode", None))
        self.radioButtonToggleDetection.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Toggle On", None))
        self.label_10.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Mesh Alpha", None))
        self.label_9.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Plane Alpha:", None))
        self.generatePointsButton.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Generate Points", None))
        self.histogramPushButton.setText(QCoreApplication.translate("AutoSegmentationWidget", u"Show Histogram", None))
        self.doneButton.setText(QCoreApplication.translate("AutoSegmentationWidget", u"&Done", None))
    # retranslateUi

