from django.urls import path
from . import views
from .views import (
    create_organization_view,
    dashboard_view,
    create_project_view,
    project_detail_view,
    create_task_view,
    change_task_status_view,
    add_comment_view,
    organization_detail_view,
    invite_user_view,
    my_invites_view,
   accept_invite_view,
 

)

urlpatterns = [
    path("create/", create_organization_view, name="create_organization"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("projects/create/", create_project_view, name="create_project"),
    path("projects/<int:project_id>/", project_detail_view, name="project_detail"),
    path("projects/<int:project_id>/tasks/create/", create_task_view, name="create_task"),
    path("tasks/<int:task_id>/change-status/", change_task_status_view, name="change_task_status"),
    path("tasks/<int:task_id>/comments/add/", add_comment_view, name="add_comment"),
    path("organizations/<int:org_id>/", organization_detail_view, name="organization_detail"),
    path("<int:org_id>/invite/", invite_user_view, name="invite_user"),
    path("invites/", my_invites_view, name="my_invites"),
    path("invites/<int:invite_id>/accept/", accept_invite_view, name="accept_invite"),
    path("tasks/<int:task_id>/edit/", views.edit_task_view, name="edit_task"),
    path("tasks/<int:task_id>/delete/", views.delete_task_view, name="delete_task"),
path("start-meeting/<int:org_id>/", views.start_meeting_view, name="start_meeting"),
path("meeting/<str:room_name>/", views.meeting_room, name="meeting_room"),




]
