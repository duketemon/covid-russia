import sys
import pandas as pd


def clean_subject_name(subject_name):
    subject_name = subject_name.replace('–', '—')
    subject_name = subject_name.replace('автономный округ', 'АО')
    subject_name = subject_name.replace('автономная область', 'АО')
    subject_name = subject_name.replace('республика', 'Республика')
    subject_name = subject_name.replace('область', 'Область')
    subject_name = subject_name.replace('край', 'Край')
    subject_name = subject_name.replace('Республика Чечня', 'Чеченская Республика')
    subject_name = subject_name.replace('Республика Чувашия', 'Чувашская Республика')
    subject_name = subject_name.replace('Республика Удмуртия', 'Удмуртская Республика')
    subject_name = subject_name.replace('Республика Кабардино-Балкария', 'Кабардино-Балкарская Республика')
    subject_name = subject_name.replace('Республика Карачаево-Черкесия', 'Карачаево-Черкесская Республика')
    subject_name = subject_name.strip()
    if 'Республика Северная Осетия' == subject_name:
        subject_name = subject_name.replace('Республика Северная Осетия', 'Республика Северная Осетия — Алания')
    return subject_name


def add_data(date):
    date = date + '.2020'
    infected_df = pd.read_csv('data-infected.csv')
    healed_df = pd.read_csv('data-healed.csv')
    died_df = pd.read_csv('data-died.csv')

    new_data_df = pd.read_csv('data-new.csv')
    new_data_df['Регион'] = new_data_df['Регион'].apply(lambda subj: clean_subject_name(subj))

    infected_values, healed_values, died_values = list(), list(), list()
    for subject in infected_df['Субъект']:
        infected_values.append(new_data_df[new_data_df['Регион'] == subject]['Выявлено'].values[0])
        healed_values.append(new_data_df[new_data_df['Регион'] == subject]['Выздоровело'].values[0])
        died_values.append(new_data_df[new_data_df['Регион'] == subject]['Умерло'].values[0])

    infected_df[date] = infected_values
    infected_df.to_csv('data-infected-new.csv', index=False)

    healed_df[date] = healed_values
    healed_df.to_csv('data-healed-new.csv', index=False)

    died_df[date] = died_values
    died_df.to_csv('data-died-new.csv', index=False)


if len(sys.argv) == 1:
    print('Forget about the date parameter. Expected: python add_data.py dd.mm')
else:
    values = sys.argv[1].split('.')
    if len(values) != 2 or len(values[0]) != 2 or len(values[1]) != 2:
        print('Wrong the date format. Expected: dd.mm')

    else:
        add_data(sys.argv[1])
