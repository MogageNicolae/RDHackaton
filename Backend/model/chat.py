from create_app import mongo


class ChatRoom:
    @staticmethod
    def add_chat_room(new_chat_room):
        mongo.db.chat_rooms.insert_one(new_chat_room)

    @staticmethod
    def delete_chat_room(chat_room_id):
        mongo.db.chat_rooms.delete_one({'id': chat_room_id})
