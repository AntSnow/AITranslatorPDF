import sys
import os
import logging

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
project_root = os.path.dirname(script_dir)

# 将项目根目录添加到 Python 路径中
sys.path.append(project_root)

import asyncio

from ai_translator.utils import ArgumentParser, ConfigLoader, LOG
from ai_translator.model import OpenAIModel, QWenModel, Model
from ai_translator.translator import PDFTranslator
from ai_translator.app import Application


async def main():
    # 配置文件的地址
    config_path = 'config.yaml'

    # 创建配置加载器
    config_loader = ConfigLoader(config_path)
    # 加载配置参数，并返回
    config = config_loader.load_config()

    # 获取 Book 文件的路径（优先从参数中读取，其次从配置中读取）
    pdf_file_path = config['common']['book']

    full_pdf_file_path = os.path.abspath(pdf_file_path)

    # App的名称
    app_name = "AITranslatorPDF"

    app = Application(app_name=app_name, pdf_path=full_pdf_file_path, yaml_config=config)

    def app_tap_begin(info):
        print(f"app_tab_begin, info = {info}")

        def translation_bengin(model: Model):
            # 实例化 PDFTranslator 类
            translator = PDFTranslator(model)

            # 调用 translate_pdf() 方法
            translator.translate_pdf(
                pdf_file_path=info['pdf_file_path'],
                output_file_path=info['output_file_path'],
                file_format="PDF",
            )

            # 告诉`App`翻译完成
            app.translation_completed()

        if info['model_type'] == "QWenModel":
            model = QWenModel(
                api_url=info["api_url"],
                api_key=info["api_key"],
                timeout=int(info["timeout"]),
            )
            translation_bengin(model)
        elif info['model_type'] == "OpenAIModel":
            model = OpenAIModel(
                model=info['model_name'],
                api_key=info['api_key']
            )
            translation_bengin(model)
        else:
            LOG.warning(f"不认识的`Model`，{info['model_type']}")

    app.begin_callback = app_tap_begin

    LOG.add(app.logger_callback, format="{message}")

    app.run()


if __name__ == "__main__":
    asyncio.run(main())
