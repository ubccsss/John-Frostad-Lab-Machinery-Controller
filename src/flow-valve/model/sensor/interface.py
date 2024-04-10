class Sensor:
    """
    This class defines a standard interface for a
    sensor.
    """

    def __init__(self):
        raise NotImplementedError("Sensor.__init__ is unimplemented")

    def get_type(self):
        raise NotImplementedError("Sensor.get_type is unimplemented")

    def is_digital(self):
        raise NotImplementedError("Sensor.is_digital is unimplemented")

    def get_digital_calibration(self):
        raise NotImplementedError("Sensor.get_digital_calibration is unimplemented")

    def get_digital_resolution(self):
        raise NotImplementedError("Sensor.get_digital_resolution is unimplemented")

    def get_voltage(self):
        raise NotImplementedError("Sensor.get_voltage is unimplemented")
