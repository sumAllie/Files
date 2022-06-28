import pandas as pd
from nltk.corpus import stopwords
import sys

stop_words = set(stopwords.words('english'))


def process(filepath, wordcloud_savepath, word_numbers, pie_savepath):
    wc_res, pie_res = process_csv(filepath, word_numbers)
    wordcloud_savefile(wordcloud_savepath, wc_res)
    pie_savefile(pie_savepath, pie_res)


def process_csv(filepath, numbers):
    df_csv = pd.read_csv(filepath, encoding='utf-8')
    wc_res_list = []
    limit = int(numbers)
    df_1 = df_csv['sentence1']
    df_2 = df_csv['sentence2']
    order_1 = dict(statistics(df_1)[:limit])
    order_2 = dict(statistics(df_2)[:limit])
    words_1 = order_1.keys()
    for word in words_1:
        wc_res_list.append([word, order_1[word], 'sentence1'])
    words_2 = order_2.keys()
    for word in words_2:
        wc_res_list.append([word, order_2[word], 'sentence2'])
    wc_res_list.sort(key=lambda x: x[1], reverse=True)

    pie_res_list = []
    pie_label_list = [int(i) for i in df_csv['label']]
    cnt = len(pie_label_list)
    i = 0
    while True:
        temp_cnt = pie_label_list.count(i)
        i = i + 1
        pie_res_list.append(temp_cnt)
        cnt = cnt - temp_cnt
        if cnt == 0 or i > 50:
            break
    return wc_res_list, pie_res_list


def wordcloud_savefile(savepath, records):
    res = '[\n'
    for record in records:
        res = res + '\t{\n'
        res = res + '\t\tx:\"' + record[0] + '\",\n'
        res = res + '\t\tvalue:' + str(record[1]) + ',\n'
        res = res + '\t\tcategory:\"' + str(record[2]) + '\"\n'
        res = res + '\t},\n'
    res = res + ']'
    with open(savepath, 'w') as f:
        f.write(res)


def pie_savefile(savepath, records):
    res = '[\n'
    for i in range(len(records)):
        if records[i] == 0:
            continue
        res = res + '\t{\n'
        if i == 5:
            res = res + '\t\ttype:\"' + str(i) + '\",\n'
        else:
            res = res + '\t\ttype:\"[' + str(i) + ' ,' + str(i + 1) + ')\",\n'
        res = res + '\t\tvalue:' + str(records[i]) + '\n'
        res = res + '\t},\n'
    res = res + ']'
    with open(savepath, 'w') as f:
        f.write(res)


def statistics(df_data):
    dict = {}
    for sentence in df_data:
        for word in str(sentence).split(sep=' '):
            word = word.lower()
            if word.isalpha() and word not in stop_words:
                if word in dict.keys():
                    dict[word] = dict[word] + 1
                else:
                    dict[word] = 1
    w_order = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    return w_order


if __name__ == '__main__':
    # filepath = "/Users/yuanren/Desktop/FinalProj/tool/sts/sts-dev.csv"
    # wordcloud_savepath = "dual_wc_result.json"
    # word_numbers = 100
    # pie_savepath = "dual_pie_result.json"
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
