"""
URL configuration for kazi_Connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('register', views.register, name='register'),
    path('login_user', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('skills_input/<int:user_id>/', views.skills_input, name='skills_input'),
    path('listings/create', views.create, name='create'),
    path('listings/<int:job_id>/', views.details, name='details'),
    path('listings/<int:job_id>/apply/', views.apply, name='apply'),
    # Other URLs
    path('listings/<int:id>/manage/', views.manage, name='manage'),
    path('listings/<int:id>/delete/', views.delete_listing, name='delete_listing'),
    path('applications', views.applications, name='applications'),
    path('applications/update_status/', views.update_status, name='update_status'),
    path('listings/search/', views.job_search, name='job_search'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
