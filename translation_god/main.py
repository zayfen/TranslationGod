#!/usr/bin/env python
# coding: utf-8

"""
Module providing a feature to collect all JSON entries in files
"""

import os, json
import esprima
from functools import reduce
import pandas as pd

from config import EXCEL_FILE_NAME, EXCEL_FILE_MAP_NAME
from chatgpt_service import ChatGPTTranslator
from options_parser import Options, parse_option


# Context
FILEPATH_MAP_JSON_DICT = {}
SOURCE_LOCALE = 'Chinese'
TARGET_LOCALES = ['French', 'German', 'Thai', 'Italian', 'Spanish', 'Dutch', 'Traditional Chinese']



def get_filename_from_filepath(filepath):
    return os.path.basename(filepath)


def get_abspath_from_relative(_path) -> str:
    root = os.path.curdir
    return os.path.abspath(os.path.join(root, filename))


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


def parse_json_object_in_javascript_file(
        javascript_file_path,
        filepath_map_json_dict):
    """
    parse json object in javascript/typescript file,
    and retrive all key-value pairs
    """

    with open(javascript_file_path, encoding="utf-8") as file:
        source_code = file.read()
        syntax_tree = esprima.parseModule(source_code)
        syntax_tree_dict = syntax_tree.toDict()
        object_expr_path = ('body', 0, 'declaration')
        object_expr = reduce(
            lambda tree, prop: tree[prop],
            object_expr_path,
            syntax_tree_dict
        )

        json_dict = parse_object_expression(object_expr)
        filepath_map_json_dict[javascript_file_path] = json_dict

    return filepath_map_json_dict


def parse_object_expression(object_expr):
    """
    parse object expression of javascript
    """
    kv_collection = {}
    properties = object_expr['properties']
    for item in properties:
        key_node = item['key']
        value_node = item['value']

        # key_node['type'] is Literal or Identifier, for Literal use 'value' else use 'name'
        item_key = key_node['value'] if key_node['type'] == 'Literal' else key_node['name']
        item_value = value_node['value']
        kv_collection[item_key] = item_value

    return kv_collection


def write_json_dict_to_excel(path_map_json_dict, output_filename=EXCEL_FILE_NAME):
    """
    write json dict to excel file
    """

    excel_writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

    extend = 'xlsx'
    output_filename_without_extend = output_filename
    if output_filename.endswith('.'+extend):
        output_filename_without_extend = output_filename[0:(0 - len("."+extend))]

    output_map_filename = ".".join([output_filename_without_extend, 'map', extend])

    excel_map_writer = pd.ExcelWriter(output_map_filename, engine='xlsxwriter')

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
        return

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

            for (key, series_dict) in dataframe_dict.items():
                # key is column name, here it's language
                # series_dict is text list translated
                print("Language: ", key)

                # ignore source locale
                if key == SOURCE_LOCALE:
                    continue

                pure_json = sheet_name.endswith(".json")

                write_json_kv_list_to_javascript_file(
                    f"{output_dir}/{key}/",
                    sheet_name,
                    json_keys,
                    series_dict.values(),
                    pure_json
                )

    except IOError as err:
        print("Read excel error: ", err)
    else:
        excel_reader.close()
        excel_map_reader.close()


def write_json_kv_list_to_javascript_file(out_dir, filename, key_list, value_list, pure_json=True):
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


def write_json_to_javascript_file(out_dir, filename, json_dict, pure_json=True):
    """
    Write json_dict to file
    """
    file_path = os.path.abspath(os.path.join(out_dir, filename))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print(f"Writing {file_path} ...")

    with open(file_path, "w+", encoding="utf-8") as file:
        json_str = json.dumps(json_dict, indent=2, ensure_ascii=False)
        final_code = json_str if pure_json else f'export default {json_str}'
        file.write(final_code)



# Commands

def translate_json_directory_or_file(opt: Options):
    """
    Translate json file or  files in directory
    """
    pass

def translate_excel_file(opt: Options):
    """
    Translate excel file
    """
    pass

def convert_json_directory_to_excel(opt: Options):
    """
    Convert json files in directory to .xlsx and .map.xlsx
    """
    filepath_map_json_dict = {}
    filepath_list = list_files_in_directory(dir_path)
    for filepath in filepath_list:
        parse_json_object_in_javascript_file(filepath, filepath_map_json_dict)

    write_json_dict_to_excel(filepath_map_json_dict, opt.output)

    filepath_map_json_dict = None


def convert_excel_to_json_files(opt: Options):
    """
    Convert .xlsx and .map.xlsx to json files
    """
    input_file_path = opt.input
    extend = 'xlsx'
    input_file_path_without_extend = input_file_path
    if input_file_path.endswith('.'+extend):
        input_file_path_without_extend = input_file_path[0:(0 - len("."+extend))]

    input_map_file_path = ".".join([input_file_path_without_extend, 'map', extend])
    write_excel_to_javascript_file(input_file_path, input_map_file_path, opt.output)


def main():
    opt = parse_option()

    if opt.file_type == 'json' and opt.output.endswith('.xlsx'):
        convert_json_directory_to_excel(opt)
    elif opt.file_type == 'json':
        translate_json_directory_or_file(opt)
    elif opt.file_type == 'excel' and opt.output.endswith('.xlsx'):
        translate_excel_file(opt)
    elif opt.file_type == 'excel':
        convert_excel_to_json_files(opt)
    else:
        raise Exception("Please pass correct arguments! If you dont know how, please check 'tg -h' for help")



if __name__ == "__main__":
    main()

    # dir_path = "./test_data/zh-CN/"
    # dir_path = "/home/zhangyunfeng@pudu.com/codeup.aliyun.com/cloud-platform-front/src/locales/zh-CN"

    # filepath_list = list_files_in_directory(dir_path)

    # for filepath in filepath_list:
        # parse_json_object_in_javascript_file(filepath)

    # items = FILEPATH_MAP_JSON_DICT.items()
    # for (filepath, json_dict) in items:
    #     print("filepath: ", filepath)
    #     filename = get_filename_from_filepath(filepath)

    #     # due to pages.ts too large
    #     if filepath.endswith("pages.ts"):
    #         continue

    #     t = ChatGPTTranslator()
    #     t.reset()

    #     translated_result = t.translate_json_dict(json_dict, TARGET_LOCALES)
    #     for (language, translated_json_dict) in translated_result.items():
    #         write_json_to_javascript_file(f"./output/{language}/", filename, translated_json_dict, False)


    # write_json_dict_to_excel(FILEPATH_MAP_JSON_DICT)
    # write_excel_to_javascript_file("./response_yunfeng2.xlsx", "./result.map.xlsx", "./output2/")
