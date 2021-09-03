import os
import json
from functools import lru_cache


# TODO: add cahing
def get_folders_names(parent_folder):
    return [d for d in os.listdir(parent_folder) if
            os.path.isdir(os.path.join(parent_folder, d))]


def actual_file_number(template_folder):
    files = os.listdir(template_folder)
    return max(int(f.split('.')[0]) for f in files)


def read_actual_template(template_folder):
    actual_number = actual_file_number(template_folder)
    f = open(os.path.join(template_folder, str(actual_number) + '.txt'))
    data = [l.strip() for l in f.readlines()]
    f.close()
    return data


def save_actual_template(template_folder, expressions):
    actual_number = actual_file_number(template_folder)
    with open(os.path.join(template_folder, str(actual_number + 1) + '.txt'), 'w') as f:
        f.write("\n".join(expressions))


def read_json(file_path):
    with open(file_path) as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))


def update_gazetteer(file_path, data):
    with open(file_path, 'w') as f:
        f.write('\n'.join(e['cname'] for e in data['entities']))


def update_dictionary(file_path, entity_type, data):
    dictionary = None
    with open(file_path) as f:
        dictionary = json.load(f)

    dictionary['entities'][entity_type]['cnames'] = list(e['cname'] for e in data['entities'])

    with open(file_path, 'w') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False))
