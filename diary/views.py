from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from datetime import date
import bcrypt 

def index(request): 
    request.session.flush()
    return render(request, "index.html")

def create_user(request):
    if request.method != "POST":
        return redirect("/")
    errors = User.objects.registration_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/")
    hashedPW = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt(10)).decode()
    new_user=User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=hashedPW )
    request.session["userID"] = new_user.id
    return redirect('/dashboard')

def login(request):
    if request.method != "POST":
        return redirect("/")
    errors = User.objects.login_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/")
    current_user = User.objects.filter(email = request.POST['email'])[0]
    request.session["userID"] = current_user.id
    return redirect('/dashboard')

def logout(request): 
    request.session.flush()
    return redirect("/")

def user(request,  user_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "user.html", context)

def user_edit(request,  user_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "edit_user.html", context)

def user_update(request,  user_id):
    errors = User.objects.update_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/user/"+str(user_id)+"/edit/")
    else:
        hashedPW = bcrypt.hashpw(request.POST['new_password'].encode(), bcrypt.gensalt(10)).decode()
        update_user = User.objects.get(id = user_id)
        update_user.first_name = request.POST["first_name"]
        update_user.last_name = request.POST["last_name"]
        update_user.email = request.POST["email"]
        update_user.password = hashedPW
        update_user.save()
        return redirect("/dashboard")

def dashboard(request): 
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
        "open_groups" : Group.objects.filter(closed = False),
    }
    return render(request, 'dashboard.html', context)

def new_group(request):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "new_group.html", context)

def create_group(request):
    errors = Group.objects.group_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/new_group")
    else:
        this_user = User.objects.get(id = request.session["userID"])
        new_group = Group.objects.create(group_name = request.POST["group_name"], max_members = request.POST["max_members"])
        new_group.members.add(this_user)
        this_user.created_groups.add(new_group)
        this_user.dungeon_master.add(new_group)
        
        return redirect("/group/"+str(new_group.id))

def group(request,  group_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_group": Group.objects.get(id =group_id),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "group.html", context)

def group_edit(request,  group_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_group": Group.objects.get(id =group_id),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "edit_group.html", context)

def group_update(request,  group_id):
    errors = Group.objects.group_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/group/"+str(group_id)+"/edit/")
    else:
        update_group = Group.objects.get(id = group_id)
        update_group.group_name = request.POST["group_name"]
        # update_group.DM = request.POST["DM"]
        # update_group.closed = request.POST["closed"]
        update_group.max_members = request.POST["max_members"]
        # update_group.members = request.POST["members"]
        update_group.save()
        return redirect("/group/"+str(group_id))

def group_delete(request, group_id):
    delete_group = Group.objects.get(id = group_id)
    delete_group.delete()
    return redirect("/dashboard")

def group_search(request):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "groups" : Group.objects.all(),
        "open_groups" : Group.objects.filter(closed = False),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "find_group.html", context)

def group_join(request,  group_id):
    this_group = Group.objects.get(id = group_id)
    this_user = User.objects.get(id = request.session["userID"])
    this_group.members.add(this_user)
    if (this_group.members.count()) >= this_group.max_members:
        this_group.closed = True
    return redirect("/group/"+str(this_group.id))

def group_leave(request,  group_id):
    this_group = Group.objects.get(id = group_id)
    this_user = User.objects.get(id = request.session["userID"])
    if this_group.DM == this_user:
        this_user.dungeon_master.remove(this_group)
    this_group.members.remove(this_user)
    if (this_group.members.count()) < this_group.max_members:
        this_group.closed = False
    return redirect("/group/"+str(this_group.id))

def group_open(request, group_id):
    this_group = Group.objects.get(id = group_id)
    this_group.closed = False
    this_group.save()
    return redirect("/group/"+str(this_group.id))

def group_close(request, group_id):
    this_group = Group.objects.get(id = group_id)
    this_group.closed = True
    this_group.save()
    return redirect("/group/"+str(this_group.id))

def schedule (request,  group_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_group": Group.objects.get(id =group_id),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "schedule.html", context)

def session_create(request): 
    errors = Session.objects.schedule_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/schedule/"+str(request.POST["group_id"]))
    else:
        this_group = Group.objects.get(id = request.POST["group_id"])
        new_session = Session.objects.create(date = request.POST["date"], time = request.POST["time"], schedule_notes = request.POST["schedule_notes"], group = this_group)
        return redirect("/dashboard")

def schedule_edit (request,  group_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_group": Group.objects.get(id =group_id),
        "this_session" : Session.objects.filter(group = group_id).last(),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
    }
    return render(request, "edit_schedule.html", context)

def schedule_update (request,  group_id):
    errors = Session.objects.schedule_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/session/"+str(session_id)+"/group/"+str(group_id)+"/edit/")
    else:
        update_session = Session.objects.get(id = session_id)
        update_session.date = request.POST["date"]
        update_session.time = request.POST["time"]
        update_session.schedule_notes = request.POST["schedule_notes"]
        update_session.save()
        return redirect("/dashboard")

def schedule_delete(request, session_id):
    delete_session = Session.objects.get(id = session_id)
    delete_session.delete()
    return redirect("/dashboard")

def session(request, session_id, group_id):
    today = date.today()
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_session": Session.objects.get(id = session_id),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
        "today" : today,
        "this_group" : Group.objects.get(id = group_id)
    }
    return render(request, "session.html", context)

def session_edit(request,  session_id, group_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_session": Session.objects.get(id = session_id),
        "this_user" : User.objects.get(id = request.session["userID"]),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
        "this_group" : Group.objects.get(id = group_id),
    }
    return render(request, "edit_session.html", context)

def session_update(request, session_id, group_id):
    errors = Session.objects.session_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/session/"+str(session_id)+"/group/"+str(group_id)+"/edit/")
    else:
        update_session = Session.objects.get(id = session_id)
        update_session.date = request.POST["date"]
        update_session.time = request.POST["time"]
        update_session.schedule_notes = request.POST["schedule_notes"]
        update_session.session_notes = request.POST["session_notes"]
        update_session.npcs_met = request.POST["npcs_met"]
        update_session.monsters = request.POST["monsters"]
        update_session.treasure = request.POST["treasure"]
        update_session.save()
        return redirect("/dashboard/")

def archive (request,  group_id):
    if "userID" not in request.session:
        messages.error(request, "Please log in")
        return redirect("/")
    context={
        "this_user" : User.objects.get(id = request.session["userID"]),
        "groups" : Group.objects.filter(members = request.session["userID"]),
        "sessions" : Session.objects.filter(group = group_id).all(),
        "user_groups" : Group.objects.filter(members = request.session["userID"]),
        "this_group": Group.objects.get(id =group_id),
    }
    return render(request, "archive.html", context)

def archive_session(request,  session_id):
        update_session = Session.objects.get(id = session_id)
        update_session.archived = True
        update_session.save()
        return redirect("/dashboard")

def add_dm(request, group_id):
    this_user = User.objects.get(id = request.session["userID"])
    this_group = Group.objects.get(id = group_id)
    this_group.members.add(this_user)
    this_user.dungeon_master.add(this_group)
    return redirect("/group/"+str(this_group.id))

def remove_dm(request, group_id): 
    this_user = User.objects.get(id = request.session["userID"])
    this_group = Group.objects.get(id = group_id)
    this_user.dungeon_master.remove(this_group)
    return redirect("/group/"+str(this_group.id))