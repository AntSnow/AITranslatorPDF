from .pdf_parser import PDFParser

from ..model import Model
from ..book import Book, ContentType
from ..utils import LOG

from .writer import Writer


class PDFTranslator:
    model: Model

    pdf_parser: PDFParser

    writer: Writer

    book: Book

    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self,
                      pdf_file_path: str,
                      file_format: str = 'markdown',
                      target_language: str = '中文',
                      output_file_path: str = None,
                      pages: int = None):

        # 解析`PDF`文件，生成`book`对象
        self.book = self.pdf_parser.parser_pdf(pdf_file_path, pages)

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):

                # 如果是图片，就跳过
                if content.content_type == ContentType.IMAGE: continue

                # 获取`prompt`
                prompt = self.model.get_translate_prompt(content, target_language)

                # 打印`prompt`
                LOG.debug(prompt)

                # 和大模型交互，获取结果
                translation, status = self.model.make_request(prompt)

                # 打印和大模型交互的结果
                LOG.info(translation)

                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)

        self.writer.save_translated_book(self.book, output_file_path, file_format)