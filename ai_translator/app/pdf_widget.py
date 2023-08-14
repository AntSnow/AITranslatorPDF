import fitz
import sys
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPaintEvent, QImage, QPixmap


class CustomWidget(QWidget):
    title: str

    def __init__(self, title: str = 'PDF Widget', parent=None):
        super().__init__(parent)

        self.title = title

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        label = QLabel("这是一个自定义窗口小部件")
        label.setStyleSheet("background-color: #f0f000")
        self.layout.addWidget(label)

        self.layout.addWidget(label)


# 展示`PDF`的`Widget`，宽高暂时固定
class PDFWidget(QWidget):

    @classmethod
    def widget_size(cls) -> QSize:
        return QSize(
            10 + PDFWidget.pdf_size().width() + 10,
            10 + 30 + 10 + PDFWidget.pdf_size().height() + 10 + 30 + 10
        )

    @classmethod
    def pdf_size(cls) -> QSize:
        return QSize(400, 400 * 1.414)

    @classmethod
    def button_style(cls) -> str:
        return """
            background: rgb(236, 236, 236); 
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """

    stack_widget: QStackedWidget

    content_widget: QWidget

    empty_widget: QWidget

    # 顶部`Title`
    title: str

    # 是否是待翻译的文件
    is_original: bool

    # `PDF`文件的地址
    pdf_path: str

    # `PDF`的`Document`
    pdf_doc: fitz.Document

    # `PDF`的`index`
    pdf_index: int

    pdf_label: QLabel

    index_label: QLabel

    pre_button: QPushButton

    next_button: QPushButton

    def __init__(self, is_original: bool, title: str = 'PDF Widget', parent=None):
        super().__init__(parent)

        self.is_original = is_original
        self.title = title

        self.setFixedSize(PDFWidget.widget_size())

        self.stack_widget = QStackedWidget()
        self.content_widget = QWidget()
        self.empty_widget = QWidget()

        self.pdf_label = QLabel()
        self.index_label = QLabel()
        self.pre_button = QPushButton()
        self.next_button = QPushButton()

        self._setup_ui()

    # 设置UI
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)
        self.setLayout(layout)

        if self.is_original:
            self.stack_widget.setStyleSheet("background-color: #fdeff2")
        else:
            self.stack_widget.setStyleSheet("background-color: #f7fcfe")

        layout.addWidget(self.stack_widget)

        self.stack_widget.addWidget(self.empty_widget)
        self.stack_widget.addWidget(self.content_widget)

        self._setup_ui_of_empty_widget()
        self._setup_ui_of_content_widget()

    def _setup_ui_of_empty_widget(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        self.empty_widget.setLayout(layout)

        text = "未发现PDF文件" if self.is_original else "未发现翻译后的文件"

        button = QPushButton(text)
        button.setFixedSize(200, 100)
        button.setStyleSheet("""
            border: none;
            background-color: transparent;
            padding: 0;
            outline: none;
            color: #474a4d;
        """)
        self.empty_widget.layout().addWidget(button)

    def _setup_ui_of_content_widget(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        self.content_widget.setLayout(layout)

        title_label = QLabel(self.title)
        title_label.setFixedHeight(30)
        title_label.setAlignment(Qt.AlignCenter)
        self.content_widget.layout().addWidget(title_label)

        self.pdf_label.setFixedSize(PDFWidget.pdf_size())
        self.pdf_label.setScaledContents(True)
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.content_widget.layout().addWidget(self.pdf_label)

        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(30)
        self.content_widget.layout().addWidget(bottom_widget)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setAlignment(Qt.AlignCenter)
        bottom_widget.setLayout(bottom_layout)

        self.pre_button.setText("上一页")
        self.pre_button.setFixedSize(60, 24)
        self.pre_button.setFlat(True)
        self.pre_button.setStyleSheet(PDFWidget.button_style())
        self.pre_button.clicked.connect(self._tap_pre_button)
        bottom_widget.layout().addWidget(self.pre_button)

        self.index_label.setText("- - -")
        bottom_widget.layout().addWidget(self.index_label)

        self.next_button.setText("下一页")
        self.next_button.setFixedSize(60, 24)
        self.next_button.setFlat(True)
        self.next_button.setStyleSheet(PDFWidget.button_style())
        self.next_button.clicked.connect(self._tap_next_button)
        bottom_widget.layout().addWidget(self.next_button)

    # 点击`上一页`按钮
    def _tap_pre_button(self):
        self._update_pdf_page(self.pdf_index - 1)

    # 点击`下一页`按钮
    def _tap_next_button(self):
        self._update_pdf_page(self.pdf_index + 1)

    # 更新`PDF`文件的路径
    def update_pdf_url(self, pdf_url: str):
        self.pdf_path = pdf_url
        self.update_pdf_doc()

    # 更新`PDF`文件的`Document`
    def update_pdf_doc(self):
        if os.path.exists(self.pdf_path):
            self.stack_widget.setCurrentIndex(1)
            self.pdf_doc = fitz.Document(self.pdf_path)
            self._update_pdf_page(0)
        else:
            self.stack_widget.setCurrentIndex(0)

    # 更新`PDF`页面
    def _update_pdf_page(self, target_index: int):
        final_index = target_index
        if target_index <= 0:
            final_index = 0
        elif target_index >= self.pdf_doc.page_count - 1:
            final_index = self.pdf_doc.page_count - 1

        page = self.pdf_doc.load_page(final_index)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        q_image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)

        self.pdf_index = final_index
        self.index_label.setText(f'{final_index + 1} / {self.pdf_doc.page_count}')
        self.pre_button.setEnabled(final_index > 0)
        self.next_button.setEnabled(final_index < self.pdf_doc.page_count - 1)
        self.pdf_label.setPixmap(q_pixmap)
