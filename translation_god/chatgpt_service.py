#!/usr/bin/env python
#coding: utf-8

"""
Provide a chatgpt translate feature
"""

import os
import abc
from openai import OpenAI
from answer_parser import parse_translate_answer

client = OpenAI(
    # api_key="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",
    api_key="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",
    # default max_retries is 2
    max_retries = 0
)

def build_translate_prompt(source_text_list, source_language, to_languages):

    content = "\n".join([f'- "{text}"' for text in source_text_list])


    # Your task is to translate them to the following languages: English, Japanese, French, and generate a json output for each language following the next rules:\n- Keys will always be number starting from 0 and increasing sequentially\n- Values will be the translations

    return f"""
From the following texts written in {source_language}:

{content}

For the following languages: {", ".join(to_languages)}, your task is to generate a json output for each language following the next rules:
- Keys will always be number starting from 0 and increasing sequentially
- Values will be the translations
- All texts must be translated"""


class Translator(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return (
            hasattr(__subclass, 'translate') and
            callable(__subclass.translate) or NotImplemented)

    @abc.abstractmethod
    def translate(self, content, to_languages, source_language="Chinese"):
        print("Please implement translate in subclass")
        pass


class ChatGPTTranslator(Translator):
    def __init__(self):
        # max translate 100 text entries each time
        self.MAX_ENTRIES = 400

        self.model = "gpt-3.5-turbo-16k"
        self.role = 'Your are a translation expert'
        self.answer = ''

        self.json_dict = None
        self.source_language = "Chinese"
        self.target_languages = []

        # output contains { [language]: {translated_json } }
        self.output = {}

    def messages(self):
        return [{ "role": "system", "content": self.role }]

    def translate(self, text_list, to_languages, source_language="Chinese"):
        _messages = self.messages()

        prompt = build_translate_prompt(text_list, source_language, to_languages)
        _messages.append({ "role": "user", "content": prompt })

        print(f"""User:
            {_messages}
        """)

        chat_completion = client.chat.completions.create(model=self.model,
        # temperature = 0.7,
        # max_tokens = 100,
        # top_p = 1,
        # frequency_penalty = 0,
        # presence_penalty = 0,
        messages=_messages)

        answer_content = chat_completion.choices[0].message.content
        self.answer = answer_content
        print(f"\n\n{self.answer}\n\n")
        return self.answer


    def translate_json_dict(self, json_dict, to_languages, source_language="Chinese"):
        """
        translate json dict, return a dict which contains language and all translated texts
        """
        self.json_dict = json_dict
        _json_dict_keys = list(json_dict.keys())
        _json_dict_values = list(json_dict.values())

        start_index = 0
        end_index = start_index + self.MAX_ENTRIES

        answer = []

        # language map text list
        translated_text_list = {}

        while start_index < (len(_json_dict_values) - 1):
            _json_dict_values_chunk = _json_dict_values[start_index:end_index]

            start_index = start_index + self.MAX_ENTRIES
            end_index = start_index + self.MAX_ENTRIES

            _answer_chunk = self.translate(_json_dict_values_chunk, to_languages, source_language)
            _result_chunk = parse_translate_answer(_answer_chunk, to_languages)

            # merge into reuslt
            for (language, text_list) in _result_chunk.items():
                if translated_text_list.get(language):
                    translated_text_list[language] = translated_text_list[language] + text_list
                else:
                    translated_text_list[language] = text_list

            answer.append(_answer_chunk)

            result_json_dict = {}
            for language in to_languages:
                translated_values = translated_text_list[language]

                if len(_json_dict_keys) != len(translated_values):
                    print(f"{language} did not translate completely! Miss {len(_json_dict_keys) - len(translated_values)} entries!")
                    # raise Exception(f"{language} did not translate completely! Miss {len(_json_dict_keys) - len(translated_values)} entries!")

                zipped = zip(_json_dict_keys, translated_values)
                result_json_dict[language] = dict(zipped)

        return result_json_dict


    def reset(self ):
        self.answer = ''

        self.json_dict = None
        self.source_language = "Chinese"
        self.target_languages = []

        # output contains { [language]: {translated_json } }
        self.output = {}


if __name__ == "__main__":
    t = ChatGPTTranslator()

    answer = t.translate_json_dict(
        dict({
            "info.hello": "你好",
            "info.今天天气真好": "今天天气真好"
        }),
        ['English', 'Japanese', 'French'])

    print(f"""
ChatGPT:
{answer}
    """)
