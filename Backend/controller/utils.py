import json

def do_fields_exist(data, fields):
    for field in fields:
        if field not in data:
            return False
    return True


def load_languages(file_name):
    with open(f'languages_mapping/{file_name}', 'r') as f:
        return json.load(f)


m2m100_languages = load_languages('m2m100_languages.json')
seamless_languages = load_languages('seamless_languages.json')


def map_language_to_m2m(language):
    return m2m100_languages[language]


def map_language_to_seamless(language):
    return seamless_languages[language]
