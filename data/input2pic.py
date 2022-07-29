import pandas as pd
import sys
from polyglot.detect import Detector
from polyglot.text import Text
import string
import stopwordsiso as stopwords
from polyglot.detect.base import logger as polyglot_logger
import json

polyglot_logger.setLevel("ERROR")


def process(filepath, result_savepath, word_numbers, input1_colnum, input2_colnum, label_colnum):
    if label_colnum == -1:
        wc_res, pie_res, violin_res, error_message = test_process_csv(filepath, word_numbers, input1_colnum,
                                                                        input2_colnum)
    elif input2_colnum == -1:
        wc_res, pie_res, violin_res, error_message = single_process_csv(filepath, word_numbers, input1_colnum,
                                                                        input2_colnum, label_colnum)
    else:
        wc_res, pie_res, violin_res, error_message = dual_process_csv(filepath, word_numbers, input1_colnum,
                                                                      input2_colnum, label_colnum)
    savefile(result_savepath, wc_res, pie_res, violin_res, error_message)


def savefile(savepath, wc_records, pie_records, violin_records, error_message):
    res = '{\n'
    res = res + '\t\"error_message\" : \"' + error_message + '\", \n\n'

    res = res + '\t\"wc_result\" : [\n'
    k = 0
    for record in wc_records:
        res = res + '\t{\n'
        res = res + '\t\t\"x\":\"' + str(record[0]).capitalize() + '\",\n'
        res = res + '\t\t\"value\":' + str(record[1]).capitalize() + ',\n'
        res = res + '\t\t\"category\":\"' + str(record[2]).capitalize() + '\"\n'
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
        res = res + '\t\t\"type\":\"' + str(record[0]).capitalize() + '\",\n'
        res = res + '\t\t\"value\":' + str(record[1]).capitalize() + '\n'
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
        res = res + '\t\t\"x\":\"' + str(record[0]).capitalize() + '\",\n'
        res = res + '\t\t\"y\":' + str(record[1]).capitalize() + '\n'
        k = k + 1
        if k == len(violin_records):
            res = res + '\t}\n'
        else:
            res = res + '\t},\n'
    res = res + '\t]'

    res = res + '\n}'

    with open(savepath, 'w') as f:
        f.write(res)

def test_process_csv(filepath, word_numbers, input1_colnum, input2_colnum):
    if filepath[-3:] == 'tsv':
        df_data = pd.read_csv(filepath, sep='\t')
    else:
        df_data = pd.read_csv(filepath)
    names = ['sentence']
    df_data = df_data.iloc[:, [input1_colnum]]
    df_data.columns = names

    limit = int(word_numbers)
    wc_res_list = []
    pie_res_list = []
    violin_res_list = []
    error_message = ""
    label = "No label"
    temp_df = df_data
    # for pie
    pie_res_list.append([str(label), len(temp_df)])
    # for wordcloud and violin
    temp_wc, temp_violin, temp_error_message = statistics(input2_colnum, temp_df)
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
    violin_res_list.sort(key=lambda x: x[0])

    return wc_res_list[:word_numbers], pie_res_list, violin_res_list, error_message


def single_process_csv(filepath, word_numbers, input1_colnum, input2_colnum, label_colnum):
    if filepath[-3:] == 'tsv':
        df_data = pd.read_csv(filepath, sep='\t')
    else:
        df_data = pd.read_csv(filepath)
    names = ['sentence', 'label']
    df_data = df_data.iloc[:, [input1_colnum, label_colnum]]
    df_data.columns = names

    label_set = set(df_data['label'])
    limit = int(word_numbers)
    wc_res_list = []
    pie_res_list = []
    violin_res_list = []
    error_message = ""
    for label in label_set:
        temp_df = df_data.loc[df_data['label'] == label]
        # for pie
        pie_res_list.append([str(label), len(temp_df)])
        # for wordcloud and violin
        temp_wc, temp_violin, temp_error_message = statistics(input2_colnum, temp_df)
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
    violin_res_list.sort(key=lambda x: x[0])

    return wc_res_list[:word_numbers], pie_res_list, violin_res_list, error_message


def statistics(input2_colnum, df_data):
    if input2_colnum == -1:
        current_data = df_data['sentence']
    else:
        current_data = df_data

    # find the suitable stopwords

    code_list = {'Afrikaans': 'af', 'Arabic': 'ar', 'Armenian': 'hy', 'Basque': 'eu', 'Bengali': 'bn', 'Breton': 'br', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Valencian': 'ca', 'Czech': 'cs', 'Chinese': 'zh', 'Danish': 'da', 'German': 'de', 'Dutch': 'nl', 'Flemish': 'nl', 'Greek': 'el', 'English': 'en', 'Esperanto': 'eo', 'Estonian': 'et', 'Persian': 'fa', 'Finnish': 'fi', 'French': 'fr', 'Irish': 'ga', 'Galician': 'gl', 'Gujarati': 'gu', 'Hausa': 'ha', 'Hebrew': 'he', 'Hindi': 'hi', 'Croatian': 'hr', 'Hungarian': 'hu', 'Indonesian': 'id', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko', 'Kurdish': 'ku', 'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Marathi': 'mr', 'Malay': 'ms', 'Norwegian': 'no', 'Polish': 'pl', 'Portuguese': 'pt', 'Romanian': 'ro', 'Moldavian': 'ro', 'Moldovan': 'ro', 'Russian': 'ru', 'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Sotho, Southern': 'st', 'Spanish': 'es', 'Castilian': 'es', 'Swahili': 'sw', 'Swedish': 'sv', 'Tagalog': 'tl', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Vietnamese': 'vi', 'Yoruba': 'yo', 'Zulu': 'zu'}
    stop_words = stopwords.stopwords("en")
    for sentence in current_data:
        temp_lang = Detector(sentence).language
        if temp_lang.confidence >= 80:
            stop_words = stopwords.stopwords(code_list[temp_lang.name])
            break

    dict = {}
    word_number_per_sentence = []
    error_message = ''
    k = 0
    for sentence in current_data:
        k = k + 1
        if sentence == '#NAME?':
            error_message = error_message + 'There is a sentence in line' + str(k) + ' presented as #NAME? .\n'
        temp_words = Text(str(sentence)).words
        for word in temp_words:
            word = word.lower()
            if word != '':
                if word not in stop_words and word not in string.punctuation:
                    if word in dict.keys():
                        dict[word] = dict[word] + 1
                    else:
                        dict[word] = 1
        word_number_per_sentence.append(len(temp_words))

    if k != len(current_data):
        error_message = error_message + 'The number of sentence is different from the original number. \n'
    w_order = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    return w_order, word_number_per_sentence, error_message


def dual_process_csv(filepath, word_numbers, input1_colnum, input2_colnum, label_colnum):
    if filepath[-3:] == 'tsv':
        df_csv = pd.read_csv(filepath, sep='\t')
    else:
        df_csv = pd.read_csv(filepath)

    names = ['sentence1', 'sentence2', 'label']
    df_csv = df_csv.iloc[:, [input1_colnum, input2_colnum, label_colnum]]
    df_csv.columns = names

    violin_res_list = []
    error_message = ""

    # for wordcloud and violin
    df_1 = df_csv['sentence1']
    df_2 = df_csv['sentence2']
    wc_1, violin_1, error_message_1 = statistics(input2_colnum, df_1)
    wc_2, violin_2, error_message_2 = statistics(input2_colnum, df_2)

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
    violin_res_list.sort(key=lambda x: x[0])

    wc_res_list = []
    limit = int(word_numbers)
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
    # input1_colnum = 0
    # input2_colnum = -1
    # label_colnum = -1
    #
    # filepath = "/Users/yuanren/Desktop/FinalProj/tool/sts/sts2.csv"
    # result_savepath = '/Users/yuanren/Desktop/test/test_result.json'
    #
    # word_numbers = 100
    # process(filepath, result_savepath, word_numbers, input1_colnum, input2_colnum, label_colnum)

    if len(sys.argv) == 7:
        print("The running filename: '{}'".format(sys.argv[0]))
        print("The data file name: '{}'".format(sys.argv[1]))
        print("The saving file path and name: '{}'".format(sys.argv[2]))
        print("The maximal number of the final words: '{}'".format(sys.argv[3]))
        print("The position of input1: '{}'".format(sys.argv[4]))
        print("The position of input2: '{}'".format(sys.argv[5]))
        print("The position of label: '{}'".format(sys.argv[6]))
        filepath = sys.argv[1]
        result_savepath = sys.argv[2]
        word_numbers = int(sys.argv[3])
        input1_colnum = int(sys.argv[4])
        input2_colnum = int(sys.argv[5])
        label_colnum = int(sys.argv[6])

        try:
            process(filepath, result_savepath, word_numbers, input1_colnum, input2_colnum, label_colnum)
            print("successfully finished")
        except Exception as e:
            print(e)

    else:
        print("the arguments are not valid")
        print("The number of arguments: '{}'".format(len(sys.argv)))
        for arg in sys.argv:
            print(arg)
