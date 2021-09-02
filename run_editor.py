import os
from flask import Flask, request, jsonify
from editor.utils import get_folders_names, read_actual_template, save_actual_template, read_json

APP_FOLDER = 'provider_bot'
EDITOR_FOLDER = os.path.join('.', 'editor')
TEMPLATES_FOLDER = os.path.join(EDITOR_FOLDER, 'templates')
ENTITIES_FOLDER = os.path.join(EDITOR_FOLDER, 'entities')

api = Flask(__name__)


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

api.run(host='0.0.0.0', debug=True, port=3333)
