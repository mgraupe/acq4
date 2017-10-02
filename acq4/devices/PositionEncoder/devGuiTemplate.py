# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\devGuiTemplate.ui'
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

class Ui_encoderDevGui(object):
    def setupUi(self, encoderDevGui):
        encoderDevGui.setObjectName(_fromUtf8("encoderDevGui"))
        encoderDevGui.resize(310, 176)
        self.gridLayout = QtGui.QGridLayout(encoderDevGui)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(encoderDevGui)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(encoderDevGui)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(encoderDevGui)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.UnitLabel = QtGui.QLabel(encoderDevGui)
        self.UnitLabel.setText(_fromUtf8(""))
        self.UnitLabel.setObjectName(_fromUtf8("UnitLabel"))
        self.gridLayout.addWidget(self.UnitLabel, 1, 3, 1, 1)
        self.ResolutionLabel = QtGui.QLabel(encoderDevGui)
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.ResolutionLabel.setFont(font)
        self.ResolutionLabel.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.ResolutionLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.ResolutionLabel.setText(_fromUtf8(""))
        self.ResolutionLabel.setObjectName(_fromUtf8("ResolutionLabel"))
        self.gridLayout.addWidget(self.ResolutionLabel, 1, 1, 1, 1)
        self.TypeLabel = QtGui.QLabel(encoderDevGui)
        self.TypeLabel.setText(_fromUtf8(""))
        self.TypeLabel.setObjectName(_fromUtf8("TypeLabel"))
        self.gridLayout.addWidget(self.TypeLabel, 0, 1, 1, 3)
        self.gridGroupBox = QtGui.QGroupBox(encoderDevGui)
        self.gridGroupBox.setObjectName(_fromUtf8("gridGroupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridGroupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(self.gridGroupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.toggleCounterBtn = QtGui.QPushButton(self.gridGroupBox)
        self.toggleCounterBtn.setCheckable(True)
        self.toggleCounterBtn.setObjectName(_fromUtf8("toggleCounterBtn"))
        self.gridLayout_2.addWidget(self.toggleCounterBtn, 1, 0, 1, 3)
        self.counterLabel = QtGui.QLabel(self.gridGroupBox)
        self.counterLabel.setText(_fromUtf8(""))
        self.counterLabel.setObjectName(_fromUtf8("counterLabel"))
        self.gridLayout_2.addWidget(self.counterLabel, 2, 1, 1, 1)
        self.distanceTravelledUnit = QtGui.QLabel(self.gridGroupBox)
        self.distanceTravelledUnit.setObjectName(_fromUtf8("distanceTravelledUnit"))
        self.gridLayout_2.addWidget(self.distanceTravelledUnit, 2, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.gridGroupBox)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_2.addWidget(self.label_7, 3, 2, 1, 1)
        self.label_5 = QtGui.QLabel(self.gridGroupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 1)
        self.timeSpentLabel = QtGui.QLabel(self.gridGroupBox)
        self.timeSpentLabel.setText(_fromUtf8(""))
        self.timeSpentLabel.setObjectName(_fromUtf8("timeSpentLabel"))
        self.gridLayout_2.addWidget(self.timeSpentLabel, 3, 1, 1, 1)
        self.savePositionBtn = QtGui.QPushButton(self.gridGroupBox)
        self.savePositionBtn.setEnabled(False)
        self.savePositionBtn.setObjectName(_fromUtf8("savePositionBtn"))
        self.gridLayout_2.addWidget(self.savePositionBtn, 4, 0, 1, 3)
        self.label_6 = QtGui.QLabel(self.gridGroupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)
        self.ActivityLabel = QtGui.QLabel(self.gridGroupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ActivityLabel.setFont(font)
        self.ActivityLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ActivityLabel.setObjectName(_fromUtf8("ActivityLabel"))
        self.gridLayout_2.addWidget(self.ActivityLabel, 0, 1, 1, 2)
        self.gridLayout.addWidget(self.gridGroupBox, 6, 0, 2, 4)

        self.retranslateUi(encoderDevGui)
        QtCore.QMetaObject.connectSlotsByName(encoderDevGui)

    def retranslateUi(self, encoderDevGui):
        encoderDevGui.setWindowTitle(_translate("encoderDevGui", "Form", None))
        self.label.setText(_translate("encoderDevGui", "Encoder Type ", None))
        self.label_2.setText(_translate("encoderDevGui", "Encoder Resolution", None))
        self.label_4.setText(_translate("encoderDevGui", "pulses per", None))
        self.gridGroupBox.setTitle(_translate("encoderDevGui", "Activity", None))
        self.label_3.setText(_translate("encoderDevGui", "DistanceTravelled", None))
        self.toggleCounterBtn.setText(_translate("encoderDevGui", "Start Postion Counter", None))
        self.distanceTravelledUnit.setText(_translate("encoderDevGui", "TextLabel", None))
        self.label_7.setText(_translate("encoderDevGui", "sec", None))
        self.label_5.setText(_translate("encoderDevGui", "Time Spent", None))
        self.savePositionBtn.setText(_translate("encoderDevGui", "Save Positions", None))
        self.label_6.setText(_translate("encoderDevGui", "Currently", None))
        self.ActivityLabel.setText(_translate("encoderDevGui", "TextLabel", None))

