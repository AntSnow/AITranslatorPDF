import os.path
import sys
import time
import concurrent.futures

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDesktopWidget, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QComboBox, QFileDialog
)

from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtCore import QUrl, Qt, QThread, pyqtSignal, QSize

from .pdf_widget import PDFWidget
from .ui_base import UIBase
from .translator_thread import TranslatorThread

from ..utils import Common, ConfigLoader, LOG


class Application:
    # App
    app: QApplication

    # Widow
    window: QMainWindow

    # 最下层的`Widget`
    base_widget: QWidget

    # 开始翻译按钮
    begin_button: QPushButton

    # 设置配置信息的`Widget`
    config_widget: QWidget

    # 存放`Model`信息的`Widget`
    model_widgets: list[QWidget]

    # 大模型类型
    model_type: str

    # 大模型类型的选择器
    model_combo: QComboBox

    # 大模型名称
    model_name: str

    # 大模型名称的选择器
    model_name_combo: QComboBox

    # 配置信息
    info_dict: dict

    # 来自`yaml`文件的配置信息
    yaml_config: dict

    # 底部打印日志输出
    log_text_edit: QLabel

    # 左侧的`PDF`容器
    left_pdf_widget: PDFWidget

    # 右侧的`PDF`容器
    right_pdf_widget: PDFWidget

    left_pdf_url: str
    left_pdf_path_text_edit: QTextEdit

    right_pdf_url: str
    right_pdf_path_text_edit: QTextEdit

    def __init__(self, app_name: str, pdf_path: str, yaml_config: str):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(app_name)
        self.base_widget = QWidget()
        self.info_dict = {}
        self.yaml_config = yaml_config
        self.model_type = Common.model_types()[0]
        self.model_name = Common.model_names(self.model_type)[0]

        self._setup_ui()

        self.left_pdf_url = pdf_path
        self.right_pdf_url = pdf_path.replace('.pdf', '_translated.pdf')

        self.left_pdf_widget.update_pdf_url(pdf_path)
        self.right_pdf_widget.update_pdf_url(self.right_pdf_url)

        self._update_config_info()
        self._update_config_key_of_model()
        self._update_config_value_of_model()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())

    def _setup_ui(self):
        # 获取`Window`的布局参数
        min_height = 10 + 30 + 10 + 400 * 1.414 + 10 + 30 + 10 + 1 + 100
        min_width = 200 + 1 + 10 + 400 + 10 + 1 + 10 + 400 + 10
        top_offset = (UIBase.get_desk_height() - min_height) / 2
        left_offset = (UIBase.get_desk_width() - min_width) / 2

        # 设置`Window`的布局
        self.window.setGeometry(left_offset, top_offset, min_width, min_height)
        self.window.setMinimumSize(min_width, min_height)
        self.window.setMaximumWidth(min_width + 200)

        # 设置`base_widget`
        self.window.setCentralWidget(self.base_widget)
        self.base_widget.setStyleSheet("background-color: #f0f0f4")

        # 设置`base_widget`对应的`base_layout`
        base_layout = QHBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(1)
        self.base_widget.setLayout(base_layout)

        # 设置左侧配置用的`Widget`容器，并将其添加到`base_widget`上
        left_widget = QWidget()
        base_layout.addWidget(left_widget)
        self.config_widget = left_widget
        self._setup_ui_of_config(left_widget)

        # 设置底部的`Widget`容器，并将其添加到`base_widget`上
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #f0f0f4")
        base_layout.addWidget(right_widget)

        # 设置与底部`Widget`对应的`bottom_layout`
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(1)
        right_widget.setLayout(right_layout)

        # 设置底部的`Widget`容器，并将其添加到`base_widget`上
        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(PDFWidget.widget_size().height())
        bottom_widget.setFixedWidth(PDFWidget.widget_size().width() * 2 + 1)
        bottom_widget.setStyleSheet("background-color: #f0f0f4")
        right_layout.addWidget(bottom_widget)

        # 设置底部的`LogWidget`，并将其添加到`base_widget`上
        log_widget = QLabel()
        log_widget.setStyleSheet("background-color: #ffffff; border:none;")
        # log_widget.setReadOnly(True)
        right_layout.addWidget(log_widget)
        self.log_text_edit = log_widget

        # 设置与底部`Widget`对应的`bottom_layout`
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(1)
        bottom_widget.setLayout(bottom_layout)

        self.left_pdf_widget = PDFWidget(is_original=True, title="翻译前")
        bottom_layout.addWidget(self.left_pdf_widget)

        self.right_pdf_widget = PDFWidget(is_original=False, title="翻译后")
        bottom_layout.addWidget(self.right_pdf_widget)

    def _setup_ui_of_config(self, base_widget: QWidget):
        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(10, 10, 10, 10)
        base_layout.setSpacing(10)
        base_layout.setAlignment(Qt.AlignTop)
        base_widget.setLayout(base_layout)

        button = QPushButton("开始翻译")
        button.setFixedHeight(40)
        button.setStyleSheet("""
            background: #e95464;
            font-size: 14px;
            color: #ffffff;
            border-radius: 5px;
        """)
        button.clicked.connect(self._tap_begin)
        base_layout.addWidget(button)
        self.begin_button = button

        base_layout.addWidget(self._get_left_path_widget())

        base_layout.addWidget(self._get_right_path_widget())

        model_combo = QComboBox()
        model_combo.setFixedHeight(26)
        model_combo.setContentsMargins(0, 0, 0, 0)
        model_combo.setFrame(False)
        model_combo.setAcceptDrops(False)
        model_combo.setStyleSheet("""
            QComboBox::item:selected { color: blue };
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """)
        model_combo.addItems(Common.model_types())
        model_combo.currentIndexChanged.connect(self._tap_model_type)
        base_layout.addWidget(self._get_title_widget("大模型类型", model_combo))
        self.model_combo = model_combo

        model_name_combo = QComboBox()
        model_name_combo.setFixedHeight(26)
        model_name_combo.setContentsMargins(0, 0, 0, 0)
        model_name_combo.setFrame(False)
        model_name_combo.setAcceptDrops(False)
        model_name_combo.setStyleSheet("""
            QComboBox::item:selected { color: blue };
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """)
        model_name_combo.addItems(Common.model_names(self.model_type))
        model_name_combo.currentIndexChanged.connect(self._tap_model_type)
        base_layout.addWidget(self._get_title_widget("大模型名称", model_name_combo))
        self.model_name_combo = model_name_combo

    def _get_title_widget(self, title: str, content_widget: QWidget) -> QWidget:
        base_widget = QWidget()
        base_widget.setFixedHeight(content_widget.height() + 25)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(5)
        base_widget.setLayout(base_layout)

        label = QLabel(title)
        label.setStyleSheet("color: #afafb0")
        label.setFixedHeight(20)
        base_layout.addWidget(label)

        base_layout.addWidget(content_widget)

        return base_widget

    def _get_left_path_widget(self) -> QWidget:
        base_widget = QWidget()
        base_widget.setFixedHeight(100)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(5)
        base_widget.setLayout(base_layout)

        top_widget = QWidget()
        top_widget.setFixedHeight(20)
        base_layout.addWidget(top_widget)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.setAlignment(Qt.AlignVCenter)
        top_widget.setLayout(top_layout)

        label = QLabel("要翻译的PDF地址")
        label.setFixedHeight(20)
        label.setStyleSheet("color: #afafb0")
        top_layout.addWidget(label)

        top_layout.addStretch()

        button = QPushButton("选择文件")
        button.setFixedSize(52, 20)
        button.setStyleSheet("""
            font-size: 11px;
            color: #5383c3;
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """)
        button.clicked.connect(self._tap_left_path_button)
        top_layout.addWidget(button)

        path_text_edit = QTextEdit()
        path_text_edit.setFixedHeight(75)
        path_text_edit.setAcceptRichText(False)
        path_text_edit.setReadOnly(True)
        path_text_edit.setStyleSheet("""
            color: black;
            font-size: 14px;
            QTextEdit::chunk { background-color: transparent; width: 0px; };
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """)
        base_layout.addWidget(path_text_edit)

        self.left_pdf_path_text_edit = path_text_edit

        return base_widget

    def _get_right_path_widget(self) -> QWidget:
        base_widget = QWidget()
        base_widget.setFixedHeight(100)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(5)
        base_widget.setLayout(base_layout)

        top_widget = QWidget()
        top_widget.setFixedHeight(20)
        base_layout.addWidget(top_widget)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.setAlignment(Qt.AlignVCenter)
        top_widget.setLayout(top_layout)

        label = QLabel("翻译后的存放地址")
        label.setFixedHeight(20)
        label.setStyleSheet("color: #afafb0")
        top_layout.addWidget(label)

        top_layout.addStretch()

        button = QPushButton("选择文件夹")
        button.setFixedSize(62, 20)
        button.setStyleSheet("""
            font-size: 11px;
            color: #5383c3;
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """)
        button.clicked.connect(self._tap_right_path_button)
        top_layout.addWidget(button)

        path_text_edit = QTextEdit()
        path_text_edit.setFixedHeight(75)
        path_text_edit.setAcceptRichText(False)
        path_text_edit.setReadOnly(True)
        path_text_edit.setStyleSheet("""
            color: black;
            font-size: 14px;
            QTextEdit::chunk { background-color: transparent; width: 0px; };
            border: 1px solid rgb(209, 209, 209); 
            border-radius: 2px;
        """)
        base_layout.addWidget(path_text_edit)

        self.right_pdf_path_text_edit = path_text_edit

        return base_widget

    # MARK: - 更新`UI`的方法

    def _update_config_info(self):
        self.left_pdf_path_text_edit.setText(self.left_pdf_url)
        self.right_pdf_path_text_edit.setText(self.right_pdf_url)

    # 更新配置参数的`Key`（从`utils`中的`Common`读取需要的`Key`）
    def _update_config_key_of_model(self):
        for widget in self.config_widget.children():
            if widget.property("tag") == "model-title":
                widget.setParent(None)

        print(f"_update_config_of_model, model_type = {self.model_type}")
        for title in Common.model_required(self.model_type):
            text_edit = QTextEdit()
            text_edit.setFixedHeight(40)
            text_edit.setAcceptRichText(False)
            text_edit.setStyleSheet("""
                color: black;
                font-size: 14px;
                QTextEdit::chunk { background-color: transparent; width: 0px; };
                border: 1px solid rgb(209, 209, 209); 
                border-radius: 2px;
            """)
            text_edit.setProperty("tag", f"model-edit-{self.model_type}-{title}")
            title_widget = self._get_title_widget(f"请输入 {title}", text_edit)
            title_widget.setProperty("tag", "model-title")
            self.config_widget.layout().addWidget(title_widget)

    # 更新配置参数的`Value`（从`config.yaml`中读取`Key`对应的`Value`，没有的话就不填，让用户填）
    def _update_config_value_of_model(self):
        if self.yaml_config[self.model_type]:
            info = self.yaml_config[self.model_type]
            for widget in self.config_widget.children():
                if widget.property("tag") == "model-title":
                    for sub_widget in widget.children():
                        if sub_widget.property("tag") and "model-edit" in sub_widget.property("tag"):
                            tag_model_config_title = sub_widget.property("tag").split("-")[3]
                            if info[tag_model_config_title]:
                                sub_widget.setText(f'{info[tag_model_config_title]}')

    def _tap_model_type(self):
        if self.model_type != self.model_combo.currentText():
            self.model_type = self.model_combo.currentText()
            self.model_name_combo.clear()
            self.model_name_combo.addItems(Common.model_names(self.model_type))
            self._tap_model_name()
            self._update_config_key_of_model()
            self._update_config_value_of_model()

    def _tap_model_name(self):
        if self.model_name != self.model_name_combo.currentText():
            self.model_name = self.model_name_combo.currentText()

    def _tap_left_path_button(self):
        file_info = QFileDialog.getOpenFileName(self.window, 'Open File', filter="PDF files (*.pdf)")
        file_path = file_info[0]
        if file_path:
            self.left_pdf_url = file_path
            self.left_pdf_path_text_edit.setText(self.left_pdf_url)
            self.left_pdf_widget.update_pdf_url(file_path)

    def _tap_right_path_button(self):
        if self.left_pdf_url:
            dialog = QFileDialog()
            dialog.setFileMode(dialog.Directory)
            if dialog.exec_():
                path = dialog.selectedFiles()[0]
                basename = os.path.basename(self.left_pdf_url).replace('.pdf', '_translated.pdf')
                self.right_pdf_url = path + '/' + basename
                self.right_pdf_path_text_edit.setText(self.right_pdf_url)
                self.right_pdf_widget.update_pdf_url(self.right_pdf_url)
        else:
            LOG.warning("需要先选好需要翻译的PDF文件")

    def execute_time_consuming_task(self):
        self.begin_button.setEnabled(False)
        self.begin_button.setText("正在翻译中...")

        self.worker_thread = TranslatorThread(info=self._get_info_dict())
        self.worker_thread.finished.connect(self.on_thread_finished)
        self.worker_thread.start()

    def on_thread_finished(self):
        self.begin_button.setEnabled(True)
        self.begin_button.setText("开始翻译")
        self.right_pdf_widget.update_pdf_doc()

    # 点击开始翻译
    def _tap_begin(self):
        self.execute_time_consuming_task()

    # 获取开始翻译时，回调的`dict`
    def _get_info_dict(self) -> dict:
        info_dict = {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "pdf_file_path": self.left_pdf_url,
            "output_file_path": self.right_pdf_url,
        }
        for widget in self.config_widget.children():
            if widget.property("tag") == "model-title":
                for sub_widget in widget.children():
                    if sub_widget.property("tag") and "model-edit" in sub_widget.property("tag"):
                        tag_model_config_title = sub_widget.property("tag").split("-")[3]
                        info_dict[tag_model_config_title] = sub_widget.toPlainText()
        return info_dict

    # 翻译完成
    def translation_completed(self):
        self._update_pdf_doc(False)

    def logger_callback(self, message: str):
        print(message)
        self.log_text_edit.setText(message)
        # self.log_text_edit.setText(message)
        # self.log_text_edit.append(f'{message.strip()}')
        # self.log_text_edit.verticalScrollBar().setValue(self.log_text_edit.verticalScrollBar().maximum())
