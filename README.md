#  Orbit 

Orbit is a modern team collaboration platform inspired by tools like Microsoft Teams.
It enables organizations to collaborate in real-time with live meetings, screen sharing,
projects, tasks, and role-based access.

---

##  Features

###  Organizations & Roles
- Create organizations
- Owner / Member roles
- Invite users to organizations

###  Project & Task Management
- Create projects inside organizations
- Tasks with status (To-Do / In Progress / Done)
- Assign tasks to members
- Comments & activity tracking

###  Real-Time Meetings (WebRTC)
- Live meeting rooms per organization
- Screen sharing
- Audio control (mute / unmute)
- Host-only meeting start
- Real-time user join notifications
- WebSocket signaling (Django Channels)

###  Real-Time Tech
- WebSocket signaling using Django Channels
- WebRTC peer connections
- Auto-reconnect handling
- Stable signaling state management

---

##  Tech Stack

**Backend**
- Django 5
- Django Channels
- ASGI (Daphne)
- SQLite (dev)

**Frontend**
- HTML / CSS (Custom UI)
- Vanilla JavaScript
- WebRTC API
- WebSocket API

---

## Screenshots

### Dashboard
![Dashboard](Orbit\orbit\screenshots\2.PNG)

### Organization
![Organization](Orbit\orbit\organization.png)

### Sign In
![Sign In](Orbit\orbit\screenshots/signin.png)

---
python manage.py migrate
python manage.py createsuperuser
