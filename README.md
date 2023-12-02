# Translation God

Super translation tool.
TG(Translation God) supports translate json files in directory.
TG supports translate excel file into multi language

## Install

因为包没有推送到仓库中，所以安装的第一步，需要下载源码tar包，并解压，
进入包目录，会看到setup.py这个文件，安装TranslationGod执行如下命令：

``` shell
pip setup.py install
```
安装成功之后，在环境系统PATH中会存在 `tg`。


## Usage

设置`OPENAI_API_KEY`环境变量

``` shell
export OPENAI_API_KEY="sk-xxxxxxx"
```

### Translate json files in directory

``` shell
tg --file=json --sourcelang="Chinese"  --targetlangs="English,Japanese,French" --input="./jsondirectory_or_file" --output="./output"
# or
tg -f json -s Chinese -t "English,Japanese,French" -i "./jsondirectory" -o "./output"

```

### Translate excel file

``` shell
tg --file=excel --sourcelang="Chinese" --input="./my_excel.xlsx" --output="./my_translated_excel.xlsx"

# Or

tg -f excel -s Chinese -i "./my_excel.xlsx" -o "./my_translated_excel.xlsx"
```

### Convert json file to excel

``` shell
# this command will produce 2 files, one is output option specified, such as "result.xlsx", the other one is "result.map.xlsx"
tg --file=json --sourcelang="Chinese" --targetlangs="English,Japanese,French" --input="./json_file" --output="./must_end_with_xlsx.xlsx"

# Or

tg -f json -s "Chinese" -t "English,Japanese,French" -i "./json_file" -o "must_end_with_xlsx.xlsx"
```

### Convert excel to json files if .map.xlsx file existed

``` shell
# this command will convert result.xlsx and result.map.xlsx to json files
tg --file excel --input "./result.xlsx" --output "outputdir/"

# Or

tg -f excel -i "./result.xlsx" -o "outputdir/"
```
