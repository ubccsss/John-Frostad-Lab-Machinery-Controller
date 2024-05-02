from PyQt5 import uic, Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel


Z_regulator_type = [
        "Z_regulator_type_none 0",
        "Z_regulator _type__0_200_mbar 1",
        "Z_regulator _type__0_2000_mbar 2",
        "Z_regulator _type__0_8000_mbar 3",
        "Z_regulator_type_m1000_1000_mbar 4",
        "Z_regulator_type_m1000_6000_mbar 5",
]



class FlowValveView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_stream = QLabel(self)
        uic.loadUi("flow.ui", self)

    def show_ui(self):
        self.show()

    def regulator_type(self):
        return self.comboBox

    def sensor_type(self):
        return self.comboBox_2

    def digital_analog(self):
        return self.comboBox_3

    def dfs_resolution(self):
        return self.comboBox_4

    def fsd_calibration(self):
        return self.comboBox_5

    def streams(self):
        return [self.radioButton, self.radioButton_2, self.radioButton_3, self.radioButton_4]

    def pressure_box(self):
        return self.lineEdit_2
