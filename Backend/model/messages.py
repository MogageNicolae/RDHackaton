from create_app import mongo


class Messages:
    @staticmethod
    def add_message(new_message):
        mongo.db.messages.insert_one(new_message)

    @staticmethod
    def get_messages_by_chat_id(chat_id, page=1, page_size=25):
        return mongo.db.messages.find({'chat_id': chat_id}).skip((page - 1) * page_size).limit(page_size)
