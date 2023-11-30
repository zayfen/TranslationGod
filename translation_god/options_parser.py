#coding: utf-8

import argparse

class Options:
    def __init__(self) -> None:
        self._file_type = None
        self._source_lang = "Chinese"
        self._target_langs = []
        self._input = None
        self._output = None


    def set_file_type(self, file_type):
        self._file_type = file_type


    def set_source_lang(self, source_lang):
        self._source_lang = source_lang


    def set_target_langs(self, target_langs):
        self._target_langs = target_langs


    def set_input(self, input):
        self._input = input


    def set_output(self, output):
        self._output = output

    @property
    def file_type(self):
        return self._file_type

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

    def __str__(self) -> str:
        return str(self.__dict__)


def parse_option() -> Options:
    """
    parse args to construct a option instance of Options class
    """
    parser = argparse.ArgumentParser(
        prog='TranslationGod(tg)',
        description="Super translation tool.",
        epilog="tg is a super translation tool.")

    parser.add_argument(
        '-f',
        '--file',
        choices=['json', 'excel'],
        dest="file_type",
        help="File type of input")

    parser.add_argument(
        '-s',
        '--sourcelang',
        default="Chinese",
        dest="source_lang",
        help="source language to translate from")

    parser.add_argument(
        '-t',
        '--targetlangs',
        dest="target_langs",
        help="target languages translate to, languages should split with ',', e.g. 'English,Japanese,French'")

    parser.add_argument(
        '-i',
        '--input',
        dest='input',
        help="Input file or directory")

    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        help="Output directory or file")

    args = parser.parse_args()

    opt = Options()
    if args.file_type:
        opt.set_file_type(args.file_type)
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

    return opt



if __name__ == "__main__":
    opt = parse_option()
    print(opt)
