import firebase_admin
from firebase_admin import credentials, firestore
import time
import os

# 1. Initialize the Link
# Ensure your json file is named exactly 'service-account.json'
cred = credentials.Certificate('service-account.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

def on_command(doc_snapshot, changes, read_time):
    """
    This function triggers INSTANTLY when a document is added/changed in Firestore.
    """
    for change in changes:
        if change.type.name == 'ADDED':
            data = change.document.to_dict()
            doc_id = change.document.id
            
            # Ignore if already completed
            if data.get('status') != 'pending':
                return

            print(f"\n📨 NEW ORDER RECEIVED: {data.get('action')}")
            print(f"   (ID: {doc_id})")
            
            # ⚡️ HERE IS WHERE WE WILL TRIGGER THE BODY LATER
            process_command(doc_id, data.get('action'))

def process_command(doc_id, action):
    print("   ⚙️ Processing...")
    time.sleep(1) # Fake work for now
    
    # Update status to 'completed' in the cloud
    db.collection('commands').document(doc_id).update({
        'status': 'completed',
        'response': 'I heard you! Ghost mode standing by.'
    })
    print("   ✅ Order Complete. Status updated in Cloud.")

def listen():
    print("📡 G-BOT LISTENING UNLINKED [Waiting for Firebase Commands]...")
    
    # Watch the 'commands' collection for any doc where status == 'pending'
    # Note: You might need to create a composite index in Firebase Console if this complains,
    # but for small datasets, it often just works.
    query = db.collection('commands').where('status', '==', 'pending')
    query.on_snapshot(on_command)
    
    # Keep the script running forever
    while True:
        time.sleep(1)

if __name__ == "__main__":
    listen()
