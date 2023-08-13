import argparse


class ArgumentParser:
    parser: argparse.ArgumentParser

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="PDF翻译器")

        self.parser.add_argument(
            '--config',
            type=str,
            default="config.yaml",
            help="配置文件的地址",
        )

        self.parser.add_argument(
            "--model_type",
            type=str,
            required=True,
            choices=["GLMModel", "OpenAIModel"],
            help="大模型类型",
        )

        self.parser.add_argument(
            "--glm_model_url",
            type=str,
            help="GLMModel 的 URL 地址"
        )

        self.parser.add_argument(
            "--timeout",
            type=int,
            default=20,
            help="API请求的超时时间，单位：秒"
        )

        self.parser.add_argument(
            "--openai_model",
            type=str,
            help="OpenAI的Model，当`model_type=OpenAIModel`时，该选项必填",
        )

        self.parser.add_argument(
            "--openai_api_key",
            type=str,
            help="OpenAI的ApiKey，当`model_type=OpenAIModel`时，该选项必填",
        )

        self.parser.add_argument(
            "--book",
            type=str,
            help="PDF文件的地址",
        )

        self.parser.add_argument(
            "--file_format",
            type=str,
            help="PDF文件的的`format`",
        )

    def parse_arguments(self):
        args = self.parser.parse_args()
        if args.model_type == "OpenAIModel" and (not args.openai_api_key or not args.openai_model):
            self.parser.error("当`model_type=OpenAIModel`时，`--openai_api_key`和`--openai_model`为必填项")
        return args
