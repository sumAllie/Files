import pandas as pd
from nltk.corpus import stopwords
import sys

stop_words = set(stopwords.words('english'))


def process(filepath, wordcloud_savepath, word_numbers, pie_savepath):
    wc_res, pie_res = process_csv(filepath, word_numbers)
    wordcloud_savefile(wordcloud_savepath, wc_res)
    pie_savefile(pie_savepath, pie_res)


def wordcloud_savefile(savepath, records):
    res = '[\n'
    for record in records:
        res = res + '\t{\n'
        res = res + '\t\tx:\"'+record[0]+'\",\n'
        res = res + '\t\tvalue:'+ str(record[1])+',\n'
        res = res + '\t\tcategory:\"' + str(record[2]) + '\"\n'
        res = res + '\t},\n'
    res = res + ']'
    with open(savepath, 'w') as f:
        f.write(res)

def pie_savefile(savepath, records):
    res = '[\n'
    k = 0
    for record in records:
        k = k + 1
        res = res + '\t{\n'
        res = res + '\t\ttype:\"' + str(record[0]) + '\",\n'
        res = res + '\t\tvalue:' + str(record[1]) + '\n'
        res = res + '\t},\n'
    res = res + ']'
    with open(savepath, 'w') as f:
        f.write(res)


def process_csv(filepath, numbers):
    df_csv = pd.read_csv(filepath, encoding='utf-8')
    label_set = set(df_csv['label'])
    limit = int(numbers)
    wc_res_list = []
    pie_res_list = []
    for label in label_set:
        temp_df = df_csv.loc[df_csv['label'] == label]
        # for pie
        pie_res_list.append([label, len(temp_df)])
        # for wordcloud
        temp_order = dict(statistics(temp_df)[:limit])
        temp_words = temp_order.keys()
        for word in temp_words:
            wc_res_list.append([word, temp_order[word], label])
    wc_res_list.sort(key=lambda x: x[1], reverse=True)
    return wc_res_list[:numbers], pie_res_list


def statistics(df_data):
    dict = {}
    for sentence in df_data['content']:
        for word in sentence.split(sep=' '):
            if word.isalpha() and word not in stop_words:
                if word in dict.keys():
                    dict[word] = dict[word] + 1
                else:
                    dict[word] = 1
    w_order = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    return w_order


if __name__ == '__main__':
    # filepath = "/Users/yuanren/Desktop/FinalProj/tool/SST-2/train.csv"
    # wordcloud_savepath = "wc_result.json"
    # word_numbers = 100
    # pie_savepath = "pie_result.json"
    #
    # process(filepath, wordcloud_savepath, word_numbers, pie_savepath)
    if len(sys.argv) == 5:
        print("The running filename: '{}'".format(sys.argv[0]))
        print("The data file name: '{}'".format(sys.argv[1]))
        print("The saving file path for wordcloud: '{}'".format(sys.argv[2]))
        print("The number of the final words: '{}'".format(sys.argv[3]))
        print("The saving file path for pie: '{}'".format(sys.argv[4]))
        filepath = sys.argv[1]
        wc_savepath = sys.argv[2]
        numbers = int(sys.argv[3])
        pie_savepath = sys.argv[4]
        process(filepath, wc_savepath, numbers, pie_savepath)
        print("successfully finished")
    else:
        print("the arguments are not valid")
        print("The number of arguments: '{}'".format(len(sys.argv)))
        for arg in sys.argv:
            print(arg)
