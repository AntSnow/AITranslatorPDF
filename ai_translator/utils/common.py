class Common:

    @classmethod
    def model_base_info(cls) -> list[dict]:
        return [
            {
                "name": "OpenAIModel",
                "models": ["gpt-3.5-turbo"],
                "required": ["api_key"]
            },
            {
                "name": "GLMModel",
                "models": ["chatglm-6b"],
                "required": ["model_url", "timeout"]
            },
            {
                "name": "QWenModel",
                "models": ["qwen-v1"],
                "required": ["api_key", "api_url", "timeout"]
            }
        ]

    @classmethod
    def model_types(cls) -> list[str]:
        return [info["name"] for info in Common.model_base_info()]

    @classmethod
    def model_info(cls, model_type: str) -> dict:
        for info in Common.model_base_info():
            if info['name'] == model_type:
                return info
        return {}

    @classmethod
    def model_names(cls, model_type: str) -> list:
        return Common.model_info(model_type)['models']

    @classmethod
    def model_required(cls, model_type: str) -> list:
        return Common.model_info(model_type)['required']

    @classmethod
    def model_if_need_key(cls, model_type: str) -> bool:
        return Common.model_info(model_type)['APIKey']
