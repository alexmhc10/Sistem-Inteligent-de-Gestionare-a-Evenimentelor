from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Paginile principale și autentificare
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutPage, name="logout"),
    path('admin-home', views.homeAdmin, name="home-admin"),
    path('admin-charts', views.admin_charts, name="admin-charts"),

    # Gestionare utilizatori
    path('profile/<str:username>/', views.profilePage, name='profile'),
    path('new_users/', views.new_users, name='new_users'),
    path('users/', views.users, name='users'),
    path('approve_user/<int:pk>/', views.approve_user, name='approve_user'),
    path('delete_user/<str:pk>/', views.deleteUser, name="delete_user"),
    path('delete_user_admin/<str:pk>/', views.deleteUserAdmin, name="delete_user_admin"),
    path('update_user_admin/<str:pk>/', views.updateUserAdmin, name="update_user_admin"),

    # Evenimente
    path('feedback_eveniment/', views.feedback_event, name='feedback_event'),
    path('admin-events', views.admin_events, name="admin-events"),
    path('admin-view-event/<str:pk>/', views.admin_view_events, name="admin-view-event"),
    path('istoric_evenimente/', views.event_history, name='event_history'),
    path('guest_list/', views.guest_list, name='guest_list'),
    path('event/<int:event_id>/', views.vizualizare_eveniment, name='vizualizare_eveniment'),
    path('my_events/', views.my_events, name='my_events'),
    path('event_builder/', views.event_builder, name='event_builder'),

    # Locații
    path('admin-view-location/<str:name>/', views.admin_view_locations, name="admin-view-location"),
    path('location/<str:pk>/', views.location, name="location"),
    path('add_location/', views.addLocation, name="add_location"),
    path('update_location/<str:pk>/', views.updateLocation, name="update_location"),
    path('delete_location/<str:pk>/', views.deleteLocation, name="delete_location"),
    path('admin-locations', views.admin_locations, name="admin-locations"),

    # Recenzii
    path('delete_review/<str:pk>/', views.deleteReview, name="delete_review"),

    # Meniu
    path('menu-items', views.MenuItems, name="menu-items"),
    path('event-menu/<int:event_id>/', views.MenuForEvent, name="event-menu"),

    # Sarcini (Tasks)
    path('add-task/', views.add_task, name='add_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),

    # Altele
    path('carousel/', views.carousel_view, name='carousel'),

    #Formular invitati
    path('invite_form/', views.invite_form, name='invite_form'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
