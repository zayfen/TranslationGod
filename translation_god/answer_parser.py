#coding: utf-8

import json
import re

from pick_json import pick_json



def parse_translate_answer(answer, to_languages):
   """
   parse gpt answer, pick json
   """""
   # json_dict_list 和 to_languages 的元素一一对应
   json_dict_list = pick_json(answer)
   result = {}

   for index in range(len(json_dict_list)):
      json_dict = json_dict_list[index]
      lang = to_languages[index]
      result[lang] = list(json_dict.values())

   print(f"Translation Result: \n {result}\n")
   return result


if __name__ == "__main__":
    with open('./translation_god/errcode.txt', "r") as f:
        answer = f.read()
        result = parse_translate_answer(answer, ['Traditional Chinese', 'French', 'German', 'Thai', 'Italian', 'Spanish', 'Dutch'])
        print(result)
