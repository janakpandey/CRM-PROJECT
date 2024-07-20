from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def home(request):
    if request.user.is_authenticated:
        records = Record.objects.filter(user=request.user)
    else:
        records = []
    # Check to see if logging in
    if request.GET.get('search'):
        records = records.filter(
            first_name__icontains=request.GET.get('search')) | records.filter(last_name__icontains=request.GET.get('search'))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.error(
                request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')

    return render(request, 'home.html', {'records': records})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(
                request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})


@login_required
def customer_record(request, pk):
    try:
        customer_record = Record.objects.get(id=pk, user=request.user)
    except Record.DoesNotExist:
        messages.error(
            request, "Record does not exist or you don't have permission to view it.")
        return redirect('home')

    return render(request, 'record.html', {'customer_record': customer_record})


@login_required
def delete_record(request, pk):
    try:
        delete_it = Record.objects.get(id=pk, user=request.user)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
    except Record.DoesNotExist:
        messages.error(
            request, "Record does not exist or you don't have permission to delete it.")

    return redirect('home')


@login_required
def add_record(request):
    if request.method == "POST":
        form = AddRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            messages.success(request, "Record Added...")
            return redirect('home')
    else:
        form = AddRecordForm()

    return render(request, 'add_record.html', {'form': form})


@login_required
def update_record(request, pk):
    try:
        current_record = Record.objects.get(id=pk, user=request.user)
        if request.method == "POST":
            form = AddRecordForm(request.POST, instance=current_record)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Has Been Updated!")
                return redirect('home')
        else:
            form = AddRecordForm(instance=current_record)

        return render(request, 'update_record.html', {'form': form})
    except Record.DoesNotExist:
        messages.error(
            request, "Record does not exist or you don't have permission to update it.")
        return redirect('home')
