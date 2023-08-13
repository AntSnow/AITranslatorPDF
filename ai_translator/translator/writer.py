import imghdr
import tempfile
import os

from reportlab.lib import colors, pagesizes, utils
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)

from datetime import datetime

from ..book import Book, Page, Content, ContentType, TableContent
from ..utils import LOG


class Writer:

    # 构造函数
    def __init__(self):
        pass

    # 保存翻译结果
    # book：`Book`对象
    # output_file_path：输出文件的路径
    # file_format：输出文件的格式
    def save_translated_book(self, book: Book, output_file_path: str = None, file_format: str = "PDF"):

        # 如果想要翻译成`PDF`格式，就调用对应的方法
        if file_format.lower() == "pdf":
            self._save_translated_book_pdf(book, output_file_path)

        # 如果想要翻译成`MARKDOWN`格式，就调用对应的方法
        elif file_format.lower() == 'markdown':
            self._save_translated_book_markdown(book, output_file_path)

        # 其他的就暂不支持
        else:
            raise Exception(f"暂时不支持保存为 {file_format} 文件")

    def _save_translated_book_pdf(self, book: Book, output_file_path: str = None):

        # 如果输出路径是`None`，就在原文件路径下创建输出文件
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', '_translated.pdf')

        LOG.info(f"开始翻译")
        LOG.info(f"原`PDF`路径为：{book.pdf_file_path}")
        LOG.info(f"翻译后的`PDF`路径为：{output_file_path}")

        # 注册中文字体
        font_path = "../fonts/simsun.ttc"
        pdfmetrics.registerFont(TTFont('SimSun', font_path))
        pdfmetrics.registerFont(TTFont('SimSun-Bold', font_path))

        left_margin = book.pages[0].left_margin if book.pages else 45
        right_margin = book.pages[0].right_margin if book.pages else 45
        top_margin = book.pages[0].top_margin if book.pages else 30
        bottom_margin = book.pages[0].bottom_margin if book.pages else 30

        # 创建`PDF`文档，`pagesizes`：页面大小，`letter`为标准信纸大小
        doc = SimpleDocTemplate(
            output_file_path,
            pagesizes=pagesizes.letter,
            leftMargin=left_margin,
            rightMargin=right_margin,
            topMargin=top_margin,
            # bottomMargin=bottom_margin,
        )

        # 获取样式表对象
        style = getSampleStyleSheet()

        story = []

        for page_idx, page in enumerate(book.pages):
            for content_idx, content in enumerate(page.contents):

                if content.status:

                    # `TEXT`类型的翻译
                    if content.content_type == ContentType.TEXT:

                        # 获取翻译后的文本
                        text: str = content.translation

                        # 创建文本`Style`
                        simsun_style = ParagraphStyle(
                            'SimSun',
                            fontName="SimSun-Bold" if content.is_bold else "SimSun",
                            fontSize=content.font_size,
                            leading=content.leading,
                            firstLineIndent=content.first_line_offset,
                            spaceBefore=content.space_before,
                            textColor=content.text_color
                        )

                        # 添加段落到`story`中
                        story.append(Paragraph(text, simsun_style))


                    # `TABLE`类型的翻译
                    elif content.content_type == ContentType.TABLE:
                        table = content.translation
                        table_style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ])
                        pdf_table = Table(
                            table.values.tolist(),
                            hAlign="LEFT",
                            colWidths=content.col_widths,
                            spaceBefore=content.space_before,
                        )
                        pdf_table.setStyle(table_style)
                        story.append(pdf_table)

                    elif content.content_type == ContentType.IMAGE:
                        image = content.original
                        img_data = image["stream"].get_data()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".img") as temp_file:
                            temp_file.write(img_data)
                            temp_file_path = temp_file.name
                        image_format = imghdr.what(temp_file_path)
                        temp_file.close()
                        img_data = image["stream"].get_data()
                        if not image_format: continue
                        if not image_format: image_format = "jpeg"
                        img_name = f"images/{str(datetime.timestamp(datetime.now()))}-{page_idx}-{content_idx}.{image_format}"
                        with open(img_name, "wb") as img_file:
                            img_file.write(img_data)
                            img = Image(img_name, width=image["width"], height=image["height"])
                            image_table = Table([[img]], hAlign="LEFT")
                            image_table.setStyle(TableStyle([
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),  # 设置左侧边距
                            ]))
                            story.append(image_table)

            # 如果`page`不是倒数第一页，就添加一个分页符
            if page != book.pages[-1]:
                story.append(PageBreak())

        doc.build(story)

        folder_path = 'images/'
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            os.remove(file_path)

        LOG.info(f"翻译完成：{output_file_path}")

    def _save_translated_book_markdown(self, book: Book, output_file_path: str = None):

        # 如果输出路径是`None`，就在原文件路径下创建输出文件
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', '_translated.md')

        LOG.info(f"开始翻译")
        LOG.info(f"原`PDF`路径为：{book.pdf_file_path}")
        LOG.info(f"翻译后的`PDF`路径为：{output_file_path}")

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for page in book.pages:
                for content in page.contents:
                    if content.status:

                        if content.content_type == ContentType.TEXT:
                            text = content.translation
                            output_file.write(text + '\n\n')

                        elif content.content_type == ContentType.TABLE:
                            table = content.translation
                            header = '| ' + ' | '.join(str(column) for column in table.columns) + ' |' + '\n'
                            separator = '| ' + ' | '.join(['---'] * len(table.columns)) + ' |' + '\n'
                            # body = '\n'.join(['| ' + ' | '.join(row) + ' |' for row in table.values.tolist()]) + '\n\n'
                            body = '\n'.join(
                                ['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in
                                 table.values.tolist()]) + '\n\n'
                            output_file.write(header + separator + body)

                if page != book.pages[-1]:
                    output_file.write('---\n\n')

        LOG.info(f"翻译完成：{output_file_path}")
