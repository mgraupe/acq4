# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'acq4/analysis/old/UncagingControlTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UncagingControlWidget(object):
    def setupUi(self, UncagingControlWidget):
        UncagingControlWidget.setObjectName("UncagingControlWidget")
        UncagingControlWidget.resize(442, 354)
        self.gridLayout_4 = QtWidgets.QGridLayout(UncagingControlWidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(UncagingControlWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.thresholdSpin = QtWidgets.QDoubleSpinBox(UncagingControlWidget)
        self.thresholdSpin.setObjectName("thresholdSpin")
        self.gridLayout.addWidget(self.thresholdSpin, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(UncagingControlWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.directTimeSpin = QtWidgets.QDoubleSpinBox(UncagingControlWidget)
        self.directTimeSpin.setObjectName("directTimeSpin")
        self.gridLayout.addWidget(self.directTimeSpin, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(UncagingControlWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.poststimTimeSpin = QtWidgets.QDoubleSpinBox(UncagingControlWidget)
        self.poststimTimeSpin.setObjectName("poststimTimeSpin")
        self.gridLayout.addWidget(self.poststimTimeSpin, 2, 1, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(UncagingControlWidget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gradientRadio = QtWidgets.QRadioButton(self.groupBox_2)
        self.gradientRadio.setObjectName("gradientRadio")
        self.gridLayout_3.addWidget(self.gradientRadio, 0, 0, 1, 2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.colorSpin1 = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.colorSpin1.setObjectName("colorSpin1")
        self.horizontalLayout_2.addWidget(self.colorSpin1)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 1, 0, 1, 2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.colorSpin3 = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.colorSpin3.setMaximum(100.0)
        self.colorSpin3.setObjectName("colorSpin3")
        self.horizontalLayout_3.addWidget(self.colorSpin3)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 2, 0, 1, 2)
        self.gradientWidget = GradientWidget(self.groupBox_2)
        self.gradientWidget.setObjectName("gradientWidget")
        self.gridLayout_3.addWidget(self.gradientWidget, 3, 0, 2, 2)
        self.rgbRadio = QtWidgets.QRadioButton(self.groupBox_2)
        self.rgbRadio.setObjectName("rgbRadio")
        self.gridLayout_3.addWidget(self.rgbRadio, 5, 0, 1, 2)
        self.colorTracesCheck = QtWidgets.QCheckBox(self.groupBox_2)
        self.colorTracesCheck.setObjectName("colorTracesCheck")
        self.gridLayout_3.addWidget(self.colorTracesCheck, 7, 0, 1, 2)
        self.svgCheck = QtWidgets.QCheckBox(self.groupBox_2)
        self.svgCheck.setObjectName("svgCheck")
        self.gridLayout_3.addWidget(self.svgCheck, 8, 0, 1, 2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_4.addWidget(self.label_6)
        self.lowClipSpin = QtWidgets.QSpinBox(self.groupBox_2)
        self.lowClipSpin.setObjectName("lowClipSpin")
        self.horizontalLayout_4.addWidget(self.lowClipSpin)
        self.highClipSpin = QtWidgets.QSpinBox(self.groupBox_2)
        self.highClipSpin.setObjectName("highClipSpin")
        self.horizontalLayout_4.addWidget(self.highClipSpin)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 9, 0, 1, 2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_5.addWidget(self.label_7)
        self.downsampleSpin = QtWidgets.QSpinBox(self.groupBox_2)
        self.downsampleSpin.setObjectName("downsampleSpin")
        self.horizontalLayout_5.addWidget(self.downsampleSpin)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 10, 0, 1, 2)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.gridLayout_4.addWidget(self.groupBox_4, 0, 1, 2, 1)
        self.groupBox = QtWidgets.QGroupBox(UncagingControlWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.eventFindRadio = QtWidgets.QRadioButton(self.groupBox)
        self.eventFindRadio.setObjectName("eventFindRadio")
        self.gridLayout_2.addWidget(self.eventFindRadio, 0, 0, 1, 1)
        self.chargeTransferRadio = QtWidgets.QRadioButton(self.groupBox)
        self.chargeTransferRadio.setObjectName("chargeTransferRadio")
        self.gridLayout_2.addWidget(self.chargeTransferRadio, 1, 0, 1, 1)
        self.useSpontActCheck = QtWidgets.QCheckBox(self.groupBox)
        self.useSpontActCheck.setObjectName("useSpontActCheck")
        self.gridLayout_2.addWidget(self.useSpontActCheck, 2, 0, 1, 1)
        self.medianCheck = QtWidgets.QCheckBox(self.groupBox)
        self.medianCheck.setObjectName("medianCheck")
        self.gridLayout_2.addWidget(self.medianCheck, 3, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 1, 0, 1, 1)
        self.recolorBtn = QtWidgets.QPushButton(UncagingControlWidget)
        self.recolorBtn.setObjectName("recolorBtn")
        self.gridLayout_4.addWidget(self.recolorBtn, 2, 0, 1, 2)

        self.retranslateUi(UncagingControlWidget)
        Qt.QMetaObject.connectSlotsByName(UncagingControlWidget)

    def retranslateUi(self, UncagingControlWidget):
        _translate = Qt.QCoreApplication.translate
        UncagingControlWidget.setWindowTitle(_translate("UncagingControlWidget", "Form"))
        self.label.setText(_translate("UncagingControlWidget", "Noise Threshold"))
        self.label_3.setText(_translate("UncagingControlWidget", "Direct Time"))
        self.label_2.setText(_translate("UncagingControlWidget", "Post-Stim. Time"))
        self.groupBox_4.setTitle(_translate("UncagingControlWidget", "Coloring Scheme:"))
        self.gradientRadio.setText(_translate("UncagingControlWidget", "Gradient"))
        self.label_4.setText(_translate("UncagingControlWidget", "Low % Cutoff"))
        self.label_5.setText(_translate("UncagingControlWidget", "High % Cutoff"))
        self.rgbRadio.setText(_translate("UncagingControlWidget", "RGB"))
        self.colorTracesCheck.setText(_translate("UncagingControlWidget", "Color Traces by Laser Power"))
        self.svgCheck.setText(_translate("UncagingControlWidget", "Prepare for SVG"))
        self.label_6.setText(_translate("UncagingControlWidget", "Clip:"))
        self.label_7.setText(_translate("UncagingControlWidget", "Downsample:"))
        self.groupBox.setTitle(_translate("UncagingControlWidget", "Analysis Method:"))
        self.eventFindRadio.setText(_translate("UncagingControlWidget", "Event Finding"))
        self.chargeTransferRadio.setText(_translate("UncagingControlWidget", "Total Charge Transfer"))
        self.useSpontActCheck.setText(_translate("UncagingControlWidget", "Use Spont. Activity"))
        self.medianCheck.setText(_translate("UncagingControlWidget", "Use Median"))
        self.recolorBtn.setText(_translate("UncagingControlWidget", "Re-Color"))

from acq4.pyqtgraph.GradientWidget import GradientWidget