from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import loginform, Register_form, UserEditForm, ProfileEditForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Profile, Contact
from actions.utils import create_action
from actions.models import Action

# Create User login view.
def user_login(request):
    if request.method == "POST":
        # create form instance
        form = loginform(request.POST)
        # check if valid inputs are provided
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd["username"], password=cd["password"])
            if user is not None:
                # add user to current session
                login(request, user)
                return HttpResponse("User Authenticated")
            else: 
                return HttpResponse("Invalid credentials")
    else:
        form = loginform()

    return render(request, "social_web/login.html", {'form': form})


@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)

    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    # retrieve first 10 actions
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    return render(request, 'social_web/dashboard.html', {'dashboard': dashboard,
                                                         'section': 'dashboard',
                                                         'actions': actions})


def register(request):
    if request.method == "POST":
        user_form = Register_form(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            new_user.save()

            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request, 'social_web/register_done.html', {'new_user': new_user})
    else:
        user_form = Register_form()
        
    return render(request, 'social_web/register.html', {'user_form': user_form})

@login_required
def edit(request):
    success = None
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            success = True
            messages.success(request, "profile updated successfully")
        else: 
            success = False
            messages.error(request, 'Error updating the profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    
    return render(request, 'social_web/edit.html', {'user_form': user_form,
                                                    'profile_form': profile_form,
                                                    'success': success})

@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    profiles = Profile.objects.all()
    return render(request, 'social_web/users/list.html', {'section': 'people',
                                                          'users': users,
                                                          'profiles': profiles})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    profile = Profile.objects.get(user= user)
    return render(request, 'social_web/users/detail.html', {"section": 'people',
                                                            "user": user,
                                                            'profile': profile})

@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from = request.user,
                                              user_to = user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
                