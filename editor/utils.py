import re
import os
import itertools
import json
from subprocess import Popen, PIPE
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


def append_template(template_folder, expressions):
    actual_number = actual_file_number(template_folder)
    with open(os.path.join(template_folder, str(actual_number) + '.txt')) as old:
        with open(os.path.join(template_folder, str(actual_number + 1) + '.txt'), 'w') as new:
            new.write("\n".join([l.strip() for l in old.readlines()] + expressions))


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


def substitute_template(template_line, entity_dictionary):
    placeholders = re.findall(r"{(.+?)}", template_line)
    if placeholders:
        filled_templates = []
        for placeholder in placeholders:
            entity_type = None
            role = None
            if "|" in placeholder:
                entity_type, role = [s.strip() for s in placeholder.split("|")]
            else:
                entity_type = placeholder.strip()
            canonical_names = entity_dictionary['entities'][entity_type]['cnames']
            filled_templates.append(
                ["{" + cname + "|" + entity_type + ("|" + role if role else "") + "}" for cname in canonical_names])
            template_line = template_line.replace(placeholder, "")
        return [template_line.format(*p) for p in itertools.product(*filled_templates)]
    else:
        return [template_line]


def generate_from_template(template_folder, train_file, entity_dictionary):
    dictionary = read_json(entity_dictionary)
    with open(train_file, 'w') as output:
        actual_template = actual_file_number(template_folder)
        with open(os.path.join(template_folder, str(actual_template) + '.txt')) as inpt:
            for case in inpt.readlines():
                output.writelines(substitute_template(case, dictionary))


def is_system_entity(entity_type, entity_dictionary_path):
    dictionary = read_json(entity_dictionary_path)
    return dictionary["entities"][entity_type]["is_system"]


def spawn_train_process():
    return Popen(["python", "-m", "provider_bot", "build"], stdout=PIPE, stderr=PIPE)
