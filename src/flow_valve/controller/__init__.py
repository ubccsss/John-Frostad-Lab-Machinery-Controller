
from ..view import FlowValveView


class FlowValveApp:

    def __init__(self, model):
        ui = FlowValveView()

        self.model = model
        self.ui = ui
        self.active_stream = 1
        self.sensors = []

        ui.pushButton.clicked.connect(self.add_sensor)

        streams = ui.streams()

        streams[0].toggled.connect(lambda: self.on_stream_change(1, streams[0]))
        streams[1].toggled.connect(lambda: self.on_stream_change(2, streams[1]))
        streams[2].toggled.connect(lambda: self.on_stream_change(3, streams[2]))
        streams[3].toggled.connect(lambda: self.on_stream_change(4, streams[3]))

    def show_pressure(self):
        try:
            pressure = self.model.get_pressure(self.active_stream)
            self.ui.pressure_box.setText(pressure)
        except Exception:
            print(f"Failed to get pressure from stream {self.active_stream}. " + 
                  "Maybe sensor has not been added?")
        


    def add_sensor(self):
        sensor = 1010101 # TODO
        self.model.add_sensor(self.active_stream, sensor)
        pass

    def on_stream_change(self, stream_idx, button):
        if button.isChecked():
            self.active_stream = stream_idx
            self.ui.active_stream.setText(f"Active stream is {stream_idx}")

    def show(self):
        self.ui.show_ui()
