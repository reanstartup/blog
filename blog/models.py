from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from tinymce.models import HTMLField
from firebase_admin import firestore
from django.contrib import admin
from django.urls import reverse

CONTENT_TYPE_CHOICES = [
    ('MVP', 'MVP'),
    ('skills', 'Skills'),
    ('startup', 'Startup Idea')
]

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    content_type = models.CharField(
        max_length=20, 
        choices=CONTENT_TYPE_CHOICES,
        default='article'
    )
    author = models.CharField(max_length=100, default='Reanstartup')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        managed = False

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Custom save logic for Firestore
        db = firestore.client()
        data = {
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'views_count': self.views_count,
            'content_type': self.content_type,
            'author': self.author,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'published_at': self.published_at,
            'is_published': self.is_published,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'tags': self.tags,
            'likes_count': self.likes_count
        }
        db.collection('blog_posts').document(self.slug).set(data)

    def delete(self, *args, **kwargs):
        # Custom delete logic for Firestore
        db = firestore.client()
        db.collection('blog_posts').document(self.slug).delete()

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

class Subscriber(models.Model):
    class Meta:
        managed = False
        verbose_name_plural = "Subscribers"

    @classmethod
    def get_all_subscribers(cls):
        db = firestore.client()
        subscribers_ref = db.collection('subscribers')
        return subscribers_ref.get()

    def __str__(self):
        return "Subscribers"

# Your other models (like BlogPost) should be here as well

class BlogPostAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        # Delete from SQLite
        super().delete_model(request, obj)
        
        # Delete from Firestore
        db = firestore.client()
        db.collection('blog_posts').document(obj.slug).delete()

    def delete_queryset(self, request, queryset):
        # Delete from SQLite
        super().delete_queryset(request, queryset)
        
        # Delete from Firestore
        db = firestore.client()
        for obj in queryset:
            db.collection('blog_posts').document(obj.slug).delete()

    def save_model(self, request, obj, form, change):
        try:
            if not obj.author:
                obj.author = request.user.username
            
            # Save to SQLite
            super().save_model(request, obj, form, change)
            
            # Save to Firestore
            db = firestore.client()
            data = {
                'title': obj.title,
                'content': obj.content,
                'image_url': obj.image_url,
                'views_count': obj.views_count,
                'content_type': obj.content_type,
                'author': obj.author,
                'created_at': obj.created_at,
                'updated_at': obj.updated_at,
                'published_at': obj.published_at,
                'is_published': obj.is_published,
                'slug': obj.slug,
                'excerpt': obj.excerpt,
                'tags': obj.tags,
                'likes_count': obj.likes_count
            }
            db.collection('blog_posts').document(obj.slug).set(data)
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error saving to Firestore: {e}")
            raise
