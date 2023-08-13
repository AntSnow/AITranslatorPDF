import pdfplumber

from collections import Counter

from ..book import Book, Page, Content, ContentType, TableContent, ImageContent
from ..utils import LOG

from .exceptions import PageOutOfRangeException


class PDFParser:

    # 构造函数
    def __init__(self):
        pass

    def parser_pdf(self, pdf_file_path: str, pages: int = None) -> Book:
        # 初始化 book
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:

            # 如果想要翻译的页码，大于`PDF`总页数，就报错
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(book.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                book.add_page(self._new_parser_pdf_page(pdf_page=pdf_page))

        return book

    # 解析`pdfplumber.pdf.Page`，返回`Page`
    def _new_parser_pdf_page(self, pdf_page: pdfplumber.pdf.Page) -> Page:

        # 创建`Page`
        page = Page()

        contents: [Content] = []

        # 从单页的`PDF`中，取出每一行的文本数据，返回格式为`List[Dict[str, Any]]`
        lines = pdf_page.extract_text_lines()

        # 从单页的`PDF`中，取出表格数据，返回格式为`List[List[List[Optional[str]]]]`
        tables = pdf_page.extract_tables()

        # 图片信息
        images = pdf_page.images

        # `Table`的每一行的文本信息
        table_row_texts = []
        for table in tables:
            for row in table:
                table_row_texts.append(" ".join(row))

        page_left = self._get_all_left(pdf_page, lines)
        page_right = self._get_all_right(pdf_page, lines)

        page.left_margin = page_left
        page.right_margin = page_left
        page.top_margin = lines[0]['top'] if lines and lines[0]['top'] else 30
        page.bottom_margin = page.top_margin

        # 将同一个段落的`line`聚合到一个数组中
        para_lines: List[List[Dict[str, Any]]] = []

        temp_lines: List[Dict[str, Any]] = []

        for idx, line in enumerate(lines):

            if idx == 0: print(line)

            text: str = line['text'].strip()

            if not text in table_row_texts:
                temp_lines.append(line)

            if self._is_para_tail(page=pdf_page, line=line, idx=idx, total=len(lines)):
                para_lines.append(temp_lines)
                temp_lines = []

            for table in tables:
                if text == " ".join(table[0]):
                    para_lines.append(temp_lines)
                    temp_lines = []
                    table_content = TableContent([table])
                    table_content.top_y = line['chars'][0]['y0']
                    table_content.col_widths = self._get_col_widths(width=page_right - page_left, count=len(table[0]))
                    contents.append(table_content)
                    tables = tables[1:]
                    break

        if len(temp_lines) > 0: para_lines.append(temp_lines)

        for lines in para_lines:
            if lines:
                all_text = " ".join([line['text'].strip() for line in lines])
                text_content = Content(content_type=ContentType.TEXT, original=all_text)
                text_content.font_size = self._get_para_font_size(lines)
                text_content.is_bold = self._get_para_is_bold(lines)
                text_content.leading = self._get_para_font_height(lines) * 1.2
                text_content.first_line_offset = self._get_line_first_offset(lines, page_left)
                text_content.text_color = self._get_para_text_color(lines)
                text_content.top_y = lines[0]['chars'][0]['y0']
                contents.append(text_content)

        for image in images:
            image_content = ImageContent(image)
            image_content.top_y = image['y0']
            contents.append(image_content)

        contents.sort(key=lambda x: x.top_y, reverse=True)

        page.contents = contents

        return page

    # 判读PDF的一行是否是段尾
    def _is_para_tail(self, page: pdfplumber.pdf.Page, line: any, idx: int, total: int) -> bool:
        if line['x1'] / page.width < 0.8: return True
        if line['text'].strip()[-1] in ['.', '"', '”', '?', '。', '!', ';']: return True
        if idx == total - 1: return True
        return False

    def _get_all_left(self, page: pdfplumber.pdf.Page, lines: any):
        lefts = []
        for line in lines:
            if line['chars']:
                lefts.append(line['chars'][0]['x0'])
        if lefts:
            element_counts = Counter(lefts)
            most_common_element = element_counts.most_common(1)[0]
            most_common_value = most_common_element[0]
            return most_common_value
        else:
            return 20

    def _get_all_right(self, page: pdfplumber.pdf.Page, lines: any):
        rights = []
        for line in lines:
            if line['chars']:
                rights.append(line['chars'][len(line['chars']) - 1]['x1'])
        if rights:
            return max(rights)
        else:
            return page.width - 20

    # 获取段落的首行缩进
    def _get_line_first_offset(self, lines: any, all_left: any):
        if lines:
            if lines[0]['chars']:
                return max(0, lines[0]['chars'][0]['x0'] - all_left)
        return 0

    def _get_para_top(self, lines: any):
        if lines:
            if lines[0]['chars']:
                return lines[0]['chars'][0]['y0']
        return 0

    def _get_para_font_size(self, lines: any):
        values = []
        for line in lines:
            if line['chars']:
                for char_info in line['chars']:
                    values.append(char_info['size'])
        if values:
            element_counts = Counter(values)
            most_common_element = element_counts.most_common(1)[0]
            most_common_value = most_common_element[0]
            return most_common_value
        else:
            return 24

    def _get_para_font_height(self, lines: any):
        values = []
        for line in lines:
            if line['chars']:
                for char_info in line['chars']:
                    values.append(char_info['height'])
        if values:
            element_counts = Counter(values)
            most_common_element = element_counts.most_common(1)[0]
            most_common_value = most_common_element[0]
            return most_common_value
        else:
            return 24

    def _get_para_text_color(self, lines: any):
        values = []
        for line in lines:
            if line['chars']:
                for char_info in line['chars']:
                    values.append(char_info['non_stroking_color'])
        if values:
            element_counts = Counter(values)
            most_common_element = element_counts.most_common(1)[0]
            most_common_value = most_common_element[0]
            return most_common_value
        else:
            return (0, 0, 0)

    def _get_para_is_bold(self, lines: any):
        values = []
        for line in lines:
            if line['chars']:
                for char_info in line['chars']:
                    values.append(char_info['fontname'])
        if values:
            element_counts = Counter(values)
            most_common_element = element_counts.most_common(1)[0]
            most_common_value = most_common_element[0]
            return 'bold' in most_common_value.lower()
        else:
            return False

    def _get_col_widths(self, width: float, count: int) -> [float]:
        item_width = width / count
        return [item_width] * count
