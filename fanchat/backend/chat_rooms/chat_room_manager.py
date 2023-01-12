import firebase_admin
from firebase_admin import credentials, db, firestore
from chat_room import ChatRoom

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="fanchat/backend/secrets/firebase_account_key.json"


class ChatRoomManager:
    def __init__(self):
        self.cred = credentials.Certificate("fanchat/backend/secrets/firebase_account_key.json")
        firebase_admin.initialize_app(name='chatroom')
        self.db = firestore.client()

    def create_chat_room(self, match_id: str):
        # Create a new ChatRoom object with the given match ID
        chat_room = ChatRoom(match_id)

        # Get a reference to the nba_chat_rooms collection in Firestore
        chat_rooms_ref = self.db.collection('nba_chat_rooms')

        # Create a new document in the collection with the match ID as the document ID
        chat_rooms_ref.document(match_id).set(chat_room.to_dict())

    def get_chat_room(self, match_id: str):
        chat_room = ChatRoom(match_id)
        doc = chat_room.ref.get()
        if doc.exists:
            return chat_room
        return None
    
    def get_match_ids(self):
        # Query the Firestore database to get a list of all NBA matches
        matches_ref = self.db.collection(u'nba_daily_matches')
        matches_query = matches_ref.where(u'status', u'in', [u'inprogress', u'closed'])
        matches = matches_query.get()
        
        # Extract the 'id' fields from the query results
        match_ids = [match.to_dict()['id'] for match in matches]
        return match_ids

    def create_chat_rooms_for_live_matches(self):
        matches_ref = self.db.collection(u'nba_daily_matches')
        query = matches_ref.where(u'status', u'in', [u'inprogress', u'closed'])
        docs = query.get()
        for doc in docs:
            match = doc.to_dict()
            match_id = match['id']
            self.create_chat_room(match_id)
            
    def delete_all_chat_rooms(self):
        # Get a reference to the chat rooms collection in Firestore
        chat_rooms_ref = self.db.collection('chat_rooms')

        # Get a list of all chat rooms in the collection
        chat_rooms = chat_rooms_ref.list_documents()

        # Delete each chat room
        for chat_room in chat_rooms:
            chat_room.delete()
    
    def archive_all_chat_rooms(self):
        # Get a reference to the chat rooms collection in Firestore
        chat_rooms_ref = self.db.collection('chat_rooms')

        # Get a list of all chat rooms in the collection
        chat_rooms = chat_rooms_ref.list_documents()

        # Archive each chat room
        for chat_room in chat_rooms:
            # Get the data from the chat room document
            data = chat_room.get().to_dict()

            # Create a new document in the "archived" collection with the same data
            self.db.collection('archived_chat_rooms').document(chat_room.id).set(data)

            # Delete the original chat room document
            chat_room.delete()

