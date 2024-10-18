from create_app import mongo


class Users:
    @staticmethod
    def add_user(new_user):
        mongo.db.users.insert_one(new_user)

    @staticmethod
    def get_user_by_username(username):
        return mongo.db.users.find({'username': {'$regex': username, '$options': 'i'}})

    @staticmethod
    def get_user_by_email(email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def update_user_token(email, token, expires_in):
        mongo.db.users.update_one({'email': email}, {'$set': {'token': token, 'expires_in': expires_in}})

    @staticmethod
    def update_user(user_id, new_values):
        mongo.db.users.update_one({'id': user_id}, {'$set': new_values})
