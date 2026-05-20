from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/problems/', include('apps.problems.urls')),
    path('api/contests/', include('apps.contests.urls')),
    path('api/submissions/', include('apps.submissions.urls')),
]