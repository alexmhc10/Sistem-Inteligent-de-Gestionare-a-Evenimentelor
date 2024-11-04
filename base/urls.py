from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutPage, name="logout"),
    path('', views.home, name="home"),
    path('location/<str:pk>/', views.location, name="location"),
    path('profile/<str:username>/', views.profilePage, name='profile'),
    path('new_users/', views.new_users, name='new_users'),
    path('approve_user/<int:pk>/', views.approve_user, name='approve_user'),
    path('add_location/', views.addLocation, name="add_location"),
    path('update_location/<str:pk>/', views.updateLocation, name="update_location"),  
    path('delete_location/<str:pk>/', views.deleteLocation, name="delete_location"),  
    path('delete_review/<str:pk>/', views.deleteReview, name="delete_review"),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
