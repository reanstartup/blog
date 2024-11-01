from django.core.management.base import BaseCommand
from blog.models import BlogPost
from firebase_admin import firestore
from django.utils.timezone import make_aware
from datetime import datetime

class Command(BaseCommand):
    help = 'Syncs Firestore data to Django database'

    def convert_timestamp(self, timestamp):
        if timestamp:
            # DatetimeWithNanoseconds is already a datetime object
            return make_aware(timestamp)
        return None

    def handle(self, *args, **options):
        db = firestore.client()
        blog_posts = db.collection('blog_posts').stream()

        for post in blog_posts:
            data = post.to_dict()
            
            # Convert Firestore timestamps to Django-compatible datetime objects
            timestamp_fields = ['created_at', 'updated_at', 'published_at']
            for field in timestamp_fields:
                if field in data and data[field]:
                    try:
                        data[field] = self.convert_timestamp(data[field])
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Could not convert {field} timestamp for post {data.get("title")}: {str(e)}'))
                        data[field] = None

            try:
                BlogPost.objects.update_or_create(
                    slug=post.id,
                    defaults=data
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully synced post: {data.get("title")}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error syncing post {data.get("title")}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Finished syncing Firestore data'))