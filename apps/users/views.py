from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import *

def index(request):
    if 'id' in request.session:
        return redirect('/success')
    return render(request, 'users/index.html')
def register(request):
    if request.method == 'POST':
        errors = User.objects.basic_validator(request.session, request.POST)
        if len(errors) == 0:
            if User.objects.register_new_user(request.session, request.POST):
                return redirect('/success')
            else:
                print("==============Unable to register user==============")
                return redirect('/')
        else:
            print("Found " + str(len(errors)) + " errors!")
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
    else:
        return redirect('/')
def login(request):
    if request.method == 'POST':
        try:
            user = User.objects.validate_login(request.session, request.POST)
            if user:
                return redirect('/success')
            else:
                messages.error(request, "The email and password provided do not match any records in our database")
                return redirect('/')
        except:
            messages.error(request, "We were unable to process your request. Please try again.")
    else:
        return redirect('/')
def success(request):
    if 'id' in request.session:
        name = User.objects.get(id=request.session['id']).first_name
        return render(request, 'users/success.html', {'name':name})
    else:
        messages.error(request, "You must be logged in to view that page.")
        return redirect('/')
def logout(request):
    if 'id' in request.session:
        request.session.pop('id')
    return redirect('/')
def view_user(request, user_id):
    if 'id' in request.session:
        if user_id == 0:
            #redirect to books list if attempting to view the profile of the Guest account-
            messages.error(request, "You don't have permission to view that page.")
            return redirect('/books/list')
        elif len(User.objects.filter(id=user_id)) > 0:
            view_user = User.objects.get(id=user_id)
            name = User.objects.get(id=request.session['id']).first_name
            return render(request, 'users/view.html', {'view_user':view_user, 'name':name})
        else:
            messages.error(request, "That page does not exist.")
            return redirect('/books/list')
    else:
        messages.error(request, "You must be logged in to view that page.")
        return redirect('/')
def catch_and_redirect(request):
    return redirect('/')