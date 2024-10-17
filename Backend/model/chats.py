from create_app import mongo


class Chats:
    @staticmethod
    def add_chat_room(new_chat_room):
        mongo.db.chats.insert_one(new_chat_room)

    @staticmethod
    def delete_chat_room(chat_room_id):
        mongo.db.chats.delete_one({'id': chat_room_id})

    @staticmethod
    def get_chat_room_by_id(chat_room_id):
        return mongo.db.chats.find_one({'chat_id': chat_room_id})

