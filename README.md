# Translation God

Translation God是一个基于ChatGPT的翻译工具。
可以将一个目录下的所有json文件翻译成指定的语言，并按照原始的文件目录结构生成翻译结果。也可以是单个的javascrit文件，只是必须保证js文件的内容格式如下：

``` javascript
export default {
    "key": "value",
    "key2": "value2"
}
```

如果你想用人工翻译，可以将目录下的json文件借助TranslationGod生成一个Excel文件。
Excel文件经过人工翻译完成之后，可以再次借助TranslationGod将Excle文件翻译写入到各个对应语言的目录中，依然是和源语言的目录结构保持一致。

## Install
因为包没有推送到仓库中，所以安装的第一步，需要下载源码tar包，并解压，
进入包目录，会看到setup.py这个文件，安装TranslationGod执行如下命令：

``` bash
pip setup.py install
```
安装成功之后，我们在终端执行 `tg -h` 查看tg的一些参数和使用帮助

## Usage

设置`OPENAI_API_KEY`环境变量

``` bash
export OPENAI_API_KEY="sk-xxxxxxx"
```

### 翻译目录下的JSON文件或者翻译单个JSON文件

``` bash
tg --file=json --sourcelang="Chinese"  --targetlangs="English,Japanese,French" --input="./jsondirectory_or_file" --output="./output"
# or
tg -f json -s Chinese -t "English,Japanese,French" -i "./jsondirectory" -o "./output"
```

### 翻译Excel文件

``` bash
tg --file=excel --sourcelang="Chinese" --input="./my_excel.xlsx" --output="./my_translated_excel.xlsx"

# Or

tg -f excel -s Chinese -i "./my_excel.xlsx" -o "./my_translated_excel.xlsx"
```

### 将目录下的JSON文件转换成Excel文件

``` bash
# this command will produce 2 files, one is output option specified, such as "result.xlsx", the other one is "result.map.xlsx"
tg --file=json --sourcelang="Chinese" --targetlangs="English,Japanese,French" --input="./json_file" --output="./must_end_with_xlsx.xlsx"

# Or

tg -f json -s "Chinese" -t "English,Japanese,French" -i "./json_file" -o "must_end_with_xlsx.xlsx"
```

### 将Excel的文件转换成对应翻译语言的目录和JSON文件

注意：excel文件必须保持TranslationGod生成的格式。

``` bash
# this command will convert result.xlsx and result.map.xlsx to json files
tg --file excel --input "./result.xlsx" --output "outputdir/"

# Or

tg -f excel -i "./result.xlsx" -o "outputdir/"
```
