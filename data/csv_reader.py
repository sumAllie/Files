import pandas as pd
import sys

def process(filepath, saving_path, max_columns):
    if filepath[-3:] == 'tsv':
        df_data = pd.read_csv(filepath, sep='\t')
    else:
        df_data = pd.read_csv(filepath)

    df_data = df_data[:int(max_columns)]
    csv2json(df_data, saving_path)


def csv2json(df_data, saving_path):
    res = '{\n'

    # data columns
    res = res + '\t\"columns\" : [\n'
    keys = df_data.keys()
    key_num = len(keys)
    for i in range(key_num):
        temp_key = "s" + str(i)
        res = res + '\t{\n'
        res = res + '\t\t\"title\":\"' + keys[i].capitalize() + '\",\n'
        res = res + '\t\t\"dataIndex":\"' + temp_key + '\",\n'
        res = res + '\t\t\"key\":\"' + temp_key + '\"\n'
        if i == key_num - 1:
            res = res + '\t}\n'
        else:
            res = res + '\t},\n'
    res = res + '\t],'

    # data source
    data_len = len(df_data)
    res = res + '\n\n\t\"dataSource\" : [\n'
    for i in range(data_len):
        res = res + '\t{\n'
        for k in range(key_num):
            temp_key_k = "s" + str(k)
            res = res + '\t\t\"' + temp_key_k + '\":\"' + str(df_data.loc[i][k])
            if k == key_num - 1:
                res = res + '\"\n'
            else:
                res = res + '\",\n'
        if i == data_len - 1:
            res = res + '\t}\n'
        else:
            res = res + '\t},\n'
    res = res + '\t]'

    res = res + '\n}'
    with open(saving_path, 'w') as f:
        f.write(res)


if __name__ == '__main__':
    # # filepath = "/Users/yuanren/Desktop/FinalProj/tool/SST-2/dev.tsv"
    # filepath = "/Users/yuanren/Desktop/FinalProj/tool/sts/sts-dev.csv"
    # result_savepath = '/Users/yuanren/Desktop/FinalProj/tool/pyCode/table_result.json'
    #
    # max_rows = 10
    # process(filepath, result_savepath, max_rows)

    if len(sys.argv) == 4:
        print("The running filename: '{}'".format(sys.argv[0]))
        print("The data file name: '{}'".format(sys.argv[1]))
        print("The saving file path: '{}'".format(sys.argv[2]))
        print("The maximal number of rows: '{}'".format(sys.argv[3]))
        filepath = sys.argv[1]
        result_savepath = sys.argv[2]
        max_rows = sys.argv[3]

        process(filepath, result_savepath, max_rows)
        print("successfully finished")
    else:
        print("the arguments are not valid")
        print("The number of arguments: '{}'".format(len(sys.argv)))
        for arg in sys.argv:
            print(arg)
