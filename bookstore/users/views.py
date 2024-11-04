from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import logout



# Create your views here.
def userRegistration(request):
    
    if request.method=='POST':
        username=request.POST.get('username')
        firstName=request.POST.get('firstname')
        lastName=request.POST.get('lastname')
        email=request.POST.get('email')
        password=request.POST.get('password')
        cpassword=request.POST.get('cpassword')
        if password==cpassword:
            if User.objects.filter(username=username).exists():
                print(User.objects.filter(username=username))
                print("dhfdgfdj")
                messages.error(request,"username already exist")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request,"this email already exist")
                return redirect('signup')
            else:
                user=User.objects.create_user(first_name=firstName,last_name=lastName, username=username,email=email,password=password)
                messages.success(request, "Profile successfully created.")
                return redirect('login')
        else:
            messages.error(request, " password not match.")
    return render(request,'userreg.html')

def loginpage(request):
    
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            if user.is_staff:
                return redirect('dashboard')
            else:
                return redirect('booklist_main')
        else:
            messages.error(request,"invalid credentials")
    return render(request,'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  