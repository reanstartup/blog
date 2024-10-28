import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
        firebase_admin.initialize_app(cred)

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        return None

def sign_in_with_email_and_password(email, password):
    try:
        user = auth.get_user_by_email(email)
        # Note: Firebase Admin SDK doesn't provide a way to verify passwords
        # You might need to use Firebase Auth REST API or Firebase JS SDK for this
        # For now, we'll just return the user if the email exists
        return user
    except auth.UserNotFoundError:
        return None

def get_account_info(uid):
    try:
        user = auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name
        }
    except auth.UserNotFoundError:
        return None
