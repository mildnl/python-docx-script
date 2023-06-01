import firebase_admin 
from firebase_admin import credentials, firestore

class FirebaseHelper:
    def __init__(self):
        self.initialize_firebase_service_account()
        self.db = self.access_firestore()

    def initialize_firebase_service_account(self):
        # Use a service account
        cred = credentials.Certificate("config/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    
    def access_firestore(self):
        # Access Firestore using the default project ID
        return firestore.client()
    
    def access_collection(self, collection_name):
        return self.db.collection(collection_name)
    
    def access_collection_document(self, book_name):
        document = self.db.collection(u'Books').document(f'{book_name}')
        if document is not None:
            return document
        else:
            document = self.db.collection(u'books').document(f'{book_name}')
            if document is not None:
                return document
            else:
                return self.db.collection(u'New World Translation').document(f'{book_name}')
    
    def book_exists(self, book_name):
        document = self.access_collection_document(book_name)
        return document.get().exists

    def get_db(self):
        return self.db