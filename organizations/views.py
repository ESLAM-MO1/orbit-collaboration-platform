from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Organization, Project, Task, Comment, OrganizationMembership, OrganizationInvite, Activity, MeetingRoom
from django.contrib import messages
from django.contrib.auth import get_user_model
import uuid
@login_required
def create_organization_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            organization = Organization.objects.create(
                name=name,
                owner=request.user
            )
            OrganizationMembership.objects.create(
                user=request.user,
                organization=organization,
                role="owner"
            )
            return redirect("dashboard")
    return render(request, "organizations/create_organization.html")


@login_required
def dashboard_view(request):
    memberships = request.user.memberships.select_related("organization")
    organizations = [m.organization for m in memberships]

    invites = request.user.organization_invites.all()
    invites_count = invites.count()

    return render(request, "organizations/dashboard.html", {
        "organizations": organizations,
        "invites_count": invites_count,
        "username": request.user.username,
    })


@login_required
def organization_detail_view(request, org_id):
    membership = OrganizationMembership.objects.filter(
        user=request.user,
        organization_id=org_id
    ).first()

    if not membership:
        return redirect("dashboard")

    organization = membership.organization
    projects = organization.projects.all()

    members = OrganizationMembership.objects.select_related("user").filter(
        organization=organization
    )
  # نجيب آخر 10 أنشطة
    activities = organization.activities.order_by("-created_at")[:10]

    return render(request, "organizations/organization_detail.html", {
        "organization": organization,
        "projects": projects,
        "members": members,
        "membership": membership,
        "activities": activities,
    })


@login_required
def create_project_view(request):
    org_id = request.GET.get("org")

    if not org_id:
        return redirect("dashboard")

    membership = OrganizationMembership.objects.filter(
        user=request.user,
        organization_id=org_id
    ).first()

    if not membership:
        return redirect("dashboard")

    organization = membership.organization

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        if name:
            project = Project.objects.create(
                organization=organization,
                name=name,
                description=description
            )

            # Activity Log
            Activity.objects.create(
                organization=organization,
                user=request.user,
                action=f"created project '{project.name}'"
            )

            return redirect("organization_detail", org_id=organization.id)

    return render(request, "organizations/create_project.html", {
        "organization": organization
    })


@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project,
        id=project_id,
        organization__memberships__user=request.user
    )

    tasks = project.tasks.all()

    return render(request, "organizations/project_detail.html", {
        "project": project,
        "tasks": tasks
    })


@login_required
def create_task_view(request, project_id):
    project = get_object_or_404(
        Project,
        id=project_id,
        organization__memberships__user=request.user
    )

    users = [m.user for m in project.organization.memberships.select_related("user")]

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to_id = request.POST.get("assigned_to")

        assigned_user = None
        if assigned_to_id:
            assigned_user = next(
                (u for u in users if str(u.id) == assigned_to_id),
                None
            )

        if title:
            task = Task.objects.create(
                project=project,
                title=title,
                description=description,
                assigned_to=assigned_user
            )

            # Activity Log
            Activity.objects.create(
                organization=project.organization,
                user=request.user,
                action=f"created task '{task.title}'"
            )

            return redirect("project_detail", project_id=project.id)

    return render(request, "organizations/create_task.html", {
        "project": project,
        "users": users
    })


@login_required
def change_task_status_view(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        project__organization__memberships__user=request.user
    )

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["todo", "in_progress", "done"]:
            task.status = new_status
            task.save()

    return redirect("project_detail", project_id=task.project.id)


@login_required
def add_comment_view(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        project__organization__memberships__user=request.user
    )

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(
                task=task,
                user=request.user,
                content=content
            )

    return redirect("project_detail", project_id=task.project.id)



User = get_user_model()

@login_required
def invite_user_view(request, org_id):
    # نتأكد إن اليوزر عضو في الأورجانايزيشن
    membership = OrganizationMembership.objects.filter(
        user=request.user,
        organization_id=org_id
    ).first()

    if not membership:
        return redirect("dashboard")

    # بس الـ Owner يقدر يبعت دعوات
    if membership.role != "owner":
        messages.error(request, "Only the organization owner can send invitations.")
        return redirect("organization_detail", org_id=org_id)

    organization = membership.organization

    if request.method == "POST":
        username = request.POST.get("username")

        try:
            invited_user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("organization_detail", org_id=org_id)

        # نتأكد إنه مش عضو بالفعل
        if OrganizationMembership.objects.filter(
            user=invited_user,
            organization=organization
        ).exists():
            messages.error(request, "User is already a member of this organization.")
            return redirect("organization_detail", org_id=org_id)

        # نتأكد إنه مفيش دعوة قديمة
        if OrganizationInvite.objects.filter(
            invited_user=invited_user,
            organization=organization
        ).exists():
            messages.error(request, "This user already has a pending invite.")
            return redirect("organization_detail", org_id=org_id)

        OrganizationInvite.objects.create(
            organization=organization,
            invited_user=invited_user,
            invited_by=request.user
        )
        #Activity

        Activity.objects.create(
    organization=organization,
    user=request.user,
    action=f"invited {invited_user.username}"
)


        messages.success(request, "Invitation sent successfully.")
        return redirect("organization_detail", org_id=org_id)

    return render(request, "organizations/invite_user.html", {
        "organization": organization
    })

@login_required
def my_invites_view(request):
    invites = OrganizationInvite.objects.filter(
        invited_user=request.user,
        is_accepted=False
    ).select_related("organization", "invited_by")

    return render(request, "organizations/my_invites.html", {
        "invites": invites
    })

@login_required
def accept_invite_view(request, invite_id):
    invite = get_object_or_404(
        OrganizationInvite,
        id=invite_id,
        invited_user=request.user
    )

    # نضيف العضوية
    OrganizationMembership.objects.create(
        user=request.user,
        organization=invite.organization,
        role="member"
    )

    #Activity
    Activity.objects.create(
    organization=invite.organization,
    user=request.user,
    action="joined the organization"
)


    # نمسح الدعوة
    invite.delete()

    return redirect("dashboard")

@login_required
def edit_task_view(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        project__organization__memberships__user=request.user
    )

    organization = task.project.organization
    members = organization.memberships.select_related("user")
    users = [m.user for m in members]

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        status = request.POST.get("status")
        assigned_to_id = request.POST.get("assigned_to")

        assigned_user = None
        if assigned_to_id:
            assigned_user = User.objects.filter(id=assigned_to_id).first()

        task.title = title
        task.description = description
        task.status = status
        task.assigned_to = assigned_user
        task.save()

        return redirect("project_detail", project_id=task.project.id)

    return render(request, "organizations/edit_task.html", {
        "task": task,
        "users": users,
    })
@login_required
def delete_task_view(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        project__organization__memberships__user=request.user
    )

    project_id = task.project.id
    task.delete()
    return redirect("project_detail", project_id=project_id)
@login_required
def meeting_room(request, room_name):
    return render(request, "organizations/meeting.html", {
        "room_name": room_name
    })

import uuid
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Organization, MeetingRoom

@login_required
def start_meeting_view(request, org_id):
    organization = Organization.objects.get(id=org_id)

    room_name = uuid.uuid4().hex[:12]

    meeting = MeetingRoom.objects.create(
        organization=organization,
        host=request.user,
        room_name=room_name
    )

    return redirect("meeting_room", room_name=room_name)