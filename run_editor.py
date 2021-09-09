import os
from flask import Flask, request, jsonify
from editor.utils import get_folders_names, read_actual_template, save_actual_template, read_json, save_json, \
    update_gazetteer, update_dictionary
from distutils.dir_util import copy_tree

APP_FOLDER = os.path.join('.', 'provider_bot')
EDITOR_FOLDER = os.path.join('.', 'editor')
TEMPLATES_FOLDER = os.path.join(EDITOR_FOLDER, 'templates')
ENTITIES_FOLDER = os.path.join(EDITOR_FOLDER, 'entities')
MODELS_FOLDER = os.path.join(EDITOR_FOLDER, 'models')

api = Flask(__name__)

selected_model = None


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
    entity_type_data = request.get_json()
    save_json(os.path.join(APP_FOLDER, 'entities', entity_type, 'mapping.json'), entity_type_data)
    update_gazetteer(os.path.join(APP_FOLDER, 'entities', entity_type, 'gazetteer.txt'), entity_type_data)
    update_dictionary(os.path.join(ENTITIES_FOLDER, 'entity_dictionary.json'), entity_type, entity_type_data)
    return jsonify({'status': 'OK'})

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

api.run(host='0.0.0.0', debug=True, port=3333)
