import pandas as pd
from nltk.corpus import stopwords
import sys

stop_words = set(stopwords.words('english'))


def process(type, filepath, result_savepath, word_numbers):
    wc_res, pie_res, violin_res, error_message = "", "", "", ""
    if type == "single":
        wc_res, pie_res, violin_res, error_message = single_process_csv(type, filepath, word_numbers)
    if type == "dual":
        wc_res, pie_res, violin_res, error_message = dual_process_csv(type, filepath, word_numbers)
    savefile(result_savepath, wc_res, pie_res, violin_res, error_message)


def savefile(savepath, wc_records, pie_records, violin_records, error_message):
    res = '{\n'
    res = res + '\t\"error_message\" : \"' + error_message + '\", \n\n'

    res = res + '\t\"wc_result\" : [\n'
    k = 0
    for record in wc_records:
        res = res + '\t{\n'
        res = res + '\t\t\"x\":\"' + record[0] + '\",\n'
        res = res + '\t\t\"value\":' + str(record[1]) + ',\n'
        res = res + '\t\t\"category\":\"' + str(record[2]) + '\"\n'
        k = k + 1
        if k == len(wc_records):
            res = res + '\t}\n'
        else:
            res = res + '\t},\n'
    res = res + '\t],'

    res = res + '\n\n\t\"pie_result\" : [\n'
    k = 0
    for record in pie_records:
        res = res + '\t{\n'
        res = res + '\t\t\"type\":\"' + str(record[0]) + '\",\n'
        res = res + '\t\t\"value\":' + str(record[1]) + '\n'
        k = k + 1
        if k == len(pie_records):
            res = res + '\t}\n'
        else:
            res = res + '\t},\n'
    res = res + '\t],'

    res = res + '\n\n\t\"violin_result\" : [\n'
    k = 0
    for record in violin_records:
        res = res + '\t{\n'
        res = res + '\t\t\"x\":\"' + str(record[0]) + '\",\n'
        res = res + '\t\t\"y\":' + str(record[1]) + '\n'
        k = k + 1
        if k == len(violin_records):
            res = res + '\t}\n'
        else:
            res = res + '\t},\n'
    res = res + '\t]'

    res = res + '\n}'

    with open(savepath, 'w') as f:
        f.write(res)


def single_process_csv(type, filepath, numbers):
    if filepath[-3:] == 'tsv':
        df_data = pd.read_csv(filepath, sep='\t', header=1, names=['content', 'label'])
    else:
        df_data = pd.read_csv(filepath, header=1, names=['content', 'label'])

    label_set = set(df_data['label'])
    limit = int(numbers)
    wc_res_list = []
    pie_res_list = []
    violin_res_list = []
    error_message = ""
    for label in label_set:
        temp_df = df_data.loc[df_data['label'] == label]
        # for pie
        pie_res_list.append([str(label), len(temp_df)])
        # for wordcloud and violin
        temp_wc, temp_violin, temp_error_message = statistics(type, temp_df)
        if temp_error_message != '':
            error_message = error_message + '\n' + temp_error_message
        # for violin
        for word_count in temp_violin:
            violin_res_list.append([str(label), word_count])
            violin_res_list.append(['total', word_count])
        # for wordcloud
        temp_order = dict(temp_wc[:limit])
        temp_words = temp_order.keys()
        for word in temp_words:
            wc_res_list.append([word, temp_order[word], str(label)])
    wc_res_list.sort(key=lambda x: x[1], reverse=True)

    return wc_res_list[:numbers], pie_res_list, violin_res_list, error_message


def statistics(type, df_data):
    dict = {}
    word_number_per_sentence = []
    error_message = ''
    k = 0
    current_data = []
    if type == "single":
        current_data = df_data['content']
    if type == "dual":
        current_data = df_data
    for sentence in current_data:
        temp_number_per_sentence = 0
        k = k + 1
        if sentence == '#NAME?':
            error_message = error_message + 'There is a sentence in line' + str(k) + ' presented as #NAME? .\n'
        for word in str(sentence).split(sep=' '):
            word = word.lower()
            if word != '':
                temp_number_per_sentence = temp_number_per_sentence + 1
                if word not in stop_words and word[0].isalpha():
                    if word in dict.keys():
                        dict[word] = dict[word] + 1
                    else:
                        dict[word] = 1
        word_number_per_sentence.append(temp_number_per_sentence)

    if k != len(current_data):
        error_message = error_message + 'The number of sentence is different from the original number. \n'
    w_order = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    return w_order, word_number_per_sentence, error_message


def dual_process_csv(type, filepath, numbers):
    if filepath[-3:] == 'tsv':
        df_csv = pd.read_csv(filepath, sep='\t')
    else:
        df_csv = pd.read_csv(filepath)

    violin_res_list = []
    error_message = ""

    # for wordcloud and violin
    df_1 = df_csv['sentence1']
    df_2 = df_csv['sentence2']
    wc_1, violin_1, error_message_1 = statistics(type, df_1)
    wc_2, violin_2, error_message_2 = statistics(type, df_2)

    # for error message
    if error_message_1 != "":
        error_message = error_message + '\n' + error_message_1
    if error_message_2 != "":
        error_message = error_message + '\n' + error_message_2

    # for violin
    for word_count in violin_1:
        violin_res_list.append(['sentence1', word_count])
        violin_res_list.append(['total', word_count])
    for word_count in violin_2:
        violin_res_list.append(['sentence2', word_count])
        violin_res_list.append(['total', word_count])

    wc_res_list = []
    limit = int(numbers)
    order_1 = dict(wc_1[:limit])
    order_2 = dict(wc_2[:limit])
    words_1 = order_1.keys()
    for word in words_1:
        wc_res_list.append([word, order_1[word], 'sentence1'])
    words_2 = order_2.keys()
    for word in words_2:
        wc_res_list.append([word, order_2[word], 'sentence2'])
    wc_res_list.sort(key=lambda x: x[1], reverse=True)

    # for pie
    pie_res_list = []
    pie_label_list = [int(i) for i in df_csv['label']]
    cnt = len(pie_label_list)
    max_label = max(pie_label_list)
    i = 0
    while True:
        temp_cnt = pie_label_list.count(i)
        if i == max_label:
            temp_label = str(i)
        else:
            temp_label = '[' + str(i) + ' ,' + str(i + 1) + ')'
        i = i + 1
        pie_res_list.append([temp_label, temp_cnt])
        cnt = cnt - temp_cnt
        if cnt == 0 or i > 50:
            break
    return wc_res_list, pie_res_list, violin_res_list, error_message


if __name__ == '__main__':
    # type = "single"
    # filepath = "/Users/yuanren/Desktop/FinalProj/tool/SST-2/dev.tsv"
    # result_savepath = '/Users/yuanren/Desktop/FinalProj/tool/pyCode/single_result.json'
    # # type = "dual"
    # # filepath = "/Users/yuanren/Desktop/FinalProj/tool/sts/sts-dev.csv"
    # # result_savepath = '/Users/yuanren/Desktop/FinalProj/tool/pyCode/dual_result.json'
    #
    # word_numbers = 100
    # process(type, filepath, result_savepath, word_numbers)

    if len(sys.argv) == 5:
        print("The running filename: '{}'".format(sys.argv[0]))
        print("The data type: '{}'".format(sys.argv[1]))
        print("The data file name: '{}'".format(sys.argv[2]))
        print("The saving file path and name: '{}'".format(sys.argv[3]))
        print("The maximal number of the final words: '{}'".format(sys.argv[4]))
        type = sys.argv[1]
        filepath = sys.argv[2]
        result_savepath = sys.argv[3]
        word_numbers = int(sys.argv[4])

        process(type, filepath, result_savepath, word_numbers)
        print("successfully finished")
    else:
        print("the arguments are not valid")
        print("The number of arguments: '{}'".format(len(sys.argv)))
        for arg in sys.argv:
            print(arg)
