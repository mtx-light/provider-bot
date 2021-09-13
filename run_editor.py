import os
from flask import Flask, request, jsonify
from editor.utils import get_folders_names, read_actual_template, save_actual_template, read_json, save_json, \
    update_gazetteer, update_dictionary, generate_from_template, is_system_entity, spawn_train_process
from distutils.dir_util import copy_tree

APP_FOLDER = os.path.join('.', 'provider_bot')
EDITOR_FOLDER = os.path.join('.', 'editor')
TEMPLATES_FOLDER = os.path.join(EDITOR_FOLDER, 'templates')
ENTITIES_FOLDER = os.path.join(EDITOR_FOLDER, 'entities')
MODELS_FOLDER = os.path.join(EDITOR_FOLDER, 'models')

api = Flask(__name__)

selected_model = None
train_process = None


@api.route('/domains', methods=['GET'])
def get_domains():
    path_to_domains = TEMPLATES_FOLDER
    domains = get_folders_names(path_to_domains)
    return jsonify({'domains': domains})


@api.route('/intents', methods=['GET'])
def get_intents():
    domain = request.args.get('domain')
    path_to_intents = os.path.join(TEMPLATES_FOLDER, domain)
    intents = get_folders_names(path_to_intents)
    return jsonify({'intents': intents})


@api.route('/template', methods=['GET'])
def get_template():
    domain = request.args.get('domain')
    intent = request.args.get('intent')
    path_to_intent = os.path.join(TEMPLATES_FOLDER, domain, intent)
    template = read_actual_template(path_to_intent)
    return jsonify({'expressions': template})


@api.route('/template', methods=['POST'])
def post_template():
    domain = request.args.get('domain')
    intent = request.args.get('intent')
    template_data = request.get_json()
    path_to_intent = os.path.join(TEMPLATES_FOLDER, domain, intent)
    save_actual_template(path_to_intent, template_data['expressions'])
    return jsonify({'status': 'OK'})


@api.route('/entity-types', methods=['GET'])
def get_entity_types():
    entities_json = read_json(os.path.join(ENTITIES_FOLDER, 'entity_dictionary.json'))
    return jsonify({'entity_types': list(entities_json["entities"].keys())})


@api.route('/entity-roles', methods=['GET'])
def get_entity_roles():
    entity_type = request.args.get('entity-type')
    entities_json = read_json(os.path.join(ENTITIES_FOLDER, 'entity_dictionary.json'))
    return jsonify({'entity_roles': entities_json["entities"][entity_type]['roles']})


@api.route('/entity-type', methods=['GET'])
def get_entity_type():
    entity_type = request.args.get('entity-type')
    entity_json = read_json(os.path.join(APP_FOLDER, 'entities', entity_type, 'mapping.json'))
    return jsonify(entity_json)


@api.route('/entity-type', methods=['POST'])
def post_entity_type():
    entity_type = request.args.get('entity-type')
    if not is_system_entity(entity_type, os.path.join(ENTITIES_FOLDER, 'entity_dictionary.json')):
        entity_type_data = request.get_json()
        save_json(os.path.join(APP_FOLDER, 'entities', entity_type, 'mapping.json'), entity_type_data)
        update_gazetteer(os.path.join(APP_FOLDER, 'entities', entity_type, 'gazetteer.txt'), entity_type_data)
        update_dictionary(os.path.join(ENTITIES_FOLDER, 'entity_dictionary.json'), entity_type, entity_type_data)
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'FAIL',
                        'reason': "Type {} is system entity type".format(entity_type)})


@api.route('/models', methods=['GET'])
def get_models():
    models = get_folders_names(MODELS_FOLDER)
    return jsonify({'models': models})


@api.route('/rename-model', methods=['POST'])
def rename_model():
    old_name = request.args.get('old-name')
    new_name = request.args.get('new-name')
    if os.path.exists(os.path.join(MODELS_FOLDER, old_name)):
        if not os.path.exists(os.path.join(MODELS_FOLDER, new_name)):
            os.rename(os.path.join(MODELS_FOLDER, old_name), os.path.join(MODELS_FOLDER, new_name))
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'FAIL',
                            'reason': "Model {} is already exist".format(new_name)})
    else:
        return jsonify({'status': 'FAIL',
                        'reason': "Model {} is not exists".format(old_name)})


@api.route('/select-model', methods=['POST'])
def select_model():
    model = request.args.get('model')
    if os.path.exists(os.path.join(MODELS_FOLDER, model)):
        global selected_model
        selected_model = model
        copy_tree(os.path.join(MODELS_FOLDER, selected_model), os.path.join(APP_FOLDER, '.generated'))
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'FAIL',
                        'reason': "Model {} is not exists".format(model)})


@api.route('/generate-train-data', methods=['POST'])
def generate_train_date():
    domains = get_folders_names(TEMPLATES_FOLDER)
    entity_dictionary = os.path.join(ENTITIES_FOLDER, 'entity_dictionary.json')
    for domain in domains:
        domain_path = os.path.join(TEMPLATES_FOLDER, domain)
        intents = get_folders_names(domain_path)
        for intent in intents:
            intent_template_folder = os.path.join(domain_path, intent)
            generate_from_template(intent_template_folder,
                                   os.path.join(APP_FOLDER, 'domains', domain, intent, 'train.txt'),
                                   entity_dictionary)
    return jsonify({'status': 'OK'})


@api.route('/train-model', methods=['POST'])
def train_model():
    global train_process
    if not train_process:
        train_process = spawn_train_process()
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'FAIL',
                        'reason': "Model training is already running"})


@api.route('/train-model-status', methods=['GET'])
def train_model_status():
    global train_process
    if train_process:
        return_code = train_process.poll()
        if return_code is not None:
            if return_code == 0:
                copy_tree(os.path.join(APP_FOLDER, '.generated'), os.path.join(MODELS_FOLDER, 'generated'))
            train_process = None
            return jsonify({'status': 'DONE',
                            'return_code': return_code})
        else:
            return jsonify({'status': 'IN_PROGRESS'})
    else:
        return jsonify({'status': 'NOT_STARTED'})


api.run(host='0.0.0.0', debug=True, port=3333)
