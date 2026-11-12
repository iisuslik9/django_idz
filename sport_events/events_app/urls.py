from django.urls import path
from . import views

urlpatterns = [
    # Общие страницы (список мероприятий и детали конкретного события)
    path("", views.home, name="home"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),

    # Действия участника
    path("event/<int:event_id>/register/", views.register_for_event, name="register_for_event"),
    path("registration/<int:registration_id>/cancel/", views.cancel_registration, name="cancel_registration"),
    path("cabinet/participant/", views.participant_cabinet, name="participant_cabinet"),

    # Действия организатора и его личный кабинет
    path("cabinet/organizer/", views.organizer_cabinet, name="organizer_cabinet"),
    path("event/create/", views.create_event, name="create_event"),
    path("event/<int:event_id>/manage/", views.manage_event, name="manage_event"),
    path("registration/<int:registration_id>/result/", views.add_or_edit_result, name="add_or_edit_result"),

    path("feedback/", views.feedback_view, name="feedback"),

]
