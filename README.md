###  # Translation God

Super translation tool.
TG(Translation God) supports translate json files in directory.
TG supports translate excel file into multi language


## Usage

### Translate json files in directory
``` shell

# translate json directory or json fle
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
