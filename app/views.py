from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from accounts.models import Student
from accounts.decorators import admin_required, lecturer_required
from .forms import SessionForm, SemesterForm, NewsAndEventsForm
from blog.models import Blog
from .models import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from SMS.settings import DEBUG
# ########################################################
# News & Events
# ########################################################

@cache_page(60 * 100 )
def landing(request):
    blogs = Blog.objects.all().order_by('-timestamp')
    landing = Landing.objects.all()
    context = {
        'title':'Welcome to kreeck Academy'
    }
    return render(request, 'landing.html', context)

@cache_page(60 * 60 )
@login_required
def home_view(request):
    items = NewsAndEvents.objects.all().order_by('-updated_date')
    context = {
        'title': "News & Events | Kreeck Academy",
        'items': items,
    }
    return render(request, 'app/index.html', context)
"""
this should be ona different environment because someone can easily break the software
"""
@cache_page(60 * 60 )
def compiler(request):
    return render(request, 'compiler/compiler.html')



@login_required
def post_add(request):
    if request.method == 'POST':
        form = NewsAndEventsForm(request.POST)
        title = request.POST.get('title')
        if form.is_valid():
            post = form.save()

            # Send email to students
            students_emails = Student.objects.values_list('student__email', flat=True)
            subject = "New Post Added at Kreeck Academy"
            template = 'emails/new-post.html'
            context = {
                'post': post,
            }

            message = render_to_string(template, context)
            if DEBUG:
                pass
            else:
                # Send the email
                send_mail(subject, '', 'dave@kreeck.com', students_emails, html_message=message)
            messages.success(request, (title + ' has been uploaded.'))
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = NewsAndEventsForm()

    return render(request, 'app/post_add.html', {
        'title': 'Add Post | Kreeck Academy',
        'form': form,
    })


@login_required
@lecturer_required 
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == 'POST':
        form = NewsAndEventsForm(request.POST, instance=instance)
        title = request.POST.get('title')
        if form.is_valid():
            form.save()
            messages.success(request, (title + ' has been updated.'))
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, 'app/post_add.html', {
        'title': 'Edit Post | Kreeck Academy',
        'form': form,
    })



@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewsAndEvents, pk=pk)
    title = post.title
    post.delete()
    messages.success(request, (title + ' has been deleted.'))
    return redirect('home')



# ########################################################
# Session
# ########################################################

@cache_page(60 * 40 )
@login_required
@lecturer_required
def session_list_view(request):
    """ Show list of all sessions """
    sessions = Session.objects.all().order_by('-is_current_session', '-session')
    return render(request, 'app/session_list.html', {"sessions": sessions})


@login_required
@lecturer_required
def session_add_view(request):
    """ check request method, if POST we add session otherwise show empty form """
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            data = form.data.get('is_current_session')  # returns string of 'True' if the user selected Yes
            print(data)
            if data == 'true':
                sessions = Session.objects.all()
                if sessions:
                    for session in sessions:
                        if session.is_current_session == True:
                            unset = Session.objects.get(is_current_session=True)
                            unset.is_current_session = False
                            unset.save()
                    form.save()
                else:
                    form.save()
            else:
                form.save()
            messages.success(request, 'Session added successfully. ')
            return redirect('session_list')

    else:
        form = SessionForm()
    return render(request, 'app/session_update.html', {'form': form})


@login_required
@lecturer_required
def session_update_view(request, pk):
    session = Session.objects.get(pk=pk)
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        data = form.data.get('is_current_session')
        if data == 'true':
            sessions = Session.objects.all()
            if sessions:
                for session in sessions:
                    if session.is_current_session == True:
                        unset = Session.objects.get(is_current_session=True)
                        unset.is_current_session = False
                        unset.save()
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Session updated successfully. ')
                return redirect('session_list')
        else:
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                form.save()
                messages.success(request, 'Session updated successfully. ')
                return redirect('session_list')

    else:
        form = SessionForm(instance=session)
    return render(request, 'app/session_update.html', {'form': form})


@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)

    if session.is_current_session:
        messages.error(request, "You cannot delete current session")
        return redirect('session_list')
    else:
        session.delete()
        messages.success(request, "Session successfully deleted")
    return redirect('session_list')
# ########################################################


# ########################################################
# Semester
# ########################################################
@cache_page(60 * 40 )
@login_required
@lecturer_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by('-is_current_semester', '-semester')
    return render(request, 'app/semester_list.html', {"semesters": semesters, })


@login_required
@lecturer_required
def semester_add_view(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            data = form.data.get('is_current_semester')  # returns string of 'True' if the user selected Yes
            if data == 'True':
                semester = form.data.get('semester')
                ss = form.data.get('session')
                session = Session.objects.get(pk=ss)
                try:
                    if Semester.objects.get(semester=semester, session=ss):
                        messages.error(request, semester + " semester in " + session.session + " session already exist")
                        return redirect('add_semester')
                except:
                    semesters = Semester.objects.all()
                    sessions = Session.objects.all()
                    if semesters:
                        for semester in semesters:
                            if semester.is_current_semester == True:
                                unset_semester = Semester.objects.get(is_current_semester=True)
                                unset_semester.is_current_semester = False
                                unset_semester.save()
                        for session in sessions:
                            if session.is_current_session == True:
                                unset_session = Session.objects.get(is_current_session=True)
                                unset_session.is_current_session = False
                                unset_session.save()

                    new_session = request.POST.get('session')
                    set_session = Session.objects.get(pk=new_session)
                    set_session.is_current_session = True
                    set_session.save()
                    form.save()
                    messages.success(request, 'Semester added successfully.')
                    return redirect('semester_list')

            form.save()
            messages.success(request, 'Semester added successfully. ')
            return redirect('semester_list')
    else:
        form = SemesterForm()
    return render(request, 'app/semester_update.html', {'form': form})


from django.shortcuts import get_object_or_404

@login_required
@lecturer_required
def semester_update_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    
    if request.method == 'POST':
        is_current_semester = request.POST.get('is_current_semester') == 'True'
        
        if is_current_semester:
            # Unset the previously set current semester and session if any
            try:
                unset_semester = Semester.objects.get(is_current_semester=True)
                unset_semester.is_current_semester = False
                unset_semester.save()
            except Semester.DoesNotExist:
                pass
            
            try:
                unset_session = Session.objects.get(is_current_session=True)
                unset_session.is_current_session = False
                unset_session.save()
            except Session.DoesNotExist:
                pass
            
            new_session = request.POST.get('session')
            form = SemesterForm(request.POST, instance=semester)
            if form.is_valid():
                set_session = Session.objects.get(pk=new_session)
                set_session.is_current_session = True
                set_session.save()
                form.save()
                messages.success(request, 'Semester updated successfully!')
                return redirect('semester_list')
        else:
            form = SemesterForm(request.POST, instance=semester)
            if form.is_valid():
                form.save()
                return redirect('semester_list')
    else:
        form = SemesterForm(instance=semester)
    
    return render(request, 'app/semester_update.html', {'form': form})

@login_required
@lecturer_required
def semester_delete_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester:
        messages.error(request, "You cannot delete current semester")
        return redirect('semester_list')
    else:
        semester.delete()
        messages.success(request, "Semester successfully deleted")
    return redirect('semester_list')



from django.core.mail import mail_admins
import logging

logger = logging.getLogger(__name__)

def handler404(request, exception, template_name="common/404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response

def handler500(request, *args, **kwargs):
    response = render(request, 'common/500.html')
    response.status_code = 500
    return response

def handler400(request, exception, template_name="common/400.html"):
    response = render(request, template_name)
    response.status_code = 400

    # Send email notification for 400 error
    subject = f"Bad Request Error (400) on Kreeck Academy"
    message = f"Bad Request Error (400) occurred. Request URL: {request.path}\nUser Agent: {request.META.get('HTTP_USER_AGENT')}"
    mail_admins(subject, message)

    # Log the error
    logger.error(message)

    return response


@cache_page(60 * 40 )
@login_required
@admin_required
def dashboard_view(request):
    return render(request, 'app/dashboard.html')



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess

def execute_code(language, code):
    if language == 'python':
        command = ['python', '-c', code]
    elif language == 'html':
        command = ['echo', code]
    elif language == 'css':
        command = ['echo', code]
    elif language == 'javascript':
        command = ['node', '-e', code]
    elif language == 'cpp':
        # Save the C++ code to a temporary file
        with open('temp.cpp', 'w') as file:
            file.write(code)
        
        # Compile the C++ code
        compile_command = ['g++', 'temp.cpp', '-o', 'temp']
        compile_result = subprocess.run(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # If compilation is successful, execute the compiled binary
        if compile_result.returncode == 0:
            execution_command = ['./temp']
            execution_result = subprocess.run(execution_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return execution_result.stdout
        else:
            return compile_result.stderr

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        return result.stderr

def run_code_view(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        code = request.POST.get('code')
        try:
            output = execute_code(language, code)
            return JsonResponse({'output': output})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method.'})
