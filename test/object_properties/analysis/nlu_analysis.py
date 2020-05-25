import json
import sqlite3

import pandas as pd

from collections import defaultdict, OrderedDict


def generate_instance_descriptions(survey_file):

    survey_df = pd.read_csv(survey_file).astype('str')
    survey_df.drop(survey_df.iloc[:, :1], axis=1, inplace=True)
    survey_df.drop(survey_df.iloc[:, 8:], axis=1, inplace=True)

    color_mappings = {}

    description_dict = dict(survey_df)
    for obj_instance, answers in description_dict.items():
        obj_type = obj_instance.split('_')[0]
        for answer in answers:
            colors = answer.split(', ')
            for color in colors:
                color = color.strip().replace('-', ' ').replace('/', ' ').replace('a ', '').replace('the ', '')
                if len(color.split()) <= 3:
                    instance_description = color + ' ' + obj_type
                    if instance_description not in color_mappings:
                        color_mappings[instance_description] = obj_instance

    with open('color_mappings.json', 'w') as f:
        json.dump(color_mappings, f)


def retrieve_data_from_nlu_table(cur, table):
    cur.execute('SELECT * FROM {}'.format(table))
    data = cur.fetchall()

    return pd.DataFrame(data)


def calculate_input_statistics(df):
    description_dict = defaultdict(set)
    count_dict = dict()

    for row in df.iterrows():
        description_dict[row[1][2]].add(row[1][0])

    for key, values in description_dict.items():
        count_dict[key] = len(values)

    return count_dict


def calculate_df_statistics(obj_instances, df):

    correct_dict = OrderedDict()

    for obj_instance in obj_instances:
        num_correct = len([row for row in df.iterrows() if row[1][2] == obj_instance and row[1][1] == row[1][2]])
        num_incorrect = len([row for row in df.iterrows() if row[1][2] == obj_instance and row[1][1] != row[1][2]])

        percent_correct = round(float(num_correct) / (float(num_correct) + (float(num_incorrect))) * 100, 2)

        correct_dict[obj_instance] = percent_correct

    correct_total = len([row for row in df.iterrows() if row[1][1] == row[1][2]])
    percent_correct_total = round(float(correct_total) / (float(df.shape[0])) * 100, 2)

    correct_dict['Total'] = percent_correct_total

    return correct_dict


def main():
    survey_file = 'color_survey.csv'

    # generate_instance_descriptions(survey_file)

    conn = sqlite3.connect('../eval_instances.db')
    cur = conn.cursor()

    baseline_df = retrieve_data_from_nlu_table(cur, 'nlu_baseline')

    glove_100_avg_df = retrieve_data_from_nlu_table(cur, 'nlu_glove_100_avg')
    glove_100_concat_df = retrieve_data_from_nlu_table(cur, 'nlu_glove_100_concat')
    glove_100_wmd_df = retrieve_data_from_nlu_table(cur, 'nlu_glove_100_wmd')

    glove_300_avg_df = retrieve_data_from_nlu_table(cur, 'nlu_glove_300_avg')
    glove_300_concat_df = retrieve_data_from_nlu_table(cur, 'nlu_glove_300_concat')
    glove_300_wmd_df = retrieve_data_from_nlu_table(cur, 'nlu_glove_300_wmd')

    conn.close()

    input_stats = calculate_input_statistics(baseline_df)
    obj_instances = input_stats.keys()

    baseline_dict = calculate_df_statistics(obj_instances, baseline_df)

    glove_100_avg_dict = calculate_df_statistics(obj_instances, glove_100_avg_df)
    glove_100_concat_dict = calculate_df_statistics(obj_instances, glove_100_concat_df)
    glove_100_wmd_dict = calculate_df_statistics(obj_instances, glove_100_wmd_df)

    glove_300_avg_dict = calculate_df_statistics(obj_instances, glove_300_avg_df)
    glove_300_concat_dict = calculate_df_statistics(obj_instances, glove_300_concat_df)
    glove_300_wmd_dict = calculate_df_statistics(obj_instances, glove_300_wmd_df)

    results_100_list = [baseline_dict, glove_100_avg_dict, glove_100_concat_dict, glove_100_wmd_dict]

    results_300_list = [baseline_dict, glove_300_avg_dict, glove_300_concat_dict, glove_300_wmd_dict]

    results_100_df = pd.DataFrame.from_records(results_100_list).transpose()
    results_300_df = pd.DataFrame.from_records(results_300_list).transpose()

    with open('nlu_results_100.tex', 'w') as tf:
        tf.write(results_100_df.to_latex(index=True, bold_rows=False))

    with open('nlu_results_300.tex', 'w') as tf:
        tf.write(results_300_df.to_latex(index=True, bold_rows=False))


if __name__ == '__main__':
    main()