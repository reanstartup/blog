from django.contrib import admin
from .models import BlogPost, Subscriber
from firebase_admin import firestore
from django.shortcuts import render, redirect
from django.urls import path
from django.http import JsonResponse

# Register your models here.

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user.username
        
        # The save() method in the model will handle both Django and Firestore
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # The delete() method in the model will handle both Django and Firestore
        obj.delete()

    def delete_queryset(self, request, queryset):
        # Delete each object individually to ensure both databases are updated
        for obj in queryset:
            obj.delete()

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    change_list_template = 'admin/subscriber_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Fetch subscribers from Firestore
        db = firestore.client()
        subscribers_ref = db.collection('subscribers')
        subscribers = subscribers_ref.get()

        # Convert to list of dicts
        subscriber_list = [
            {
                'email': sub.to_dict()['email'],
                'subscribed_at': sub.to_dict()['subscribed_at'].strftime('%Y-%m-%d %H:%M:%S')
            }
            for sub in subscribers
        ]

        context = {
            'subscribers': subscriber_list,
            **self.admin_site.each_context(request),
            **(extra_context or {})
        }
        return render(request, self.change_list_template, context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete/<str:email>/', self.admin_site.admin_view(self.delete_subscriber), name='delete_subscriber'),
        ]
        return custom_urls + urls

    def delete_subscriber(self, request, email):
        if request.method == 'POST':
            try:
                # Delete subscriber from Firestore using email as document ID
                db = firestore.client()
                db.collection('subscribers').document(email).delete()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
