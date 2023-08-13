from .content import Content


class Page:
    # `Content`数组，一个`PDF`页面，会包含多个不同的`Content`
    contents: [Content]

    # 左侧边距
    left_margin: float

    # 右侧边距
    right_margin: float

    # 顶部边距
    top_margin: float

    # 底部边距
    bottom_margin: float

    # 构造函数
    def __init__(self):
        self.contents = []

    # 添加一个`Content`
    def add_content(self, content: Content):
        self.contents.append(content)
