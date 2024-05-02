import sys

from PyQt5.QtWidgets import QApplication
from flow_valve.controller import FlowValveApp
from flow_valve.model.flow_valve_controller.ob1 import FlowValveController


def main():
    app = QApplication(sys.argv)

    with FlowValveController() as controller:
        main_window = FlowValveApp(controller)
        main_window.show()
        app.exec_()


if __name__ == "__main__":
    main()
