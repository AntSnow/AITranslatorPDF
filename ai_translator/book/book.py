from .page import Page

class Book:
    # 声明：`PDF`文件的地址
    pdf_file_path: str

    # 声明：`Page`数组，一个`PDF`会包含多个`Page`
    pages: [Page]

    # 构造函数
    def __init__(self, pdf_file_path):
        self.pdf_file_path = pdf_file_path
        self.pages = []

    # 添加一个`Page`
    def add_page(self, page: Page):
        self.pages.append(page)
