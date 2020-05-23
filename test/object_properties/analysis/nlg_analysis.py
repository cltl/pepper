import sqlite3

import pandas as pd

from collections import OrderedDict


class InstanceLabel:

    all_labels = []

    def __init__(self, name, instance, method):

        self.name = name
        self.instance = instance
        self.method = method

        self.picks = None
        self.correct_scores = None
        self.natural_scores = None

        self.avg_correct = None
        self.avg_natural = None

        self.__class__.all_labels.append(self)

    def add_instance_picks(self, list_of_picks):
        picks = dict()
        for pick in list_of_picks:
            pick = str(pick).strip()
            # some values not counted if list_of_picks.count(pick) is used
            if pick not in picks:
                picks[pick] = 1
            else:
                picks[pick] += 1
        self.picks = picks

    def add_correct_scores(self, list_of_scores):
        filtered_scores = [float(eval(score)) for score in list_of_scores if score != 'nan']
        avg_score = round(sum(filtered_scores) / len(filtered_scores), 2)
        self.avg_correct = avg_score
        scores = dict()
        for score in filtered_scores:
            scores[score] = list_of_scores.count(score)
        self.correct_scores = scores

    def add_natural_scores(self, list_of_scores):
        filtered_scores = [float(eval(score)) for score in list_of_scores if score != 'nan']
        avg_score = round(sum(filtered_scores) / len(filtered_scores), 2)
        self.avg_natural = avg_score
        scores = dict()
        for score in filtered_scores:
            scores[score] = list_of_scores.count(score)
        self.natural_scores = scores

    @classmethod
    def all(cls):
        for description in cls.all_labels:
            yield(description)


def retrieve_data_from_table(cur, table):
    cur.execute('SELECT * FROM {}'.format(table))
    data = cur.fetchall()

    return dict(data)


def add_survey_scores(label, column_names, survey_df):
    for column in column_names:
        if label.name == column:
            label.add_instance_picks(list(survey_df[column]))
        elif label.name in column and 'correct' in column:
            label.add_correct_scores(list(survey_df[column]))
        elif label.name in column and 'natural' in column:
            label.add_natural_scores(list(survey_df[column]))


def calculate_avg_method_scores(label_list):
    method_correct = round(sum([label.avg_correct for label in label_list]) / len(label_list), 2)
    method_natural = round(sum([label.avg_natural for label in label_list]) / len(label_list), 2)

    return {'avg_correct_score': method_correct, 'avg_natural_score': method_natural}


'''def create_scores_table(label_list, label_averages):
    label_dict = OrderedDict()
    label_dict[''] = ['avg correct score', 'avg natural score']
    for label in label_list:
        label_dict['{} ({})'.format(label.name, label.instance)] = [label.avg_correct, label.avg_natural]
    label_dict['total average'] = [label_averages['avg_correct_score'], label_averages['avg_natural_score']]

    label_df = pd.DataFrame.from_dict(label_dict, orient='index')

    with open('nlg_{}_avg_table.tex'.format(label_list[0].method), 'w') as tf:
        tf.write(label_df.to_latex(index=True, bold_rows=True))'''


def create_scores_table(label_list, label_averages):
    score_list = []

    for label in label_list:
        label_dict = OrderedDict()
        label_dict['Label'] = label.name
        label_dict['Object instance'] = label.instance
        label_dict['Avg. correct'] = label.avg_correct
        label_dict['Avg. natural'] = label.avg_natural
        label_dict['total average'] = [label_averages['avg_correct_score'], label_averages['avg_natural_score']]

        score_list.append(label_dict)

    label_df = pd.DataFrame.from_records(score_list)

    with open('nlg_{}_avg_table.tex'.format(label_list[0].method), 'w') as tf:
        tf.write(label_df.to_latex(index=False, bold_rows=False))


def create_picks_table(label_list):
    score_list = []
    for label in label_list:
        correct = sum([label.picks[key] for key in label.picks.keys() if str(key) == str(label.instance)])
        incorrect = sum([label.picks[key] for key in label.picks.keys() if str(key) != str(label.instance)])

        correct_percent = round(float(correct) / float(correct + incorrect) * 100, 2)
        incorrect_percent = round(float(incorrect) / float(correct + incorrect) * 100, 2)

        label_dict = OrderedDict()
        label_dict['Label'] = label.name
        label_dict['Object instance'] = label.instance
        label_dict['Correct %'] = correct_percent
        label_dict['Incorrect %'] = incorrect_percent

        score_list.append(label_dict)

    picks_df = pd.DataFrame.from_records(score_list)

    with open('nlg_{}_picks_table.tex'.format(label_list[0].method), 'w') as tf:
        tf.write(picks_df.to_latex(index=False, bold_rows=False))


def main():

    survey_file = 'color_survey.csv'

    survey_df = pd.read_csv(survey_file).astype('str')
    survey_df.drop(survey_df.iloc[:, :9], axis=1, inplace=True)

    column_names = list(survey_df.columns)

    conn = sqlite3.connect('../eval_instances.db')
    cur = conn.cursor()

    baseline = retrieve_data_from_table(cur, 'nlg_baseline')
    glove_100 = retrieve_data_from_table(cur, 'nlg_glove_100')
    glove_300 = retrieve_data_from_table(cur, 'nlg_glove_300')

    obj_instances = baseline.keys()

    for obj_instance in obj_instances:
        if baseline[obj_instance] in (glove_100[obj_instance], glove_300[obj_instance]):
            shared_label = InstanceLabel(baseline[obj_instance], obj_instance, 'shared')
            add_survey_scores(shared_label, column_names, survey_df)
        else:
            baseline_label = InstanceLabel(baseline[obj_instance], obj_instance, 'baseline')
            add_survey_scores(baseline_label, column_names, survey_df)
            glove100_label = InstanceLabel(glove_100[obj_instance], obj_instance, 'glove')
            add_survey_scores(glove100_label, column_names, survey_df)
            if glove_300[obj_instance] != glove_100[obj_instance]:
                glove300_label = InstanceLabel(glove_300[obj_instance], obj_instance, 'glove')
                add_survey_scores(glove300_label, column_names, survey_df)

    conn.close()

    shared_labels = [label for label in InstanceLabel.all_labels if label.method == 'shared']
    baseline_labels = [label for label in InstanceLabel.all_labels if label.method == 'baseline']
    glove_labels = [label for label in InstanceLabel.all_labels if label.method == 'glove']

    create_picks_table(shared_labels)
    create_picks_table(baseline_labels)
    create_picks_table(glove_labels)

    shared_averages = calculate_avg_method_scores(shared_labels)
    baseline_averages = calculate_avg_method_scores(baseline_labels)
    glove_averages = calculate_avg_method_scores(glove_labels)

    create_scores_table(shared_labels, shared_averages)
    create_scores_table(baseline_labels, baseline_averages)
    create_scores_table(glove_labels, glove_averages)


if __name__ == '__main__':
    main()
