from ai_translator.book import Content, ContentType, TableContent


class Model:

    # 获取`TEXT`类型翻译的`prompt`
    # text: 需要翻译的源文本
    # target_language: 需要翻译的目标文本的语言类型
    def get_text_prompt(self, text: str, target_language: str) -> str:
        return f"翻译为{target_language}，不要添加多余信息：{text}"

    # 获取`TABLE`类型翻译的`prompt`
    # text: 需要翻译的源文本
    # target_language: 需要翻译的目标文本的语言类型
    def get_table_prompt(self, table: str, target_language: str) -> str:
        return f"翻译为{target_language}，不要添加多余信息，保持间距（空格、分隔符），以表格形式返回：\n{table}"

    def get_translate_prompt(self, content: Content, target_language: str) -> str:
        if content.content_type == ContentType.TEXT:
            return self.get_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            content: TableContent
            return self.get_table_prompt(content.get_original_as_str(), target_language)

    def make_request(self, prompt) -> (str, bool):
        raise NotImplementedError("子类必须实现该方法")
