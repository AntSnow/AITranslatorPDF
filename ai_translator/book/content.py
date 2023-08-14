import sys, os

# # 将当前脚本的所在目录添加到系统路径
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from enum import Enum, auto
from PIL import Image as PILImage

from ..utils import LOG


class ContentType(Enum):
    # 文本
    TEXT = auto()
    # 标签
    TABLE = auto()
    # 图片
    IMAGE = auto()


class Content:
    # 类型：文本、标签、图片
    content_type: ContentType

    # 原始数据
    original: any

    # 翻译后的数据
    translation: any

    # 状态：是否已经翻译过
    status: False

    # 文本大小
    font_size: float

    # 是否加粗
    is_bold: bool

    # 行高
    leading: float

    # 段落首行缩进
    first_line_offset: float

    # 文字颜色
    text_color: any

    # 段前间距
    space_before: float = 5

    # 顶部的坐标
    top_y: float = 0

    # 构造函数
    def __init__(self, content_type, original, translation=None):
        self.content_type = content_type
        self.original = original
        self.translation = translation
        self.status = False
        self.font_size = 12
        self.is_bold = False

    # 设置状态和翻译后的数据
    def set_translation(self, translation: any, status: bool):
        if not self.check_translator_type(translation):
            raise "ERROR"
        self.translation = translation
        self.status = status

    # 检查`translation`是否和内容类型相匹配
    def check_translator_type(self, translation: any) -> bool:
        if self.content_type == ContentType.TEXT and isinstance(translation, str):
            return True
        elif self.content_type == ContentType.TABLE and isinstance(translation, list):
            return True
        elif self.content_type == ContentType.IMAGE and isinstance(translation, PILImage.Image):
            return True
        else:
            return False


class TableContent(Content):
    df: pd.DataFrame

    col_widths: [float]

    def __init__(self, data, translation=None):

        # 根据`data`，创建`DataFrame`
        df = pd.DataFrame(data)

        if len(data) != len(df) or len(data[0]) != len(df.columns):
            raise ValueError("Error")

        super().__init__(ContentType.TABLE, df)

    def set_translation(self, translation: any, status: bool):
        try:
            if not isinstance(translation, str):
                raise "Error"

            # LOG.debug(translation)

            print(f"66666 translation = {translation}")

            # table_data = [row.strip().split() for row in translation.strip().split("\n")]
            table_data = []
            for row in translation.strip().split("\n"):
                print(f"66666 row = {row}")
                if not row.strip(): continue
                row = row.strip().strip('[]')
                if ", " in row:
                    table_data.append(row.split(", "))
                elif "   " in row:
                    table_data.append(row.split("   "))
                elif "  " in row:
                    table_data.append(row.split("  "))
                else:
                    table_data.append(row.split(" "))

            # LOG.debug(table_data)

            translated_df = pd.DataFrame(table_data)

            # LOG.debug(translated_df)

            self.translation = translated_df

            self.status = status

        except Exception as e:
            LOG.error(f"Error {e}")
            self.translation = None
            self.status = False

    def __str__(self):
        return self.original.to_string(header=False, index=False)

    # 迭代器
    def iter_items(self, translated=False):
        target_df = self.translation if translated else self.original
        for row_idx, row in target_df.iterrows():
            for col_idx, item in enumerate(row):
                yield (row_idx, col_idx, item)

    def update_item(self, row_idx, col_idx, new_value, translated=False):
        target_df = self.translation if translated else self.original
        target_df.at[row_idx, col_idx] = new_value

    # 获取原文的字符串格式
    def get_original_as_str(self) -> str:
        self.original: pd.DataFrame
        text = self.original.to_string(header=False, index=False, line_width=20)
        return text


class ImageContent(Content):
    def __init__(self, image, translation=None):
        super().__init__(ContentType.IMAGE, image)
        self.translation = image
        self.status = True

    def set_translation(self, translation: any, status: bool):
        self.translation = translation
        self.status = status
