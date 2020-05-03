import os
import json
import pandas as pd
from collections import defaultdict


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


def extract_info_from_line(line: str):
    text, healed, died = line.split('/')
    values = text.split('–')
    infected = values[-1]
    subject_name = '–'.join(values[:-1])
    subject_name = clean_subject_name(subject_name)
    if subject_name not in SUBJECTS:
        print(f'Problem with "{subject_name}"')
    return subject_name, int(infected.replace(' ', '')), int(healed.replace(' ', '')), int(died.replace(' ', ''))


def start_processing(data_path):
    data = defaultdict(lambda: defaultdict(list))
    for filename in sorted(os.listdir(data_path)):
        with open(data_path + filename) as f:
            print(filename)
            for line in f.read().split('\n'):
                subject, infected, healed, died = extract_info_from_line(line)
                data[subject]['dates'].append(filename)
                data[subject]['infected'].append(infected)
                data[subject]['healed'].append(healed)
                data[subject]['died'].append(died)

                RUSSIA_DATA[filename]['infected'].append(infected)
                RUSSIA_DATA[filename]['healed'].append(healed)
                RUSSIA_DATA[filename]['died'].append(died)
    return data


df_subject_districts = pd.read_csv('rf-structure.csv')
SUBJECTS = set(df_subject_districts['Субъект'])
data_path = 'data/'
RUSSIA_DATA = defaultdict(lambda: defaultdict(list))
DATA = start_processing(data_path)

DATA['Россия']['dates'] = sorted(list(RUSSIA_DATA.keys()))
for d in DATA['Россия']['dates']:
    DATA['Россия']['infected'].append(sum(RUSSIA_DATA[d]['infected']))
    DATA['Россия']['healed'].append(sum(RUSSIA_DATA[d]['healed']))
    DATA['Россия']['died'].append(sum(RUSSIA_DATA[d]['died']))

# Данные для вэба
output_filename = 'stats.js'
with open(output_filename, 'w') as f:
    json.dump(DATA, f, ensure_ascii=False)


# Данные для построения иерархичечного графика "Федеральные округа - Субъекты"
timeline_data_infected, timeline_data_healed, timeline_data_died = dict(), dict(), dict()
for d in DATA['Россия']['dates']:
    timeline_data_infected[d] = list()
    timeline_data_healed[d] = list()
    timeline_data_died[d] = list()

for subject in df_subject_districts['Субъект']:
    if not all([len(timeline_data_infected['20.03.26']) == len(timeline_data_infected[key]) for key in timeline_data_infected]):
        print(subject)
    for i, date in enumerate(DATA[subject]['dates']):
        timeline_data_infected[date].append(DATA[subject]['infected'][i])
        timeline_data_healed[date].append(DATA[subject]['healed'][i])
        timeline_data_died[date].append(DATA[subject]['died'][i])
    empty_values = sorted(timeline_data_infected.keys())[:len(DATA['Россия']['dates'])-len(DATA[subject]['dates'])]
    for date in empty_values:
        timeline_data_infected[date].append(0)
        timeline_data_healed[date].append(0)
        timeline_data_died[date].append(0)


def save_data(filename, timeline_data):
    output_data = {
        'Субъект': df_subject_districts['Субъект'],
        'Федеральный Округ': df_subject_districts['Федеральный Округ'],
    }

    for key, values in timeline_data.items():
        _, mm, dd = key.split('.')
        date = f'{dd}.{mm}'
        output_data[date] = values

    pd.DataFrame(data=output_data).to_csv(filename, index=False)


save_data('data-infected.csv', timeline_data_infected)
save_data('data-healed.csv', timeline_data_healed)
save_data('data-died.csv', timeline_data_died)
