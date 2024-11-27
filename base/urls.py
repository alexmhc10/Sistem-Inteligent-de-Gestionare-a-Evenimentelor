from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('eveniment/<int:event_id>/', views.vizualizare_eveniment, name='vizualizare_eveniment'),
    path('event/<int:event_id>/', views.vizualizare_eveniment, name='vizualizare_eveniment'),
    path('my_events/', views.my_events, name='my_events'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    # path('task-manager/', views.task_manager_view, name='task_manager'),
    path('add-task/', views.add_task, name='add_task'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('carousel/', views.carousel_view, name='carousel'),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutPage, name="logout"),
    path('', views.home, name="home"),
    path('admin-home', views.homeAdmin, name="home-admin"),
    path('location/<str:pk>/', views.location, name="location"),
    path('profile/<str:username>/', views.profilePage, name='profile'),
    path('new_users/', views.new_users, name='new_users'),
    path('approve_user/<int:pk>/', views.approve_user, name='approve_user'),
    path('add_location/', views.addLocation, name="add_location"),
    path('update_location/<str:pk>/', views.updateLocation, name="update_location"),  
    path('delete_location/<str:pk>/', views.deleteLocation, name="delete_location"),  
    path('delete_user/<str:pk>/', views.deleteUser, name="delete_user"),  
    path('delete_review/<str:pk>/', views.deleteReview, name="delete_review"),  
    path('menu-items', views.MenuItems, name="menu-items"),  
    path('event-menu/<int:event_id>/', views.MenuForEvent, name="event-menu"),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
