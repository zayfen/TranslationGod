#!/usr/bin/env python
# coding: utf-8

"""
Module providing a feature to collect all JSON entries in files
"""

import os, json
import esprima
from functools import reduce
import pandas as pd

from config import EXCEL_FILE_NAME
from chatgpt_service import ChatGPTTranslator
from options_parser import Command, Options, parse_option
from helpers import copy_file, diff_dict, merge_json_dict



# Context
SOURCE_LOCALE = None
TARGET_LOCALES = []


def get_filename_from_filepath(filepath):
    return os.path.basename(filepath)


def get_abspath_from_relative(_path, root=os.path.curdir) -> str:
    root_dir = os.path.dirname(root)
    return os.path.abspath(os.path.join(root_dir, _path))


def list_files_in_directory(directory):
    """
    list all file in directory recursively
    """
    collected_files = []

    for root, _dirs, files in os.walk(directory):
        for filename in files:
            abs_path = os.path.abspath(os.path.join(root, filename))
            collected_files.append(abs_path)

    return collected_files


def parse_json_object_in_javascript_file(javascript_file_path, filepath_map_json_dict):
    """
    parse json object in javascript/typescript file,
    and retrive all key-value pairs
    """

    with open(javascript_file_path, encoding="utf-8") as file:
        source_code = file.read()
        pure_json = javascript_file_path.endswith(".json")
        if pure_json:
            source_code = "export default " + source_code

        syntax_tree = esprima.parseModule(source_code)
        syntax_tree_dict = syntax_tree.toDict()
        object_expr_path = ("body", 0, "declaration")
        object_expr = reduce(
            lambda tree, prop: tree[prop], object_expr_path, syntax_tree_dict
        )

        json_dict = parse_object_expression(object_expr)
        filepath_map_json_dict[javascript_file_path] = json_dict

    return filepath_map_json_dict


def parse_object_expression(object_expr):
    """
    parse object expression of javascript
    """
    kv_collection = {}
    properties = object_expr["properties"]
    for item in properties:
        key_node = item["key"]
        value_node = item["value"]

        # key_node['type'] is Literal or Identifier, for Literal use 'value' else use 'name'
        item_key = (
            key_node["value"] if key_node["type"] == "Literal" else key_node["name"]
        )
        item_value = value_node["value"]
        kv_collection[item_key] = item_value

    return kv_collection


def write_json_dict_to_excel(path_map_json_dict, output_filepath=EXCEL_FILE_NAME):
    """
    write json dict to excel file
    """
    dir_path = os.path.dirname(output_filepath) or "."
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # basename maybe "" xxx, yyy.xlsx
    basename = os.path.basename(output_filepath)

    output_filepath = os.path.join(
        dir_path, EXCEL_FILE_NAME if basename == "" else basename
    )
    excel_writer = pd.ExcelWriter(output_filepath, engine="xlsxwriter")

    extend = "xlsx"
    output_filename_without_extend = output_filepath
    if output_filepath.endswith("." + extend):
        output_filename_without_extend = output_filepath[0 : (0 - len("." + extend))]

    output_map_filename = ".".join([output_filename_without_extend, "map", extend])

    excel_map_writer = pd.ExcelWriter(output_map_filename, engine="xlsxwriter")

    for path, json_dict in path_map_json_dict.items():
        # take one sheet every path
        filename = get_filename_from_filepath(path)
        data_set = {}
        map_data_set = {}

        source_locale_series = []
        data_set[SOURCE_LOCALE] = source_locale_series

        map_source_locale_series = []
        map_data_set[SOURCE_LOCALE] = map_source_locale_series

        for key, value in json_dict.items():
            source_locale_series.append(value)
            map_source_locale_series.append(key)

        for target_locale in TARGET_LOCALES:
            data_set[target_locale] = [None] * len(source_locale_series)
            map_data_set[target_locale] = [None] * len(source_locale_series)

        dataframe = pd.DataFrame(data_set)
        # remove default index column
        dataframe.set_index(SOURCE_LOCALE, inplace=True)
        dataframe.to_excel(excel_writer, sheet_name=filename)

        map_dataframe = pd.DataFrame(map_data_set)
        # remove default index column
        map_dataframe.set_index(SOURCE_LOCALE, inplace=True)
        map_dataframe.to_excel(excel_map_writer, sheet_name=filename)

    excel_writer.close()
    excel_map_writer.close()


def write_excel_to_javascript_file(excel_file_path, excel_map_file_path, output_dir):
    """
    write excel to json(javascript) back
    output json file name named as excel sheet name
    """
    # excel_map_file_path必须存在，如果不存在此文件，则表示没有对应的json文件，直接忽略
    if not os.path.exists(excel_map_file_path):
        raise Exception(f"{excel_map_file_path} don't exist!")

    try:
        excel_reader = pd.ExcelFile(excel_file_path)
        excel_map_reader = pd.ExcelFile(excel_map_file_path)
        print(excel_reader.sheet_names)
        sheet_names = excel_reader.sheet_names

        for sheet_name in sheet_names:
            dataframe = excel_reader.parse(sheet_name=sheet_name)
            dataframe_dict = dataframe.to_dict()

            # get json key
            map_dataframe = excel_map_reader.parse(sheet_name=sheet_name)
            map_dataframe_dict = map_dataframe.to_dict()

            # json_keys_dict lick {0: 'key1', 1: 'key2',... }
            json_keys_dict = map_dataframe_dict[SOURCE_LOCALE]
            json_keys = json_keys_dict.values()

            for key, series_dict in dataframe_dict.items():
                # key is column name, here it's language
                # series_dict is text list translated
                print("Language: ", key)

                # ignore source locale
                if key == SOURCE_LOCALE:
                    continue

                pure_json = sheet_name.endswith(".json")

                write_json_kv_list_to_javascript_file(
                    os.path.join(output_dir, key),
                    sheet_name,
                    json_keys,
                    series_dict.values(),
                    pure_json,
                )

    except IOError as err:
        print("Read excel error: ", err)
    else:
        excel_reader.close()
        excel_map_reader.close()


def write_json_kv_list_to_javascript_file(
    out_dir, filename, key_list, value_list, pure_json=True
):
    """
    write json [key, value] to out_dir/filename
    """
    pairs = zip(key_list, value_list)
    json_dict = {}

    for item in pairs:
        key = item[0]
        value = item[1]
        json_dict[key] = value

    write_json_to_javascript_file(out_dir, filename, json_dict, pure_json)


def _write_json_to_javascript_file(file_path, json_dict, pure_json=True):
    """
    Write json_dict to file_path
    """
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    print(f"Writing {file_path} ...")

    with open(file_path, "w+", encoding="utf-8") as file:
        json_str = json.dumps(json_dict, indent=2, ensure_ascii=False)
        final_code = json_str if pure_json else f"export default {json_str}"
        file.write(final_code)

def write_json_to_javascript_file(out_dir, filename, json_dict, pure_json=True):
    """
    Write json_dict to file
    """
    file_path = os.path.abspath(os.path.join(out_dir, filename))
    _write_json_to_javascript_file(file_path, json_dict, pure_json)

# Commands


def translate_json_directory_or_file(opt: Options):
    """
    Translate json file or  files in directory
    """

    input_path = get_abspath_from_relative(opt.input)
    input_path_existed = os.path.exists(input_path)
    if not input_path_existed:
        raise Exception(f"{input_path} don't exist!")

    input_is_dir = os.path.isdir(input_path)
    json_file_path_list = []
    if input_is_dir:
        file_path_list = list_files_in_directory(input_path)
        avaiable_file_extends = [".json", ".ts", ".js"]
        json_file_path_list = list(
            filter(
                lambda _path: any(
                    [_path.endswith(extend) for extend in avaiable_file_extends]
                ),
                file_path_list,
            )
        )
    else:
        json_file_path_list.append(input_path)

    filepath_map_json_dict = {}
    for json_file_path in json_file_path_list:
        parse_json_object_in_javascript_file(json_file_path, filepath_map_json_dict)

    target_langs = opt.target_langs
    output_path = opt.output
    abs_output_path = get_abspath_from_relative(output_path)

    items = filepath_map_json_dict.items()
    t = ChatGPTTranslator(opt.model, opt.frequency)

    for filepath, json_dict in items:
        filename = get_filename_from_filepath(filepath)
        purse_josn = filename.endswith(".json")

        t.reset()
        translated_result = t.translate_json_dict(json_dict, target_langs)

        for language, translated_json_dict in translated_result.items():
            write_json_to_javascript_file(
                f"{abs_output_path}/{language}/",
                filename,
                translated_json_dict,
                purse_josn,
            )


def translate_excel_file(opt: Options):
    """
    Translate excel file
    """
    raise NotImplementedError("Don't support translating excel file yet!")


def convert_json_directory_to_excel(opt: Options):
    """
    Convert json files in directory to .xlsx and .map.xlsx
    """

    input_path = get_abspath_from_relative(opt.input)
    input_path_existed = os.path.exists(input_path)
    if not input_path_existed:
        raise Exception(f"{input_path} doesn't exist!")

    input_is_dir = os.path.isdir(input_path)

    filepath_map_json_dict = {}
    filepath_list = (
        list_files_in_directory(input_path) if input_is_dir else [input_path]
    )

    for filepath in filepath_list:
        parse_json_object_in_javascript_file(filepath, filepath_map_json_dict)

    output_path = get_abspath_from_relative(opt.output)
    write_json_dict_to_excel(filepath_map_json_dict, output_path)

    filepath_map_json_dict = None


def convert_excel_to_json_files(opt: Options):
    """
    Convert .xlsx and .map.xlsx to json files
    """
    input_file_path = get_abspath_from_relative(opt.input)
    input_path_existed = os.path.exists(input_file_path)
    if not input_path_existed:
        raise Exception(f"{input_file_path} doesn't exist!")

    extend = "xlsx"
    input_file_path_without_extend = input_file_path
    if input_file_path.endswith("." + extend):
        input_file_path_without_extend = input_file_path[0 : (0 - len("." + extend))]

    input_map_file_path = ".".join([input_file_path_without_extend, "map", extend])
    if not os.path.exists(input_map_file_path):
        raise Exception(f"{input_map_file_path} doesn't exist!")
    output_path = get_abspath_from_relative(opt.output)
    write_excel_to_javascript_file(input_file_path, input_map_file_path, output_path)


def generate_langs_diff(opt: Options):
    """
    Generate lang diff, output to directory
    """
    source_lang = opt.source_lang
    source_relative_path = os.path.join(opt.input, source_lang)
    source_input_dir_path = get_abspath_from_relative(source_relative_path)
    print(f"{source_input_dir_path=}")
    input_path_existed = os.path.exists(source_input_dir_path)
    if not input_path_existed:
        raise Exception(f"{source_input_dir_path} doesn't exist!")

    output_dir_path = get_abspath_from_relative(opt.output)
    print(f"{output_dir_path=}")

    input_is_dir = os.path.isdir(source_input_dir_path)
    json_file_path_list = []
    if input_is_dir:
        file_path_list = list_files_in_directory(source_input_dir_path)
        avaiable_file_extends = [".json", ".ts", ".js"]
        json_file_path_list = list(
            filter(
                lambda _path: any(
                    [_path.endswith(extend) for extend in avaiable_file_extends]
                ),
                file_path_list,
            )
        )
    else:
        json_file_path_list.append(source_input_dir_path)

    filepath_map_json_dict = {}

    for filepath in json_file_path_list:
        parse_json_object_in_javascript_file(filepath, filepath_map_json_dict)

    input_path_len = len(source_input_dir_path)
    for filepath, json_dict in filepath_map_json_dict.items():
        relative_path = filepath[input_path_len:]

        for lang in opt.target_langs:
            target_relative_path = os.path.normpath(
                os.path.join(lang, f".{relative_path}")
            )
            target_input_file_path = os.path.join(opt.input, target_relative_path)
            target_filepath_map_json_dict = {}
            if os.path.exists(target_input_file_path):
                parse_json_object_in_javascript_file(target_input_file_path, target_filepath_map_json_dict)

            target_json_dict = target_filepath_map_json_dict.get(target_input_file_path) or {}
            diff_json_dict = diff_dict(json_dict, target_json_dict)

            print(f"{target_input_file_path=}")
            target_output_file_path = os.path.join(output_dir_path, target_relative_path)
            print(f"{target_output_file_path=}")

            pure_json = filepath.endswith(".json")
            _write_json_to_javascript_file(target_output_file_path, diff_json_dict, pure_json)


def merge_json(opt):
    """
    Merge source json file to target json
    """
    input_dir_path = get_abspath_from_relative(opt.input)
    input_dir_path_existed = os.path.exists(input_dir_path)
    if not input_dir_path_existed:
        raise Exception(f"{input_dir_path} doesn't exist!")
    
    assert os.path.isdir(input_dir_path)
    
    output_dir_path = get_abspath_from_relative(opt.output)
    print(f"{output_dir_path=}")
    output_dir_path_existed = os.path.exists(output_dir_path)
    if not output_dir_path_existed:
        raise Exception(f"{output_dir_path} doesn't exist")

    assert os.path.isdir(output_dir_path)

    # for each file in input dir, merge it to file mathed input file in output directory.
    file_path_list = list_files_in_directory(input_dir_path)
    input_dir_path_len = len(input_dir_path)
    for input_file_path in file_path_list:
        relative_input_path = input_file_path[input_dir_path_len+1:]
        output_file_path = os.path.join(output_dir_path, relative_input_path)

        if not os.path.exists(output_file_path):
            # copy input_file_path to output_file_path
            print(f"Copy {input_file_path} to {output_file_path}")
            copy_file(input_file_path, output_file_path)
            continue
        
        json_dict = {}
        parse_json_object_in_javascript_file(input_file_path, json_dict)
        parse_json_object_in_javascript_file(output_file_path, json_dict)

        output_json_dict = json_dict.get(output_file_path)
        input_json_dict = json_dict.get(input_file_path)

        final_output_json_dict = merge_json_dict(output_json_dict, input_json_dict)
        pure_json = output_file_path.endswith(".json")
        _write_json_to_javascript_file(output_file_path, final_output_json_dict, pure_json)
        
    

def main():
    opt = parse_option()

    global SOURCE_LOCALE
    global TARGET_LOCALES

    SOURCE_LOCALE = opt.source_lang
    TARGET_LOCALES = opt.target_langs

    print(opt)

    if opt.command == Command.CONVERT_JSON_TO_EXCEL:
        convert_json_directory_to_excel(opt)
    elif opt.command == Command.GENERATE_LANGS_DIFF:
        # generate diff locales
        generate_langs_diff(opt)
    elif opt.command == Command.MERGE_JSON:
        merge_json(opt)
    elif opt.command == Command.TRANSLATE_JSON_FILES:
        translate_json_directory_or_file(opt)
    elif opt.command == Command.TRANSLATE_EXCEL_FILE:
        translate_excel_file(opt)
    elif opt.command == Command.CONVERT_EXCEL_TO_JSON:
        convert_excel_to_json_files(opt)
    else:
        raise Exception(
            "Please pass correct arguments! If you don't know how, please check 'tg -h' for help"
        )


if __name__ == "__main__":
    main()
