from google.cloud import firestore
import os

# Firestore 初期化
db = firestore.Client()

def save_user(user_id: str):
    doc_ref = db.collection("users").document(user_id)
    doc_ref.set({"user_id": user_id})

def get_all_user_ids():
    users_ref = db.collection("users")
    docs = users_ref.stream()
    return [doc.id for doc in docs]
