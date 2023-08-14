import requests

from simplejson import errors as simplejson_errors

from .model import Model


class QWenModel(Model):
    # 大模型的请求地址
    api_url: str

    # 请求需要的`Key`
    api_key: str

    # 请求超时的时间，单位：秒
    timeout: int

    def __init__(self, api_url: str, api_key: str, timeout: int):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def make_request(self, prompt) -> (str, bool):
        try:
            payload = {
                "model": "qwen-v1",
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                }
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.post(url=self.api_url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            response_dict = response.json()
            translation = response_dict['output']['text']
            return translation, True
        except requests.exceptions.Timeout as e:
            raise Exception(f"请求超时：{e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常：{e}")
        except simplejson_errors.JSONDecodeError as e:
            raise Exception("JSON解析错误：{e}")
        except Exception as e:
            return Exception(f"发生了未知错误：{e}")
