import firebase_admin
from firebase_admin import firestore

class ChatRoom:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.db = firestore.client()
        self.ref = self.db.collection(u'nba_chat_rooms').document(self.match_id)
        self.messages = []

    def to_dict(self):
        # Return a dictionary representation of the ChatRoom object
        return {
            'match_id': self.match_id,
            'messages': self.messages
        }

    def add_message(self, message: str, username: str):
        self.ref.update({
            u'messages': firestore.ArrayUnion([{
                u'message': message,
                u'username': username
            }])
        })

    def get_messages(self):
        doc = self.ref.get()
        if doc.exists:
            return doc.to_dict()['messages']
        return []

    def delete_message(self, message_id: int):
        self.ref.update({
            u'messages': firestore.ArrayRemove([{
                u'id': message_id
            }])
        })
