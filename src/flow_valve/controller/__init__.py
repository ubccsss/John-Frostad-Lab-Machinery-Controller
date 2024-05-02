from PyQt5.QtCore import QTimer
from ..view import FlowValveView
from ..model.sensor.granular_sensor import GranularSensor

# 1 s = 1000ms
SEC = 1000


class FlowValveApp:
    def __init__(self, model):
        ui = FlowValveView()

        self.model = model
        self.ui = ui
        self.active_stream = 1

        ui.pushButton.clicked.connect(self.add_sensor)

        streams = ui.streams()

        # NOTE: This would be nicer as a for loop, but Python for loops don't
        # play nicely with lambdas since it captures the index variable and
        # not the value itself. This means that any toggled radio button will
        # end up calling self.on_stream_change(4, streams[3]) !
        streams[0].toggled.connect(lambda: self.on_stream_change(1, streams[0]))
        streams[1].toggled.connect(lambda: self.on_stream_change(2, streams[1]))
        streams[2].toggled.connect(lambda: self.on_stream_change(3, streams[2]))
        streams[3].toggled.connect(lambda: self.on_stream_change(4, streams[3]))

        # Pressure get loop
        timer = QTimer(self)
        timer.setInterval(1.00 * SEC)
        timer.timeout.connect(self.show_pressure)
        timer.start()

    def show_pressure(self):
        try:
            pressure = self.model.get_pressure(self.active_stream)
            self.ui.pressure_box.setText(pressure)
        except Exception:
            print(f"Failed to get pressure from stream {self.active_stream}. " +
                  "Maybe sensor has not been added?")

    def set_pressure(self, pressure):
        try:
            pressure = self.model.set_pressure(self.active_stream, pressure)
            self.ui.pressure_box.setText(pressure)
        except Exception:
            print(f"Failed to set pressure from stream {self.active_stream}. " +
                  "Maybe sensor has not been added?")

    def add_sensor(self):
        # The combo box layout and the (elveflow-internal) sensor API has a nice
        # 1-to-1 correspondence (e.g. the regulator_type QComboBox index 0
        # "Z_regulator_type_none" also has an index 0 in the Elveflow API),
        # so no fancy mapping is required. Do note that
        # in case of changes, this may not hold.

        type = self.ui.regulator_type().currentIndex()
        digital = self.ui.digital_analog().currentIndex()
        calibration = self.ui.fsd_calibration().currentIndex()
        resolution = self.ui.dfs_resolution().currentIndex()

        sensor = GranularSensor(type, digital, calibration, resolution)
        self.model.add_sensor(self.active_stream, sensor)

    def on_stream_change(self, stream_idx, button):
        if button.isChecked():
            self.active_stream = stream_idx
            self.ui.active_stream.setText(f"Active stream is {stream_idx}")

    def show(self):
        self.ui.show_ui()
