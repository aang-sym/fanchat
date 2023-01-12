import firebase_admin
from firebase_admin import firestore
from chat_room_manager import ChatRoomManager
import time
import random

# Initialize the Firebase app
firebase_admin.initialize_app()

# Create an instance of the ChatRoomManager
chat_room_manager = ChatRoomManager()

# Create chat rooms for all live NBA matches
chat_room_manager.create_chat_rooms_for_live_matches()

# Get a list of all match_ids
match_ids = chat_room_manager.get_match_ids()

# Loop through all match_ids
for match_id in match_ids:
# Get the chat room for the match
    chat_room = chat_room_manager.get_chat_room(match_id)

    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < 1:
        # Generate a random message and username
        message = f"Hello, World! ({random.randint(1, 100)})"
        username = f"user{random.randint(1, 100)}"

        # Add the message to the chat room
        chat_room.add_message(message, username)

        # Retrieve the messages for the chat room
        messages = chat_room.get_messages()
        print(messages)

        # Pause the loop for 1 second
        time.sleep(0.2)

        # Update the elapsed time
        elapsed_time = time.time() - start_time