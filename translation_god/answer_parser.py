#coding: utf-8

import json

def parse_translate_answer(answer, to_languages):
   """
   parse gpt answer, pick json
   """""
   result = {}

   # 放置结尾没有换行符
   answer = answer + '\n'
   last_cursor = 0

   for language in to_languages:
       remaing_answer = answer
       search_tag = f"{language}:\n"
       index = remaing_answer.find(search_tag, 0)
       if index == -1:
          print(f"parse_translate_answer: can't find language {language}")
          index = last_cursor
           # raise Exception(f"parse_translate_answer: can't find language {language}")

       remaing_answer = remaing_answer[index:]

       # find json start char '{'
       json_start_index = remaing_answer.find('{\n')

       # find json end char '}'
       json_end_index = remaing_answer.find('}\n')

       # update json_end_index
       last_cursor = json_end_index if json_end_index > -1 else last_cursor

       json_str = remaing_answer[json_start_index:(json_end_index+1)]
       print(f"{json_str= }")

       try:
          json_dict = json.loads(json_str)

          # collect translations
          result[language] = list(json_dict.values())
       except Exception as err:
         print(f"Fro {language} parse error: {json_start_index}, {json_end_index} \n {json_str}")

   return result


if __name__ == "__main__":
    with open('./translation_god/errcode.txt', "r") as f:
        answer = f.read()
        result = parse_translate_answer(answer, ['Traditional Chinese', 'French', 'German', 'Thai', 'Italian', 'Spanish', 'Dutch'])
        print(result)
