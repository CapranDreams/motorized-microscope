import cv2
import time
import serial        # pip install pySerial
import io
import tkinter as tk
import os
import shutil
import re
import imutils
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import numpy as np
import serial.tools.list_ports
from skimage import io
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from threading import Thread
import argparse
from datetime import datetime, timedelta
from timeloop import Timeloop


print("keep this CMD window open while running script!")
print("------------------------------------------------------")
cwd = os.getcwd()
print("CWD:  " + str(cwd))

ser = serial.Serial()		#open serial port
ser.baudrate = 115200
class serial_port_list():
    portlist = serial.tools.list_ports.comports()
    
    def print_ports(self):
        for port, desc, hwid in sorted(self.portlist):
            print("{}: {} [{}]".format(port, desc, hwid))
        
    def update_ports(self):
        self.portlist = serial.tools.list_ports.comports()
        
    def get_port(self):
        return self.portlist
    
    def select_port(self):
        try:
            ser.close()
            ui.connected = False
        except:
            print("[no port currently open]")
    
        try:
            selected_comm = ui.comboBox_port.currentText()
            print("SELECTED COMM: {}".format(selected_comm))
            ser.port = selected_comm

            ser.open()
            time.sleep(0.05)

            #print(ser.readline())
            print(ser)
            ui.feedback("SUCCESS:  COMM OPEN")
            ui.connected = True
        except:
            print("FAILURE: Failed to connect to port, please try a different port")
            ui.connected = False

        
ports = serial_port_list()
#ports.print_ports()



class Ui_Form(object):
    feedback_string = " "
    step_size_um = 1
    num_pictures = 10
    settle_time_ms = 500
    usteps = 400
    step_dir = True
    position = 0
    connected = False
    
    
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(330, 440)
        font = QtGui.QFont()
        
        self.btn_up = QtWidgets.QPushButton(Form)
        self.btn_up.setGeometry(QtCore.QRect(10, 290, 101, 41))
        self.btn_up.setFont(font)
        self.btn_up.setStyleSheet("font-size:14px;")
        self.btn_up.setObjectName("btn_up")
        self.btn_up.clicked.connect(self.press_btn_up)
        
        self.textEdit_feedback = QtWidgets.QTextEdit(Form)
        self.textEdit_feedback.setGeometry(QtCore.QRect(120, 290, 201, 91))
        self.textEdit_feedback.setStyleSheet("font-size:9px;")
        self.textEdit_feedback.setObjectName("textEdit_feedback")
        self.btn_startFS = QtWidgets.QPushButton(Form)
        self.btn_startFS.setGeometry(QtCore.QRect(10, 390, 311, 41))
        self.btn_startFS.setFont(font)
        self.btn_startFS.setStyleSheet("font-size:14px;")
        self.btn_startFS.setObjectName("btn_startFS")
        self.btn_startFS.clicked.connect(self.run_sequence)
        
        self.btn_down = QtWidgets.QPushButton(Form)
        self.btn_down.setGeometry(QtCore.QRect(10, 340, 101, 41))
        self.btn_down.setFont(font)
        self.btn_down.setStyleSheet("font-size:14px;")
        self.btn_down.setObjectName("btn_down")
        self.btn_down.clicked.connect(self.press_btn_down)
        
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setGeometry(QtCore.QRect(120, 270, 191, 21))
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("font-size:9px;")
        self.label_6.setObjectName("label_6")
        
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 311, 251))
        self.tabWidget.setStyleSheet("font-size:10px;")
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setGeometry(QtCore.QRect(230, 20, 31, 21))
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        
        self.doubleSpinBox_numimages = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_numimages.setGeometry(QtCore.QRect(160, 50, 62, 22))
        self.doubleSpinBox_numimages.setProperty("value", 1)
        self.doubleSpinBox_numimages.setDecimals(0)
        self.doubleSpinBox_numimages.setMaximum(1000.0)
        self.doubleSpinBox_numimages.setObjectName("doubleSpinBox_numimages")
        self.doubleSpinBox_numimages.editingFinished.connect(self.update_vars)
        
        self.label_9 = QtWidgets.QLabel(self.tab)
        self.label_9.setGeometry(QtCore.QRect(230, 80, 31, 21))
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.tab)
        self.label_10.setGeometry(QtCore.QRect(20, 80, 131, 21))
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(40, 20, 111, 21))
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        
        self.doubleSpinBox_stabletime = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_stabletime.setGeometry(QtCore.QRect(160, 80, 62, 22))
        self.doubleSpinBox_stabletime.setDecimals(0)
        self.doubleSpinBox_stabletime.setMaximum(600000.0)
        self.doubleSpinBox_stabletime.setProperty("value", 100.0)
        self.doubleSpinBox_stabletime.setObjectName("doubleSpinBox_stabletime")
        self.doubleSpinBox_stabletime.editingFinished.connect(self.update_vars)
        
        self.doubleSpinBox_stepsize = QtWidgets.QDoubleSpinBox(self.tab)
        self.doubleSpinBox_stepsize.setGeometry(QtCore.QRect(160, 20, 62, 22))
        self.doubleSpinBox_stepsize.setDecimals(2)
        self.doubleSpinBox_stepsize.setMaximum(1000000.0)
        self.doubleSpinBox_stepsize.setProperty("value", 100.0)
        self.doubleSpinBox_stepsize.setObjectName("doubleSpinBox_stepsize")
        self.doubleSpinBox_stepsize.editingFinished.connect(self.update_vars)
        
        self.label_7 = QtWidgets.QLabel(self.tab)
        self.label_7.setGeometry(QtCore.QRect(40, 50, 111, 21))
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        
        self.groupBox_direction = QtWidgets.QGroupBox(self.tab)
        self.groupBox_direction.setGeometry(QtCore.QRect(150, 130, 91, 61))
        self.groupBox_direction.setObjectName("groupBox_direction")
        self.radioButton_up = QtWidgets.QRadioButton(self.groupBox_direction)
        self.radioButton_up.setGeometry(QtCore.QRect(13, 17, 71, 16))
        self.radioButton_up.setChecked(True)
        self.radioButton_up.setObjectName("radioButton_up")
        self.radioButton_down = QtWidgets.QRadioButton(self.groupBox_direction)
        self.radioButton_down.setGeometry(QtCore.QRect(13, 37, 71, 16))
        self.radioButton_down.setObjectName("radioButton_down")
        
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        
        self.label_11 = QtWidgets.QLabel(self.tab_2)
        self.label_11.setGeometry(QtCore.QRect(35, 40, 75, 25))
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        
        self.label_baud = QtWidgets.QLabel(self.tab_2)
        self.label_baud.setGeometry(QtCore.QRect(110, 70, 161, 25))
        self.label_baud.setFont(font)
        self.label_baud.setObjectName("label_baud")
        
        self.label_12 = QtWidgets.QLabel(self.tab_2)
        self.label_12.setGeometry(QtCore.QRect(35, 70, 75, 25))
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        
        self.btn_refresh = QtWidgets.QPushButton(self.tab_2)
        self.btn_refresh.setGeometry(QtCore.QRect(190, 40, 75, 25))
        self.btn_refresh.clicked.connect(self.refresh_comms_click)
        self.btn_refresh.setFont(font)
        self.btn_refresh.setObjectName("btn_refresh")
        
        self.comboBox_port = QtWidgets.QComboBox(self.tab_2)
        self.comboBox_port.setGeometry(QtCore.QRect(110, 40, 70, 25))
        self.comboBox_port.setObjectName("comboBox_port")
        self.comboBox_port.currentIndexChanged.connect(self.connect_comm)
        
        self.label_13 = QtWidgets.QLabel(self.tab_2)
        self.label_13.setGeometry(QtCore.QRect(20, 10, 75, 25))
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.doubleSpinBox_stepsizepermm = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.doubleSpinBox_stepsizepermm.setGeometry(QtCore.QRect(130, 80, 62, 22))
        self.doubleSpinBox_stepsizepermm.setMaximum(100000.0)
        self.doubleSpinBox_stepsizepermm.setProperty("value", 561.1)
        self.doubleSpinBox_stepsizepermm.setObjectName("doubleSpinBox_stepsizepermm")
        
        self.doubleSpinBox_microstepping = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.doubleSpinBox_microstepping.setGeometry(QtCore.QRect(130, 20, 62, 22))
        self.doubleSpinBox_microstepping.setDecimals(0)
        self.doubleSpinBox_microstepping.setMaximum(1000000.0)
        self.doubleSpinBox_microstepping.setSingleStep(1.0)
        self.doubleSpinBox_microstepping.setProperty("value", 400.0)
        self.doubleSpinBox_microstepping.setObjectName("doubleSpinBox_microstepping")
        
        self.doubleSpinBox_stepperrev = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.doubleSpinBox_stepperrev.setGeometry(QtCore.QRect(130, 50, 62, 22))
        self.doubleSpinBox_stepperrev.setDecimals(0)
        self.doubleSpinBox_stepperrev.setMaximum(10000.0)
        self.doubleSpinBox_stepperrev.setSingleStep(10.0)
        self.doubleSpinBox_stepperrev.setProperty("value", 200.0)
        self.doubleSpinBox_stepperrev.setObjectName("doubleSpinBox_stepperrev")
        self.label_8 = QtWidgets.QLabel(self.tab_3)
        self.label_8.setGeometry(QtCore.QRect(20, 80, 101, 21))
        font = QtGui.QFont()
            
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_14 = QtWidgets.QLabel(self.tab_3)
        self.label_14.setGeometry(QtCore.QRect(20, 50, 101, 21))
        font = QtGui.QFont()
            
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.tab_3)
        self.label_15.setGeometry(QtCore.QRect(20, 20, 101, 21))
        font = QtGui.QFont()
            
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.label_20 = QtWidgets.QLabel(self.tab_3)
        self.label_20.setGeometry(QtCore.QRect(20, 110, 421, 21))
        font = QtGui.QFont()
            
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.label_21 = QtWidgets.QLabel(self.tab_3)
        self.label_21.setGeometry(QtCore.QRect(20, 130, 421, 21))
        font = QtGui.QFont()
            
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.doubleSpinBox_pausesteps = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.doubleSpinBox_pausesteps.setGeometry(QtCore.QRect(130, 160, 62, 22))
        self.doubleSpinBox_pausesteps.setMaximum(10000.0)
        self.doubleSpinBox_pausesteps.setProperty("value", 400.0)
        self.doubleSpinBox_pausesteps.setObjectName("doubleSpinBox_pausesteps")
        self.label_23 = QtWidgets.QLabel(self.tab_3)
        self.label_23.setGeometry(QtCore.QRect(20, 160, 101, 21))
        font = QtGui.QFont()
            
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.doubleSpinBox_motorspeed = QtWidgets.QDoubleSpinBox(self.tab_3)
        self.doubleSpinBox_motorspeed.setGeometry(QtCore.QRect(130, 190, 62, 22))
        self.doubleSpinBox_motorspeed.setMaximum(10000.0)
        self.doubleSpinBox_motorspeed.setProperty("value", 60.0)
        self.doubleSpinBox_motorspeed.setObjectName("doubleSpinBox_motorspeed")
        self.label_26 = QtWidgets.QLabel(self.tab_3)
        self.label_26.setGeometry(QtCore.QRect(20, 190, 91, 21))
        font = QtGui.QFont()
            
        self.label_26.setFont(font)
        self.label_26.setObjectName("label_26")
        self.tabWidget.addTab(self.tab_3, "")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Motor Controller"))
        self.btn_up.setText(_translate("Form", "STEP UP"))
        self.btn_startFS.setText(_translate("Form", "RUN SEQUENCE"))
        self.btn_down.setText(_translate("Form", "STEP DOWN"))
        self.label_6.setText(_translate("Form", "Feedback Terminal"))
        self.label_5.setText(_translate("Form", "um"))
        self.label_9.setText(_translate("Form", "ms"))
        self.label_10.setText(_translate("Form", "Pause between steps"))
        self.label_4.setText(_translate("Form", "Step Size"))
        self.label_7.setText(_translate("Form", "# Steps"))
        self.groupBox_direction.setTitle(_translate("Form", "Step Direction"))
        self.radioButton_up.setText(_translate("Form", "UP"))
        self.radioButton_down.setText(_translate("Form", "DOWN"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Motion"))
        self.label_11.setText(_translate("Form", "Comm Port"))
        self.label_baud.setText(_translate("Form", "115200"))
        self.label_12.setText(_translate("Form", "Baud"))
        self.btn_refresh.setText(_translate("Form", "Refresh"))
        self.label_13.setText(_translate("Form", "Microcontroller"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Serial Port"))
        self.label_8.setText(_translate("Form", "Steps/mm"))
        self.label_14.setText(_translate("Form", "Motor steps/rev"))
        self.label_15.setText(_translate("Form", "Microstepping"))
        self.label_20.setText(_translate("Form", "5050 raw steps correlates to about 90 degrees motor motion"))
        self.label_21.setText(_translate("Form", "Back calculate appropriate step size from there..."))
        self.label_23.setText(_translate("Form", "Pause Steps"))
        self.label_26.setText(_translate("Form", "Velocity"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Motor Spec"))

    
    def refresh_comms_click(self):
        ports.update_ports()
        #ports.print_ports()
        self.feedback("Ports List:")
        
        list1=[]
        i=0
        for port, desc, hwid in sorted(ports.portlist):
            self.feedback("{}: {} [{}]".format(port, desc, hwid))
            list1.insert(i,port)
            i=i+1
                
        self.comboBox_port.clear()
        self.comboBox_port.addItems(list1)
        
        self.comboBox_port.setCurrentIndex(i-1)
        
    def connect_comm(self):
        try:
            self.feedback("Attempting to connect to {}...".format(self.comboBox_port.currentText()))
            ports.select_port()
        except:
            self.feedback("Failed to connect to {}".format(self.comboBox_port.currentText()))

    def feedback(self, newstring):
        print("\n"+newstring)
        self.feedback_string = self.feedback_string+"\n"+newstring
        self.textEdit_feedback.setText(self.feedback_string)
        self.textEdit_feedback.moveCursor(QtGui.QTextCursor.End)
        
    def update_vars(self):
        
        self.step_size_um = self.doubleSpinBox_stepsize.value()
        self.num_pictures = int(self.doubleSpinBox_numimages.value())
        self.settle_time_ms = self.doubleSpinBox_stabletime.value()
        self.usteps = self.doubleSpinBox_microstepping.value()
        
        self.command_set_step_size()
        
        if self.radioButton_up.isChecked():
            self.step_dir = True # UP
        else:
            self.step_dir = False # DOWN
            

    def run_sequence(self):
        if self.connected:
            self.update_vars()
            time.sleep(0.005)
            self.command_set_pause()
            time.sleep(0.005)
            for i in range(0,self.num_pictures):
                self.command_LED()
                if self.step_dir:
                    self.press_btn_up()
                else:
                    self.press_btn_down()
                time.sleep(self.settle_time_ms/1000)
        else:
            self.feedback("Connect to serial port first!")
            self.feedback("Attempting to guess port connection...")
            self.refresh_comms_click()
        
    def press_btn_up(self):
        try:
            self.update_vars()
            trunc_step_size = "%.9f" % self.step_size_um
            write_cmd = 'w '+str(trunc_step_size)+'\n'
            ser.write(write_cmd.encode())
            self.position = self.position + self.step_size_um
            self.feedback("step: up  \t Z = {}".format(self.position))
        except:
            self.feedback("Connect to serial port first!")
            self.feedback("Attempting to guess port connection...")
            self.refresh_comms_click()
        
        
    def press_btn_down(self):
        try:
            self.update_vars()
            trunc_step_size = "%.9f" % self.step_size_um
            write_cmd = 's '+str(trunc_step_size)+'\n'
            ser.write(write_cmd.encode())
            self.position = self.position - self.step_size_um
            self.feedback("step: down\t Z = {}".format(self.position))
        except:
            self.feedback("Connect to serial port first!")
            self.feedback("Attempting to guess port connection...")
            self.refresh_comms_click()
    
    def command_LED(self):
        ser.write('l\n'.encode())
        #self.feedback('blip LED')
        
    def command_set_step_size(self):
        trunc_step_size = "%.5f" % (self.step_size_um/4.0)
        ser.write('z {}\n'.format(str(trunc_step_size)).encode())
        self.feedback('set step size to {}. Default: 5050 for ~90 degrees'.format(self.step_size_um))
        
    def command_set_pause(self):
        ser.write('p {}\n'.format(self.settle_time_ms).encode())
        self.feedback('set step pause size to {}. Default: 400'.format(self.settle_time_ms))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    
    app_icon = QtGui.QIcon()
    app_icon.addFile('C:/Users/schra/Documents/Python/FocusStack/icon48.png', QtCore.QSize(48,48))
    Form.setWindowIcon(app_icon)
    
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    
    
    ser.close()
    sys.exit(app.exec_())
