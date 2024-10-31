from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.http import JsonResponse
from firebase_admin import firestore

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
                # Initialize Firestore client
                db = firestore.client()

                # Attempt to delete the subscriber document
                subscribers_ref = db.collection('subscribers')
                query = subscribers_ref.where('email', '==', email).get()

                if query:
                    for doc in query:
                        doc.reference.delete()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Subscriber not found.'})
            except Exception as e:
                # Log the error for debugging
                print(f"Error deleting subscriber: {e}")
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion