from django.contrib import admin
from django.shortcuts import render
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