from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QRect, QSize


class UIBase:

    @classmethod
    def get_desk_rect(cls) -> QRect:
        desktop = QApplication.desktop()
        return desktop.screenGeometry()

    @classmethod
    def get_desk_size(cls) -> QSize:
        return UIBase.get_desk_rect().size()

    @classmethod
    def get_desk_width(cls) -> int:
        desktop = QApplication.desktop()
        return desktop.screenGeometry().width()

    @classmethod
    def get_desk_height(cls) -> int:
        desktop = QApplication.desktop()
        return desktop.screenGeometry().height()
