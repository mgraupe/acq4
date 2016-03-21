# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\devTemplate.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(695, 698)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setMargin(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.wavelengthGroup = QtGui.QGroupBox(Form)
        self.wavelengthGroup.setTitle(_fromUtf8(""))
        self.wavelengthGroup.setObjectName(_fromUtf8("wavelengthGroup"))
        self.gridLayout_5 = QtGui.QGridLayout(self.wavelengthGroup)
        self.gridLayout_5.setMargin(6)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_7 = QtGui.QLabel(self.wavelengthGroup)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_5.addWidget(self.label_7, 0, 0, 1, 1)
        self.wavelengthSpin = SpinBox(self.wavelengthGroup)
        self.wavelengthSpin.setSuffix(_fromUtf8(""))
        self.wavelengthSpin.setObjectName(_fromUtf8("wavelengthSpin"))
        self.gridLayout_5.addWidget(self.wavelengthSpin, 0, 1, 1, 1)
        self.wavelengthCombo = QtGui.QComboBox(self.wavelengthGroup)
        self.wavelengthCombo.setObjectName(_fromUtf8("wavelengthCombo"))
        self.wavelengthCombo.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.wavelengthCombo, 0, 2, 1, 1)
        self.GDDEnableCheck = QtGui.QCheckBox(self.wavelengthGroup)
        self.GDDEnableCheck.setObjectName(_fromUtf8("GDDEnableCheck"))
        self.gridLayout_5.addWidget(self.GDDEnableCheck, 1, 0, 1, 1)
        self.GDDSpin = QtGui.QSpinBox(self.wavelengthGroup)
        self.GDDSpin.setMaximum(32000)
        self.GDDSpin.setObjectName(_fromUtf8("GDDSpin"))
        self.gridLayout_5.addWidget(self.GDDSpin, 1, 1, 1, 1)
        self.GDDLimits = QtGui.QLabel(self.wavelengthGroup)
        self.GDDLimits.setObjectName(_fromUtf8("GDDLimits"))
        self.gridLayout_5.addWidget(self.GDDLimits, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.wavelengthGroup, 7, 0, 1, 3)
        self.powerGroup = QtGui.QGroupBox(Form)
        self.powerGroup.setTitle(_fromUtf8(""))
        self.powerGroup.setObjectName(_fromUtf8("powerGroup"))
        self.gridLayout_4 = QtGui.QGridLayout(self.powerGroup)
        self.gridLayout_4.setMargin(6)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_4 = QtGui.QLabel(self.powerGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_4.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.powerGroup)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_4.addWidget(self.label_8, 3, 0, 1, 1)
        self.outputPowerLabel = QtGui.QLabel(self.powerGroup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.outputPowerLabel.setFont(font)
        self.outputPowerLabel.setText(_fromUtf8(""))
        self.outputPowerLabel.setObjectName(_fromUtf8("outputPowerLabel"))
        self.gridLayout_4.addWidget(self.outputPowerLabel, 1, 1, 1, 1)
        self.samplePowerLabel = QtGui.QLabel(self.powerGroup)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.samplePowerLabel.setFont(font)
        self.samplePowerLabel.setText(_fromUtf8(""))
        self.samplePowerLabel.setObjectName(_fromUtf8("samplePowerLabel"))
        self.gridLayout_4.addWidget(self.samplePowerLabel, 3, 1, 1, 1)
        self.label_16 = QtGui.QLabel(self.powerGroup)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_4.addWidget(self.label_16, 0, 0, 1, 1)
        self.pumpPowerLabel = QtGui.QLabel(self.powerGroup)
        self.pumpPowerLabel.setText(_fromUtf8(""))
        self.pumpPowerLabel.setObjectName(_fromUtf8("pumpPowerLabel"))
        self.gridLayout_4.addWidget(self.pumpPowerLabel, 0, 1, 1, 1)
        self.subPowerGroup = QtGui.QGroupBox(self.powerGroup)
        self.subPowerGroup.setObjectName(_fromUtf8("subPowerGroup"))
        self.gridLayout_10 = QtGui.QGridLayout(self.subPowerGroup)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.expectedPowerSpin = SpinBox(self.subPowerGroup)
        self.expectedPowerSpin.setMinimumSize(QtCore.QSize(75, 0))
        self.expectedPowerSpin.setObjectName(_fromUtf8("expectedPowerSpin"))
        self.gridLayout_10.addWidget(self.expectedPowerSpin, 0, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.subPowerGroup)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_10.addWidget(self.label_5, 0, 0, 1, 1)
        self.powerAlertCheck = QtGui.QCheckBox(self.subPowerGroup)
        self.powerAlertCheck.setChecked(True)
        self.powerAlertCheck.setObjectName(_fromUtf8("powerAlertCheck"))
        self.gridLayout_10.addWidget(self.powerAlertCheck, 1, 0, 1, 1)
        self.toleranceSpin = SpinBox(self.subPowerGroup)
        self.toleranceSpin.setMinimumSize(QtCore.QSize(75, 0))
        self.toleranceSpin.setObjectName(_fromUtf8("toleranceSpin"))
        self.gridLayout_10.addWidget(self.toleranceSpin, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.subPowerGroup, 0, 2, 4, 1)
        self.energyCalcGroup = QtGui.QGroupBox(self.powerGroup)
        self.energyCalcGroup.setObjectName(_fromUtf8("energyCalcGroup"))
        self.verticalLayout = QtGui.QVBoxLayout(self.energyCalcGroup)
        self.verticalLayout.setContentsMargins(-1, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.currentPowerRadio = QtGui.QRadioButton(self.energyCalcGroup)
        self.currentPowerRadio.setObjectName(_fromUtf8("currentPowerRadio"))
        self.verticalLayout.addWidget(self.currentPowerRadio)
        self.expectedPowerRadio = QtGui.QRadioButton(self.energyCalcGroup)
        self.expectedPowerRadio.setChecked(True)
        self.expectedPowerRadio.setObjectName(_fromUtf8("expectedPowerRadio"))
        self.verticalLayout.addWidget(self.expectedPowerRadio)
        self.gridLayout_4.addWidget(self.energyCalcGroup, 0, 5, 4, 1)
        self.gridLayout.addWidget(self.powerGroup, 2, 0, 1, 3)
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.calibrationList = QtGui.QTreeWidget(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.calibrationList.setFont(font)
        self.calibrationList.setRootIsDecorated(False)
        self.calibrationList.setItemsExpandable(False)
        self.calibrationList.setObjectName(_fromUtf8("calibrationList"))
        self.calibrationList.header().setStretchLastSection(True)
        self.gridLayout_6.addWidget(self.calibrationList, 0, 0, 1, 5)
        self.groupBox = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_3.setMargin(6)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setHorizontalSpacing(6)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scanLabel = QtGui.QLabel(self.groupBox)
        self.scanLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.scanLabel.setObjectName(_fromUtf8("scanLabel"))
        self.gridLayout_2.addWidget(self.scanLabel, 1, 3, 1, 1)
        self.measurementSpin = SpinBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.measurementSpin.sizePolicy().hasHeightForWidth())
        self.measurementSpin.setSizePolicy(sizePolicy)
        self.measurementSpin.setMinimum(0.0)
        self.measurementSpin.setMaximum(100.0)
        self.measurementSpin.setProperty("value", 1.0)
        self.measurementSpin.setObjectName(_fromUtf8("measurementSpin"))
        self.gridLayout_2.addWidget(self.measurementSpin, 1, 4, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 2, 3, 1, 1)
        self.settlingSpin = SpinBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settlingSpin.sizePolicy().hasHeightForWidth())
        self.settlingSpin.setSizePolicy(sizePolicy)
        self.settlingSpin.setObjectName(_fromUtf8("settlingSpin"))
        self.gridLayout_2.addWidget(self.settlingSpin, 2, 4, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.meterCombo = InterfaceCombo(self.groupBox)
        self.meterCombo.setObjectName(_fromUtf8("meterCombo"))
        self.gridLayout_2.addWidget(self.meterCombo, 1, 1, 1, 1)
        self.label_12 = QtGui.QLabel(self.groupBox)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_2.addWidget(self.label_12, 2, 0, 1, 1)
        self.channelCombo = QtGui.QComboBox(self.groupBox)
        self.channelCombo.setObjectName(_fromUtf8("channelCombo"))
        self.gridLayout_2.addWidget(self.channelCombo, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.pCellGroup = QtGui.QGroupBox(self.groupBox)
        self.pCellGroup.setAlignment(QtCore.Qt.AlignCenter)
        self.pCellGroup.setObjectName(_fromUtf8("pCellGroup"))
        self.gridLayout_8 = QtGui.QGridLayout(self.pCellGroup)
        self.gridLayout_8.setMargin(6)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setVerticalSpacing(0)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.label_9 = QtGui.QLabel(self.pCellGroup)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_7.addWidget(self.label_9, 0, 0, 1, 1)
        self.minVSpin = SpinBox(self.pCellGroup)
        self.minVSpin.setMinimum(-99.0)
        self.minVSpin.setSingleStep(0.01)
        self.minVSpin.setProperty("value", -0.2)
        self.minVSpin.setObjectName(_fromUtf8("minVSpin"))
        self.gridLayout_7.addWidget(self.minVSpin, 0, 1, 1, 1)
        self.label_11 = QtGui.QLabel(self.pCellGroup)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_7.addWidget(self.label_11, 0, 2, 1, 1)
        self.stepsSpin = SpinBox(self.pCellGroup)
        self.stepsSpin.setDecimals(0)
        self.stepsSpin.setMinimum(10.0)
        self.stepsSpin.setMaximum(1000.0)
        self.stepsSpin.setProperty("value", 20.0)
        self.stepsSpin.setObjectName(_fromUtf8("stepsSpin"))
        self.gridLayout_7.addWidget(self.stepsSpin, 0, 3, 1, 1)
        self.label_10 = QtGui.QLabel(self.pCellGroup)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_7.addWidget(self.label_10, 2, 0, 1, 1)
        self.maxVSpin = SpinBox(self.pCellGroup)
        self.maxVSpin.setSingleStep(0.01)
        self.maxVSpin.setProperty("value", 1.2)
        self.maxVSpin.setObjectName(_fromUtf8("maxVSpin"))
        self.gridLayout_7.addWidget(self.maxVSpin, 2, 1, 1, 1)
        self.recalibratePCellCheck = QtGui.QCheckBox(self.pCellGroup)
        self.recalibratePCellCheck.setObjectName(_fromUtf8("recalibratePCellCheck"))
        self.gridLayout_7.addWidget(self.recalibratePCellCheck, 2, 3, 1, 1)
        self.gridLayout_8.addLayout(self.gridLayout_7, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.pCellGroup, 1, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox, 2, 0, 1, 5)
        self.deleteBtn = QtGui.QPushButton(self.groupBox_2)
        self.deleteBtn.setObjectName(_fromUtf8("deleteBtn"))
        self.gridLayout_6.addWidget(self.deleteBtn, 1, 4, 1, 1)
        self.calibrateBtn = QtGui.QPushButton(self.groupBox_2)
        self.calibrateBtn.setObjectName(_fromUtf8("calibrateBtn"))
        self.gridLayout_6.addWidget(self.calibrateBtn, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 8, 0, 1, 3)
        self.controlButtonGroup = QtGui.QGroupBox(Form)
        self.controlButtonGroup.setObjectName(_fromUtf8("controlButtonGroup"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.controlButtonGroup)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkPowerBtn = QtGui.QPushButton(self.controlButtonGroup)
        self.checkPowerBtn.setObjectName(_fromUtf8("checkPowerBtn"))
        self.horizontalLayout.addWidget(self.checkPowerBtn)
        self.shutterBtn = QtGui.QPushButton(self.controlButtonGroup)
        self.shutterBtn.setCheckable(True)
        self.shutterBtn.setObjectName(_fromUtf8("shutterBtn"))
        self.horizontalLayout.addWidget(self.shutterBtn)
        self.qSwitchBtn = QtGui.QPushButton(self.controlButtonGroup)
        self.qSwitchBtn.setCheckable(True)
        self.qSwitchBtn.setObjectName(_fromUtf8("qSwitchBtn"))
        self.horizontalLayout.addWidget(self.qSwitchBtn)
        self.gridLayout.addWidget(self.controlButtonGroup, 5, 0, 1, 3)
        self.maitaiControlGroup = QtGui.QGroupBox(Form)
        self.maitaiControlGroup.setObjectName(_fromUtf8("maitaiControlGroup"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.maitaiControlGroup)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.turnOnOffBtn = QtGui.QPushButton(self.maitaiControlGroup)
        self.turnOnOffBtn.setStyleSheet(_fromUtf8(""))
        self.turnOnOffBtn.setCheckable(True)
        self.turnOnOffBtn.setObjectName(_fromUtf8("turnOnOffBtn"))
        self.horizontalLayout_2.addWidget(self.turnOnOffBtn)
        self.InternalShutterBtn = QtGui.QPushButton(self.maitaiControlGroup)
        self.InternalShutterBtn.setCheckable(True)
        self.InternalShutterBtn.setObjectName(_fromUtf8("InternalShutterBtn"))
        self.horizontalLayout_2.addWidget(self.InternalShutterBtn)
        self.ExternalShutterBtn = QtGui.QPushButton(self.maitaiControlGroup)
        self.ExternalShutterBtn.setCheckable(True)
        self.ExternalShutterBtn.setObjectName(_fromUtf8("ExternalShutterBtn"))
        self.horizontalLayout_2.addWidget(self.ExternalShutterBtn)
        self.pushButton_2 = QtGui.QPushButton(self.maitaiControlGroup)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.gridLayout.addWidget(self.maitaiControlGroup, 0, 0, 1, 3)
        self.maitaiWavelengthGroup = QtGui.QGroupBox(Form)
        self.maitaiWavelengthGroup.setTitle(_fromUtf8(""))
        self.maitaiWavelengthGroup.setObjectName(_fromUtf8("maitaiWavelengthGroup"))
        self.gridLayout_9 = QtGui.QGridLayout(self.maitaiWavelengthGroup)
        self.gridLayout_9.setMargin(6)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.label_13 = QtGui.QLabel(self.maitaiWavelengthGroup)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_9.addWidget(self.label_13, 0, 0, 1, 1)
        self.wavelengthSpin_2 = SpinBox(self.maitaiWavelengthGroup)
        self.wavelengthSpin_2.setSuffix(_fromUtf8(""))
        self.wavelengthSpin_2.setObjectName(_fromUtf8("wavelengthSpin_2"))
        self.gridLayout_9.addWidget(self.wavelengthSpin_2, 0, 2, 1, 1)
        self.currentWaveLengthLabel = QtGui.QLabel(self.maitaiWavelengthGroup)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.currentWaveLengthLabel.setFont(font)
        self.currentWaveLengthLabel.setText(_fromUtf8(""))
        self.currentWaveLengthLabel.setObjectName(_fromUtf8("currentWaveLengthLabel"))
        self.gridLayout_9.addWidget(self.currentWaveLengthLabel, 1, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.maitaiWavelengthGroup)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_9.addWidget(self.label_2, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.maitaiWavelengthGroup, 4, 0, 1, 3)
        self.MaiTaiGroup = QtGui.QGroupBox(Form)
        self.MaiTaiGroup.setObjectName(_fromUtf8("MaiTaiGroup"))
        self.gridLayout_11 = QtGui.QGridLayout(self.MaiTaiGroup)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.relHumidityLabel = QtGui.QLabel(self.MaiTaiGroup)
        self.relHumidityLabel.setText(_fromUtf8(""))
        self.relHumidityLabel.setObjectName(_fromUtf8("relHumidityLabel"))
        self.gridLayout_11.addWidget(self.relHumidityLabel, 1, 1, 1, 1)
        self.label_14 = QtGui.QLabel(self.MaiTaiGroup)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_11.addWidget(self.label_14, 1, 0, 1, 1)
        self.PulsingLabel = QtGui.QLabel(self.MaiTaiGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.PulsingLabel.setFont(font)
        self.PulsingLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.PulsingLabel.setObjectName(_fromUtf8("PulsingLabel"))
        self.gridLayout_11.addWidget(self.PulsingLabel, 0, 3, 1, 1)
        self.EmissionLabel = QtGui.QLabel(self.MaiTaiGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.EmissionLabel.setFont(font)
        self.EmissionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.EmissionLabel.setObjectName(_fromUtf8("EmissionLabel"))
        self.gridLayout_11.addWidget(self.EmissionLabel, 0, 0, 1, 1)
        self.InternalShutterLabel = QtGui.QLabel(self.MaiTaiGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.InternalShutterLabel.setFont(font)
        self.InternalShutterLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.InternalShutterLabel.setObjectName(_fromUtf8("InternalShutterLabel"))
        self.gridLayout_11.addWidget(self.InternalShutterLabel, 0, 1, 1, 1)
        self.label_17 = QtGui.QLabel(self.MaiTaiGroup)
        self.label_17.setText(_fromUtf8(""))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout_11.addWidget(self.label_17, 1, 3, 1, 1)
        self.ExternalShutterLabel = QtGui.QLabel(self.MaiTaiGroup)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ExternalShutterLabel.setFont(font)
        self.ExternalShutterLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ExternalShutterLabel.setObjectName(_fromUtf8("ExternalShutterLabel"))
        self.gridLayout_11.addWidget(self.ExternalShutterLabel, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.MaiTaiGroup, 1, 0, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_7.setText(_translate("Form", "Current Wavelength: ", None))
        self.wavelengthCombo.setItemText(0, _translate("Form", "Set wavelength for:", None))
        self.GDDEnableCheck.setText(_translate("Form", "GDD Enable", None))
        self.GDDLimits.setText(_translate("Form", "GDD Limits", None))
        self.label_4.setText(_translate("Form", "Current Output Power:", None))
        self.label_8.setText(_translate("Form", "Power at sample (calc.):", None))
        self.label_16.setText(_translate("Form", "Current Pump Power:", None))
        self.label_5.setText(_translate("Form", "Expected Output Power:", None))
        self.powerAlertCheck.setText(_translate("Form", "Alert me to power changes larger than:", None))
        self.energyCalcGroup.setTitle(_translate("Form", "For energy calculations use:", None))
        self.currentPowerRadio.setText(_translate("Form", "Current Power", None))
        self.expectedPowerRadio.setText(_translate("Form", "Expected Power", None))
        self.groupBox_2.setTitle(_translate("Form", "Power Calibration", None))
        self.calibrationList.headerItem().setText(0, _translate("Form", "Optics", None))
        self.calibrationList.headerItem().setText(1, _translate("Form", "Wavelength", None))
        self.calibrationList.headerItem().setText(2, _translate("Form", "Transmission", None))
        self.calibrationList.headerItem().setText(3, _translate("Form", "Power at Sample", None))
        self.calibrationList.headerItem().setText(4, _translate("Form", "Date", None))
        self.groupBox.setTitle(_translate("Form", "Calibration Parameters", None))
        self.scanLabel.setText(_translate("Form", "Measurement Duration", None))
        self.measurementSpin.setSuffix(_translate("Form", " s", None))
        self.label.setText(_translate("Form", "Settling Duration:", None))
        self.settlingSpin.setToolTip(_translate("Form", "Specify the time it takes for the selected power meter to settle on a value.", None))
        self.label_3.setText(_translate("Form", "Power Meter:", None))
        self.label_12.setText(_translate("Form", "Channel:", None))
        self.pCellGroup.setTitle(_translate("Form", "Pockel Cell Parameters", None))
        self.label_9.setText(_translate("Form", "Minimum Voltage:", None))
        self.minVSpin.setSuffix(_translate("Form", "V", None))
        self.label_11.setText(_translate("Form", "Number of Steps: ", None))
        self.label_10.setText(_translate("Form", "Maximum Voltage:", None))
        self.maxVSpin.setSuffix(_translate("Form", "V", None))
        self.recalibratePCellCheck.setText(_translate("Form", "Re-Calibrate Pockel Cell", None))
        self.deleteBtn.setText(_translate("Form", "Delete", None))
        self.calibrateBtn.setText(_translate("Form", "Calibrate", None))
        self.checkPowerBtn.setText(_translate("Form", "Check Power", None))
        self.shutterBtn.setText(_translate("Form", "Open Shutter", None))
        self.qSwitchBtn.setText(_translate("Form", "Turn On QSwitch", None))
        self.turnOnOffBtn.setText(_translate("Form", "Turn Laser On", None))
        self.InternalShutterBtn.setText(_translate("Form", "Open Laser Shutter", None))
        self.ExternalShutterBtn.setText(_translate("Form", "Open External Shutter", None))
        self.pushButton_2.setText(_translate("Form", "Alignment mode", None))
        self.label_13.setText(_translate("Form", "Set Wavelength: ", None))
        self.label_2.setText(_translate("Form", "Current Wavelength:", None))
        self.label_14.setText(_translate("Form", "relative Humidity:", None))
        self.PulsingLabel.setText(_translate("Form", "Not Pulsing", None))
        self.EmissionLabel.setText(_translate("Form", "Emission Off", None))
        self.InternalShutterLabel.setText(_translate("Form", "Laser Shutter Closed", None))
        self.ExternalShutterLabel.setText(_translate("Form", "External Shutter Closed", None))

from acq4.pyqtgraph import SpinBox
from acq4.util.InterfaceCombo import InterfaceCombo
