import os
import json
from collections import defaultdict


def get_subjects():
    with open('RF.subjects', 'r') as f:
        subjects = f.read().split('\n')
        return {s.strip() for s in subjects}

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


def extract_info(line: str):
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
                subject, infected, healed, died = extract_info(line)
                data[subject]['dates'].append(filename)
                data[subject]['infected'].append(infected)
                data[subject]['healed'].append(healed)
                data[subject]['died'].append(died)

                RUSSIA_DATA[filename]['infected'].append(infected)
                RUSSIA_DATA[filename]['healed'].append(healed)
                RUSSIA_DATA[filename]['died'].append(died)
    return data

SUBJECTS = get_subjects()
data_path = 'data/'
RUSSIA_DATA = defaultdict(lambda: defaultdict(list))
DATA = start_processing(data_path)

DATA['Россия']['dates'] = sorted(list(RUSSIA_DATA.keys()))
for d in DATA['Россия']['dates']:
    DATA['Россия']['infected'].append(sum(RUSSIA_DATA[d]['infected']))
    DATA['Россия']['healed'].append(sum(RUSSIA_DATA[d]['healed']))
    DATA['Россия']['died'].append(sum(RUSSIA_DATA[d]['died']))

output_filename = 'stats.js'
with open(output_filename, 'w') as f:
    json.dump(DATA, f, ensure_ascii=False)
