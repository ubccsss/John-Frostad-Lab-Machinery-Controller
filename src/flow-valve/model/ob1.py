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


    def __str__(self):
        raise NotImplementedError("FlowValveController.__str__ is unimplemented")

    def get_pressure(self, channel):
        raise NotImplementedError("FlowValveController.get_pressure is unimplemented")

    def set_pressure(self, channel, pressure):
        raise NotImplementedError("FlowValveController.set_pressure is unimplemented")
