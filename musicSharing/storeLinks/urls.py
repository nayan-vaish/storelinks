from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from . import views

urlpatterns = [
    # ex: /storeLinks/5/
    path('', views.showList, name='showList'),
    path('<int:status>/', views.showList, name='showList'),
    path('<int:status>/<str:shared>', views.showList, name='showList'),
    path('manageSharedLink/<int:status>/', views.manageSharedLinks, name='manageSharedLinks'),
    path('manageSharedLink/<int:status>/<int:id>/', views.manageSharedLinks, name='manageSharedLinks'),
    path('deleteLink/<int:status>/<int:id>', views.deleteLink, name='deleteLink'),
    path('shareLink/<int:status>/<int:id>', views.shareLink, name='shareLink'),
    path('changeStatusofLink/<int:current_status>/<int:to_status>/<int:id>', views.changeStatusofLink, name='changeStatusofLink'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
