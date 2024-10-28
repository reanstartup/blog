from firebase_admin import firestore
from django.utils import timezone

# Get a reference to the Firestore database
db = firestore.client()

def get_all_posts():
    posts = []
    docs = db.collection('posts').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    for doc in docs:
        post = doc.to_dict()
        post['id'] = doc.id
        posts.append(post)
    return posts

def get_post(slug):
    docs = db.collection('posts').where('slug', '==', slug).limit(1).stream()
    for doc in docs:
        post = doc.to_dict()
        post['id'] = doc.id
        return post
    return None

def create_post(title, content, author, content_type, image_url, tags, slug):
    doc_ref = db.collection('posts').document()
    doc_ref.set({
        'title': title,
        'content': content,
        'author': author,
        'content_type': content_type,
        'image_url': image_url,
        'tags': tags,
        'slug': slug,
        'views_count': 0,
        'likes_count': 0,
        'created_at': timezone.now(),
        'updated_at': timezone.now(),
        'is_published': True,
        'excerpt': content[:500] if content else '',
    })
    return doc_ref.id

def update_post(post_id, update_data):
    doc_ref = db.collection('posts').document(post_id)
    doc_ref.update(update_data)

def delete_post(post_id):
    db.collection('posts').document(post_id).delete()
