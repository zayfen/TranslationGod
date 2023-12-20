#!/usr/bin/env python
#coding: utf-8

"""
Provide a chatgpt translate feature
"""

import os
import abc
import time
from openai import OpenAI
from answer_parser import parse_translate_answer


def build_translate_prompt(source_text_list, source_language, to_languages):
    content = "\n".join([f'- "{text}"' for text in source_text_list])

    return f"""
I want you act as a translator. I will give you the following sentences in {source_language}:

{content}

For the following languages: {", ".join(to_languages)}, your task is to generate JSON output for each language following the next rules:
- Keys will always be number starting from 0 and increasing sequentially
- Values will only be the translation sentence
- Do not write explanations
"""


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
    def __init__(self, mode="gpt-3.5-turbo", frequcency=3):
        """
        @Param { model } - ChatGPT model
        @Param { frequcency } - Requests per minute
        """
        # max translate 100 text entries each time
        self.client = OpenAI(
            # api_key="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",
            # api_key="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",
        )


        self.MAX_ENTRIES = 100
        self._frequcency = frequcency

        self.model = mode
        self.role = 'Your are a translation expert'
        self.answer = ''

        self.json_dict = None
        self.source_language = "Chinese"
        self.target_languages = []

        # output contains { [language]: {translated_json } }
        self.output = {}

    def messages(self):
        # return [{ "role": "system", "content": self.role }]
        return []

    def translate(self, text_list, to_languages, source_language="Chinese"):
        _messages = self.messages()

        prompt = build_translate_prompt(text_list, source_language, to_languages)
        _messages.append({ "role": "user", "content": prompt })

        print(f"Translating from {source_language} to {to_languages}")

        chat_completion = self.client.chat.completions.create(model=self.model,
        temperature = 0.8,
        # max_tokens = 100,
        # top_p = 1,
        # frequency_penalty = 0,
        # presence_penalty = 0,
        messages=_messages)

        answer_content = chat_completion.choices[0].message.content
        self.answer = answer_content
        print(f"\n\n{self.answer}\n\n")

        # sleep for 60/self.frequency
        sleep_seconds = 60 / self._frequcency
        time.sleep(sleep_seconds)

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

        while start_index < len(_json_dict_values):
            _json_dict_values_chunk = _json_dict_values[start_index:end_index]

            start_index = start_index + self.MAX_ENTRIES
            end_index = start_index + self.MAX_ENTRIES

            #FIXME: 单个语言翻译，准确率更高，多个语言一起翻译不太稳定.
            for to_language in to_languages:
                _answer_chunk = self.translate(_json_dict_values_chunk, [to_language], source_language)
                _result_chunk = parse_translate_answer(_answer_chunk, [to_language])

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

                if len(_json_dict_keys) > len(translated_values):
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
