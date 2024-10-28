from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from . import views
from blog.sitemaps import BlogPostSitemap, StaticViewSitemap

sitemaps = {
    'blog': BlogPostSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('about/', views.about_us, name='about_us'),
    path('subscribe/', views.subscribe_mailing_list, name='subscribe_mailing_list'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
