
from .interface import Sensor


class GranularSensor(Sensor):
    """
    This sensor implementation is a granular
    sensor that allows you to pass in any
    value into OB1_Add_Sens.
    """

    def __init__(self, type, digital, calibration, resolution, voltage=0):
        self.type = type
        self.digital = digital
        self.calibration = calibration
        self.resolution = resolution
        self.voltage = voltage

    def get_type(self):
        return self.type

    def is_digital(self):
        return self.digital

    def get_digital_calibration(self):
        return self.calibration

    def get_digital_resolution(self):
        return self.resolution

    def get_voltage(self):
        return self.voltage
