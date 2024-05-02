import sys

from .interface import FlowValveController


from ctypes import *
from Elveflow64 import *



class Ob1FlowValveController(FlowValveController):
    def __init__(self, name):
        self.name = name
        self.instrument_id = None

    def __enter__(self):
        name_ascii_encoded = self.name.encode('ascii')
        instrument_id_ref = c_int32()

        error = OB1_Initialization(name_ascii_encoded, 0, 0, 0, 0, byref(instrument_id_ref))
        # ^ handle this

        self.instrument_id = instrument_id_ref.value
        return self

    def __exit__(self):
        OB1_Destructor(self.instrument_id)

    def __str__(self):
        #raise NotImplementedError("FlowValveController.__str__ is unimplemented")
        return f"OB1 Controller {self.name}, ID: {self.instrument_id}"

    def get_pressure(self, channel):
        #raise NotImplementedError("FlowValveController.get_pressure is unimplemented")
        pressure = c_double()
        # Assuming default calibration is loaded and calibration length is 1000
        error = OB1_Get_Press(self.instrument_id, channel, 1, byref(self.calib), byref(pressure), 1000)
        if error != 0:
            raise Exception(f"Get pressure failed with error code: {error}")
        return pressure.value

    def set_pressure(self, channel, pressure):
        #raise NotImplementedError("FlowValveController.set_pressure is unimplemented")
        error = OB1_Set_Press(self.instrument_id, channel, c_double(pressure), byref(self.calib), 1000)
        if error != 0:
            raise Exception(f"Set pressure failed with error code: {error}")
