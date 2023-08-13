class PageOutOfRangeException(Exception):

    book_pages: int

    requested_pages: int

    def __init__(self, book_pages: int, requested_pages: int):
        self.book_pages = book_pages
        self.requested_pages = requested_pages
        super().__init__(f"PDF请求页码越界：PDF 只有 {self.book_pages} 页，但是请求了第 {self.requested_pages} 页 ")
