class FlowValveController:
    """
    This class defines a standard interface for a client to use a flow / valve
    controller. It is intended that you use this interface with a context manager
    in order to properly dispose of any references to physical hardware controllers.
    """

    def __init__(self):
        raise NotImplementedError("FlowValveController.__init__ is unimplemented")

    def __enter__(self):
        raise NotImplementedError("FlowValveController.__enter__ is unimplemented")

    def __exit__(self):
        raise NotImplementedError("FlowValveController.__exit__ is unimplemented")

    def __str__(self):
        raise NotImplementedError("FlowValveController.__str__ is unimplemented")

    def add_sensor(self, channel, sensor):
        raise NotImplementedError("FlowValveController.add_sensor is unimplemented")

    def get_pressure(self, channel):
        raise NotImplementedError("FlowValveController.get_pressure is unimplemented")

    def set_pressure(self, channel, pressure):
        raise NotImplementedError("FlowValveController.set_pressure is unimplemented")
