from create_app import mongo


class Message:
    @staticmethod
    def add_message(new_message):
        mongo.db.messages.insert_one(new_message)

    @staticmethod
    def get_messages_by_chat_id(chat_id):
        return mongo.db.messages.find({'chat_id': chat_id})
