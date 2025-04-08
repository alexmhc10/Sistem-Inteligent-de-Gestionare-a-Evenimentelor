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

    # Gestionare utilizatori
    path('profile/<str:username>/', views.profilePage, name='profile'),
    path('new_users/', views.new_users, name='new_users'),
    path('users/', views.users, name='users'),
    path('approve_user/<int:pk>/', views.approve_user, name='approve_user'),
    path('delete_user/<str:pk>/', views.deleteUser, name="delete_user"),
    path('delete_user_admin/<str:pk>/', views.deleteUserAdmin, name="delete_user_admin"),
    path('view_user_admin/<str:pk>/', views.viewUserAdmin, name="view_user_admin"),
    path('view_user_events/<str:pk>/', views.viewUserEvents, name="view_user_events"),
    path('view_user_locations/<str:pk>/', views.viewUserLocations, name="view_user_locations"),
    path('admin_account_settings', views.admin_settings, name="admin_account_settings"),
    path('admin_edit_location/<int:pk>/', views.admin_edit_location, name='admin_edit_location'),

    # Evenimente
    path('edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/guest_list/', views.guest_list, name='guest_list'),
    path('event/<int:event_id>/details/', views.event_details, name='event_details'),
    path('feedback_eveniment/', views.feedback_event, name='feedback_event'),
    path('admin-events', views.admin_events, name="admin-events"),
    path('admin-view-event/<str:pk>/', views.admin_view_events, name="admin-view-event"),
    path('istoric_evenimente/', views.event_history, name='event_history'),
    path('guest_list/', views.guest_list, name='guest_list'),
    path('event/<int:event_id>/', views.vizualizare_eveniment, name='vizualizare_eveniment'),
    path('my_events/', views.my_events, name='my_events'),
    path('event_builder/', views.event_builder, name='event_builder'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
   


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
    path('search/', views.search_food, name="search_food"),
    path('add_food/', views.add_food, name="add_food"),
    path('add_allergen/', views.add_allergen, name="add_allergen"),
    path('get_food_details/<int:food_id>/', views.get_food_details, name="get_food_details"),
    path('update_food/<int:food_id>/', views.update_food, name='update_food'),
    path('delete_dish/<int:dish_id>/', views.delete_dish, name='delete_dish'),

    # Sarcini (Tasks)
    path('add-task/', views.add_task, name='add_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),



    #Formular invitati
    path('invite_form/<int:event_id>/<int:guest_id>', views.invite_form, name='invite_form'),

    #Personal
    path('personal_eveniment_home/', views.personal_eveniment_home, name='personal_eveniment_home'),
    path('personal_vizualizare_eveniment/<int:pk>', views.personal_vizualizare_eveniment, name='personal_vizualizare_eveniment'),
    path('personal_aranjament_invitati/', views.personal_aranjament_invitati, name='personal_aranjament_invitati'),
    path('personal_aranjament_invitati/<int:pk>', views.personal_aranjament_invitati, name='personal_aranjament_invitati_event'),
    path('personal_face_id/<int:pk>', views.personal_face_id, name='personal_face_id'),
    path('personal_profile/', views.personal_profile, name='personal_profile'),
    path('upload_images/', views.upload_images, name='upload_images'),
    path("delete-image/<int:image_id>/", views.delete_image, name="delete_image"),
    path("personal_menu/", views.personal_menu, name="personal_menu"),
    

    #Guest
    path('guest_home', views.guest_home, name='guest_home'),
    path('guest_profile', views.guest_profile, name='guest_profile'),
    path('guest_event_view/<int:pk>', views.guest_event_view, name='guest_event_view'),
    path('event_status_api/<int:pk>', views.event_status_api, name='event_status_api'),

    #Postari
    path('like/<int:post_id>', views.like_post, name='like_post'),
    path('comment/<int:post_id>', views.add_comment, name='add_comment'),
    path('delete_post/<int:postId>/', views.delete_post, name='delete_post'),

    #Face_recog
    path('classify/', views.find_user_view, name='classify'),

    #Notifications
    path("send_notification/", views.send_notification, name="send_notification"),
    path("get_notifications/", views.get_notifications, name="get_notifications"),
    path('mark_notifications_as_read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    
    ##organizator
    path('locations/', views.locations_list, name='locations-list'),
    path('home-organizer/', views.home_organizer, name='home-organizer'),
    path('edit-profile/<str:username>/', views.edit_profile, name='edit_profile'),
    path('organizer-profile/<str:username>/', views.organizer_profile, name='organizer-profile'),
    path('organizer-locations', views.organizer_locations, name='organizer_locations'),
    path('organizer-events', views.organizer_events, name='organizer_events')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
