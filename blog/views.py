from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from firebase_admin import firestore
from .firebase_auth import initialize_firebase
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Initialize Firebase
initialize_firebase()

# Get a reference to the Firestore database
db = firestore.client()

def index(request):
    db = firestore.client()
    blog_posts_ref = db.collection('blog_posts')
    
    try:
        query = blog_posts_ref.where('is_published', '==', True).order_by('published_at', direction=firestore.Query.DESCENDING)
        docs = query.stream()
        blog_posts = []
        for doc in docs:
            post = doc.to_dict()
            post['id'] = doc.id
            blog_posts.append(post)
    except Exception as e:
        print(f"Error executing query: {e}")
        query = blog_posts_ref.where('is_published', '==', True).limit(10)
        docs = query.stream()
        blog_posts = []
        for doc in docs:
            post = doc.to_dict()
            post['id'] = doc.id
            blog_posts.append(post)
    
    return render(request, 'blog/index.html', {'blog_posts': blog_posts})

def blog_detail(request, slug):
    db = firestore.client()
    doc_ref = db.collection('blog_posts').document(slug)
    doc = doc_ref.get()
    
    if doc.exists:
        post = doc.to_dict()
        post['id'] = doc.id
        
        new_view_count = post.get('views_count', 0) + 1
        doc_ref.update({'views_count': new_view_count})
        
        post['views_count'] = new_view_count
        
        return render(request, 'blog/blog_detail.html', {'post': post})
    else:
        return render(request, 'blog/404.html', status=404)

def about_us(request):
    return render(request, 'blog/about_us.html')

def subscribe_mailing_list(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            db = firestore.client()
            subscribers_ref = db.collection('subscribers')
            
            # Check if email already exists
            if subscribers_ref.where('email', '==', email).get():
                return JsonResponse({'status': 'error', 'message': 'This email is already subscribed.'})
            else:
                # Add new subscriber
                subscribers_ref.add({'email': email, 'subscribed_at': firestore.SERVER_TIMESTAMP})
                return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Please enter a valid email address.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def like_post(request, post_id):
    if request.method == 'POST':
        db = firestore.client()
        doc_ref = db.collection('blog_posts').document(post_id)
        doc = doc_ref.get()

        if doc.exists:
            post = doc.to_dict()
            new_like_count = post.get('likes_count', 0) + 1
            doc_ref.update({'likes_count': new_like_count})

            return JsonResponse({'status': 'success', 'new_like_count': new_like_count})
        else:
            return JsonResponse({'status': 'error', 'message': 'Post not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
