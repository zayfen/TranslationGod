# coding: utf-8

"""
translation god params:
--command, -c; values:
* cje: convert json to excel
* gld: generate langs diff from json files
* mj: merge json
* tj: translate json files
* te: translate excel files
* cej: convert excel to json

"""

import argparse
from enum import Enum

__all__ = ["Command", "Options"]


class Command(Enum):
    def __str__(self) -> str:
        return self.value

    CONVERT_JSON_TO_EXCEL = "cje"
    GENERATE_LANGS_DIFF = "gld"
    MERGE_JSON = "mj"
    TRANSLATE_JSON_FILES = "tj"
    TRANSLATE_EXCEL_FILE = "te"
    CONVERT_EXCEL_TO_JSON = "cej"
    UPSERT_ENTRY = "upsert"

    @classmethod
    def load(cls, value: str):
        if value == cls.CONVERT_EXCEL_TO_JSON.value:
            return cls.CONVERT_EXCEL_TO_JSON

        for name, member in cls.__members__.items():
            if member.value == value:
                return member

        return None


class Options:
    def __init__(self) -> None:
        self._command = None
        self._source_lang = None
        self._target_langs = []
        self._input = None
        self._output = None
        self._model = "gpt-3.5-turbo"
        self._frequcency = 3
        self._key = None
        self._value = None

    def set_command(self, command: Command):
        self._command = command

    def set_diff(self, diff):
        self._diff = diff

    def set_source_lang(self, source_lang):
        self._source_lang = source_lang

    def set_target_langs(self, target_langs):
        self._target_langs = target_langs

    def set_model(self, model):
        self._model = model

    def set_input(self, input):
        self._input = input

    def set_output(self, output):
        self._output = output

    def set_frequency(self, frequency):
        self._frequcency = frequency

    def set_key(self, key):
        self._key = key

    def set_value(self, value):
        self._value = value

    @property
    def command(self):
        return self._command

    @property
    def source_lang(self):
        return self._source_lang

    @property
    def target_langs(self):
        return self._target_langs

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @property
    def model(self):
        return self._model

    @property
    def frequency(self):
        return self._frequcency

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    def __str__(self) -> str:
        return str(self.__dict__)


def parse_option() -> Options:
    """
    parse args to construct a option instance of Options class
    """
    parser = argparse.ArgumentParser(
        prog="TranslationGod(tg)",
        description="Super translation tool.",
        epilog="tg is a super translation tool.",
    )
    Command.__members__.values()
    parser.add_argument(
        "-c",
        "--command",
        choices=[member.value for member in Command.__members__.values()],
        dest="command",
        help="Command",
    )

    parser.add_argument(
        "-s",
        "--sourcelang",
        dest="source_lang",
        help="source language to translate from",
    )

    parser.add_argument(
        "-t",
        "--targetlangs",
        dest="target_langs",
        help="target languages translate to, languages should split with ',', e.g. 'English,Japanese,French'",
    )

    parser.add_argument("-i", "--input", dest="input", help="Input file or directory")

    parser.add_argument(
        "-o", "--output", dest="output", help="Output directory or file"
    )

    parser.add_argument("-m", "--model", dest="model", help="Use which ChatGPT model")

    parser.add_argument(
        "-q", "--frequency", dest="frequency", help="How many requests per minute"
    )

    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="The key of translation entry",
    )
    parser.add_argument(
        "-v",
        "--value",
        dest="value",
        help="The value of translation entry",
    )

    args = parser.parse_args()
    opt = Options()

    if args.command:
        opt.set_command(Command.load(args.command))

    if args.source_lang:
        opt.set_source_lang(args.source_lang)

    if args.target_langs:
        # args.target_langs is like "English,French"
        _target_langs = args.target_langs.split(",")
        opt.set_target_langs(_target_langs)

    if args.input:
        opt.set_input(args.input)

    if args.output:
        opt.set_output(args.output)

    if args.model:
        opt.set_model(args.model)

    if args.frequency:
        _frequency = int(args.frequency)
        opt.set_frequency(_frequency)

    if args.key:
        opt.set_key(args.key)

    if args.value:
        opt.set_value(args.value)

    return opt


if __name__ == "__main__":
    opt = parse_option()
    print(opt)
