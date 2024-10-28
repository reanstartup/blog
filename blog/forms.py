from django import forms
from .models import BlogPost
from tinymce.widgets import TinyMCE

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image_url', 'content_type', 'tags', 'excerpt']
