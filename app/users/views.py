from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from traitlets import Instance
from users.forms import ProfileForm, UserLoginForm, UserRegistrationForm


def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Ви зайшли в аккаунт")

                if request.POST.get('next', None):
                    return HttpResponseRedirect(request.POST.get('next'))
                
                return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserLoginForm()
         
    context = {
        "title": "Home - Логін",
        "form": form,
    }
    return render(request, "users/login.html", context=context)


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            messages.success(request, f"{user.username}, Ви успішно зареєструвалися, заходьте в аккаунт")
            return HttpResponseRedirect(reverse("users:login"))
    else:
        form = UserRegistrationForm()
    print("errors=",form.errors) 

    context = {
        "title": "Home - Реєстрація",
        "form": form,
    }
    return render(request, "users/registrations.html",context=context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(
            data=request.POST, instance=request.user, files=request.FILES
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профайл успішно оновлено")
            return HttpResponseRedirect(reverse("users:profile"))
    else:
        form = ProfileForm(instance=request.user)

    context = {
        "title": "Home - Профіль",
        "form": form,
    }
    return render(request, "users/edit_profile.html", context=context)

@login_required
def profile(request):
    context = {
        "title": "Home - Мій профіль",
        "user": request.user,  # Поточний користувач
    }
    return render(request, "users/profile.html", context=context)

@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Ви вийшли з аккаунту")
    auth.logout(request)
    return redirect(reverse("main:index"))
