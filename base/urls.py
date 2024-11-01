from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('', views.home, name="home"),
    path('location/<str:pk>/', views.location, name="location"),
    path('add_location/', views.addLocation, name="add_location"),
    path('update_location/<str:pk>/', views.updateLocation, name="update_location"),  
    path('delete_location/<str:pk>/', views.deleteLocation, name="delete_location"),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
