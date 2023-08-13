import openai
import requests

from simplejson import errors as simplejson_errors

from model import Model
from ai_translator.utils import LOG


class OpenAIModel(Model):
    # 模型名称
    model: str

    def __init__(self, model: str, api_key: str):
        self.model = model
        openai.api_key = api_key

    def make_request(self, prompt) -> (str, bool):

        # `Debug`调试使用
        if "请输入你自己的" in openai.api_key:
            text_0 = "翻译为中文，不要添加多余信息："
            text_1 = "翻译为中文，不要添加多余信息，保持间距（空格、分隔符），以表格形式返回：\n"
            if text_1 in prompt:
                return prompt[len(text_1):], True
            if text_0 in prompt:
                return prompt[len(text_0):], True

        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt-3.5-turbo":
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message['content'].strip()
                else:
                    response = openai.Completion.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()
                return translation, True
            except openai.error.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning("请求频率受限，等待60秒之后重试")
                else:
                    raise Exception("请求受限，已达到最大请求次数限制")
            except requests.exceptions.Timeout as e:
                raise Exception(f"请求超时：{e}")
            except requests.exceptions.RequestException as e:
                raise Exception(f"请求异常：{e}")
            except simplejson_errors.JSONDecodeError as e:
                raise Exception("JSON解析错误：{e}")
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
