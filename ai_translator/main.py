import sys
import os

# # 将当前脚本的所在目录添加到系统路径
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
project_root = os.path.dirname(script_dir)

# 将项目根目录添加到 Python 路径中
sys.path.append(project_root)

from ai_translator.utils import ArgumentParser, ConfigLoader, LOG
from ai_translator.model import OpenAIModel, QWenModel
from ai_translator.translator import PDFTranslator

if __name__ == "__main__":
    # 创建参数解析器
    argument_parser = ArgumentParser()
    # 解析参数，并返回
    args = argument_parser.parse_arguments()

    # 创建配置加载器
    config_loader = ConfigLoader(args.config)
    # 加载配置参数，并返回
    config = config_loader.load_config()

    # 获取模型名称
    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']

    # 获取 APIKey（优先从参数中读取，其次从配置中读取）
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']

    # 根据模型名称和 APIKey，创建 OpenAIModel
    model = OpenAIModel(model=model_name, api_key=api_key)

    # 获取 Book 文件的路径（优先从参数中读取，其次从配置中读取）
    pdf_file_path = args.book if args.book else config['common']['book']

    # 获取 Book 文件的类型（优先从参数中读取，其次从配置中读取）
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # 实例化 PDFTranslator 类
    translator = PDFTranslator(model)

    # 调用 translate_pdf() 方法
    translator.translate_pdf(pdf_file_path, file_format)
