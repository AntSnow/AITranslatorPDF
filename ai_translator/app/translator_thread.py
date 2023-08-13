from PyQt5.QtCore import QThread, pyqtSignal

from ..translator import PDFTranslator
from ..model import QWenModel, OpenAIModel
from ..utils import LOG


class TranslatorThread(QThread):
    # 信号
    finished = pyqtSignal()

    # 翻译器
    translator: PDFTranslator

    info: dict

    def __init__(self, info: dict):
        super().__init__()

        if info['model_type'] == "QWenModel":
            model = QWenModel(
                api_url=info["api_url"],
                api_key=info["api_key"],
                timeout=int(info["timeout"]),
            )
            self.translator = PDFTranslator(model)

        elif info['model_type'] == "OpenAIModel":
            model = OpenAIModel(
                model=info["model_name"],
                api_key=info["api_key"]
            )
            self.translator = PDFTranslator(model)

        else:
            self.translator = None
            LOG.warning(f"暂不支持的大模型，{info['model_type']}")

        self.info = info

    def run(self):
        if self.translator:
            try:
                self.translator.translate_pdf(
                    pdf_file_path=self.info['pdf_file_path'],
                    output_file_path=self.info['output_file_path'],
                    file_format="PDF",
                )
            except Exception as e:
                LOG.error(e)
        self.finished.emit()
