from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.mail import send_mail
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control
from SMS.settings import DEBUG
from .decorators import lecturer_required, student_required, admin_required
from course.models import Course
from result.models import TakenCourse
from app.models import Session, Semester
from .forms import StaffAddForm, StudentAddForm, ProfileUpdateForm, ParentAddForm
from .models import User, Student, Parent
from django.template.loader import render_to_string

def validate_username(request):
    username = request.GET.get("username", None)
    data = {
        "is_taken": User.objects.filter(username__iexact = username).exists()
    }
    return JsonResponse (data)

def register(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            form.save()

            # Sending email to the user
            subject = 'Welcome to Kreeck Academy!'
            template = 'emails/welcome.html'

            message = render_to_string(template)
            #If the software is in the local server it doesnt use the email functionality
            if DEBUG:
                pass
            else:
                send_mail(subject, '', 'dave@kreeck.com.com', [form.cleaned_data['email']], html_message=message)
                send_mail(
                    subject="A new User Has joined KreeckAcademy",
                    message=f"A new user with username: {form.cleaned_data['username']} and email: {form.cleaned_data['email']} has joined Kreeck Academy.",
                    from_email="dave@kreeck.com",
                    recipient_list=["kreeckinc@gmail.com"]
                )

            messages.success(request, 'Account created successfully.')
        else:
            messages.error(request, 'Something is not correct, please fill all fields correctly.')
    else:
        form = StudentAddForm()

    return render(request, "registration/register.html", {'form': form})


@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def profile(request):
    """ Show profile of any user that fire out the request """
    try:
        current_session = get_object_or_404(Session, is_current_session=True)
        current_semester = get_object_or_404(Semester, is_current_semester=True, session=current_session)
        
    except Semester.MultipleObjectsReturned and Semester.DoesNotExist and Session.DoesNotExist:
        raise Http404

    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(
            semester=current_semester)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "courses": courses,
            'current_session': current_session,
            'current_semester': current_semester,
        })
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        try:
            parent = Parent.objects.get(student=level)
        except:
            parent = "no parent set"
        courses = TakenCourse.objects.filter(student__student__id=request.user.id, course__level=level.level)
        context = {
            'title': request.user.get_full_name,
            'parent': parent,
            'courses': courses,
            'level': level,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'profile/profile.html', context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(request, 'profile/profile.html', {
            'title': request.user.get_full_name,
            "staff": staff,
            'current_session': current_session,
            'current_semester': current_semester,
        })

@cache_page(60 * 40 )
@login_required
@admin_required
def profile_single(request, id):
    """ Show profile of any selected user """
    if request.user.id == id:
        return redirect("/profile/")

    current_session = get_object_or_404(Session, is_current_session=True)
    current_semester = get_object_or_404(Semester, is_current_semester=True, session=current_session)
    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(semester=current_semester)
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "Lecturer",
            "courses": courses,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = TakenCourse.objects.filter(student__student__id=id, course__level=student.level)
        context = {
            'title': user.get_full_name,
            'user': user,
            "user_type": "student",
            'courses': courses,
            'student': student,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)
    else:
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "superuser",
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)

@cache_page(60 * 40 )
@login_required
@admin_required
def admin_panel(request):
    return render(request, 'setting/admin_panel.html', {})

@cache_page(60 * 40 )
@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'setting/profile_info_change.html', {
        'title': 'Setting | Kreeck Academy',
        'form': form,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below. ')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'setting/password_change.html', {
        'form': form,
    })
# ########################################################
@cache_page(60 * 40 )
@login_required
@admin_required
def staff_add_view(request):
    if request.method == 'POST':
        form = StaffAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, "Account for lecturer " + first_name + ' ' + last_name + " has been created.")
            return redirect("lecturer_list")
    else:
        form = StaffAddForm()

    context = {
        'title': 'Lecturer Add | Kreeck Academy',
        'form': form,
    }

    return render(request, 'accounts/add_staff.html', context)


@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, 'Lecturer ' + full_name + ' has been updated.')
            return redirect('lecturer_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_lecturer.html', {
        'title': 'Edit Lecturer | Kreeck Academy',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class LecturerListView(ListView):
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lecturers | Kreeck Academy"
        return context


# @login_required
# @lecturer_required
# def delete_staff(request, pk):
#     staff = get_object_or_404(User, pk=pk)
#     staff.delete()
#     return redirect('lecturer_list')

@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, 'Lecturer ' + full_name + ' has been deleted.')
    return redirect('lecturer_list')
# ########################################################


# ########################################################
# Student views
# ########################################################

def student_add_view(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, 'Account for ' + first_name + ' ' + last_name + ' has been created.')
            return redirect('student_list')
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = StudentAddForm()

    return render(request, 'accounts/add_student.html', {
        'title': "Add Student | Kreeck Academy",
        'form': form
    })


@login_required
@admin_required
def edit_student(request, pk):
    # instance = User.objects.get(pk=pk)
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ('Student ' + full_name + ' has been updated.'))
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_student.html', {
        'title': 'Edit-profile | Kreeck Academy',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class StudentListView(ListView):
    template_name = "accounts/student_list.html"
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get('student_id')
        if query is not None:
            queryset = queryset.filter(Q(department=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Students | Kreeck Academy"
        return context


@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # full_name = student.user.get_full_name
    student.delete()
    messages.success(request, 'Student has been deleted.')
    return redirect('student_list')
# ########################################################


class ParentAdd(CreateView):
    model = Parent
    form_class = ParentAddForm
    template_name = 'accounts/parent_form.html'


# def parent_add(request):
#     if request.method == 'POST':
#         form = ParentAddForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('student_list')
#     else:
#         form = ParentAddForm(request.POST)
