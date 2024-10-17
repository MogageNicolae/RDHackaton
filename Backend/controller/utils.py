def does_fields_exist(data, fields):
    for field in fields:
        if field not in data:
            return False
    return True
