from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.mail import send_mass_mail
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from SMS.settings import DEBUG
from .forms import ProgramForm
from accounts.models import User, Student
from app.models import Session, Semester
from result.models import TakenCourse
from accounts.decorators import admin_required, lecturer_required, student_required
from .forms import (
    ProgramForm, CourseAddForm, CourseAllocationForm, 
    EditCourseAllocationForm, UploadFormFile, UploadFormVideo
)
from .models import Program, Course, CourseAllocation, Upload, UploadVideo
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
import os
from django.conf import settings
from django.core.files.storage import default_storage

# ########################################################
# Program views
# ########################################################
@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def program_view(request):
    programs = Program.objects.all()

    program_filter = request.GET.get('program_filter')
    if program_filter:
        programs = Program.objects.filter(title__icontains=program_filter)

    return render(request, 'course/program_list.html', {
        'title': "Programs | Kreeck Academy",
        'programs': programs,
    })


@login_required
@lecturer_required  # Assuming you have a custom decorator for lecturer access
def program_add(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()

            if DEBUG:
                pass
            else:
                send_mail(
                    subject="New Program Created at Kreeck Academy",
                    message=f"A new program '{program.title}' has been created. Check it out on our website",
                    from_email="dave@kreeck.com",
                    recipient_list=["kreeckinc@gmail.com"],
                )

            messages.success(request, program.title + ' program has been created.')
            return redirect('programs')
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = ProgramForm()

    return render(request, 'course/program_add.html', {
        'title': "Add Program | Kreeck Academy",
        'form': form,
    })

#this will cache the page for 15 minutes, 60 secs by 15.
@cache_page(60 * 60)
@login_required
def program_detail(request, pk):
    program = Program.objects.get(pk=pk)
    courses = Course.objects.filter(program_id=pk).order_by('-year')
    credits = Course.objects.aggregate(Sum('credit'))

    paginator = Paginator(courses, 10)
    page = request.GET.get('page')

    courses = paginator.get_page(page)

    return render(request, 'course/program_single.html', {
        'title': program.title,
        'program': program, 'courses': courses, 'credits': credits
    }, )


@login_required
@lecturer_required
def program_edit(request, pk):
    program = Program.objects.get(pk=pk)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, str(request.POST.get('title')) + ' program has been updated.')
            return redirect('programs')
    else:
        form = ProgramForm(instance=program)

    return render(request, 'course/program_add.html', {
        'title': "Edit Program | Kreeck Academy",
        'form': form
    })


@login_required
@lecturer_required
def program_delete(request, pk):
    program = Program.objects.get(pk=pk)
    title = program.title
    program.delete()
    messages.success(request, 'Program ' + title + ' has been deleted.')

    return redirect('programs')
# ########################################################

# ########################################################
# Course views
# #######################################################
# this will cache the page for 45 minutes because this page is the one that their are goig to be viewing the video
# on so it needs to be cached for a longer timeframe

#@cache_page(60 * 40 )
#@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@cache_page(60 * 10 )
@login_required
def course_single(request, slug):
    course = Course.objects.get(slug=slug)
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)

    # lecturers = User.objects.filter(allocated_lecturer__pk=course.id)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    return render(request, 'course/course_single.html', {
        'title': course.title,
        'course': course,
        'files': files,
        'videos': videos,
        'lecturers': lecturers,
        'media_url': settings.MEDIA_ROOT,
    }, )

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
#@lecturer_required
def course_add(request, pk):
    users = User.objects.all()
    if request.method == 'POST':
        form = CourseAddForm(request.POST)
        course_name = request.POST.get('title')
        course_code = request.POST.get('code')
        if form.is_valid():
            course = form.save()

            if DEBUG:
                pass
            else:
                send_mail(
                    subject="New Course Created at Kreeck Academy",
                    message=f"A new course '{course.title}' with code '{course.code}' has been created.",
                    from_email="dave@kreeck.com",
                    recipient_list=["kreeckinc@gmail.com"],
                )

            messages.success(request, (course_name + '(' + course_code + ')' + ' has been created.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = CourseAddForm(initial={'program': Program.objects.get(pk=pk)})

    return render(request, 'course/course_add.html', {
        'title': "Add Course | Kreeck Academy",
        'form': form, 'program': pk, 'users': users
    })


@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = CourseAddForm(request.POST, instance=course)
        course_name = request.POST.get('title')
        course_code = request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_name + '(' + course_code + ')' + ' has been updated.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = CourseAddForm(instance=course)

    return render(request, 'course/course_add.html', {
        'title': "Edit Course | Kreeck Academy",
        # 'form': form, 'program': pk, 'course': pk
        'form': form
    }, )

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required
def course_delete(request, slug):
    course = Course.objects.get(slug=slug)
    # course_name = course.title
    course.delete()
    messages.success(request, 'Course ' + course.title + ' has been deleted.')

    return redirect('program_detail', pk=course.program.id)
# ########################################################


# ########################################################
# Course Allocation
# ########################################################
@method_decorator([login_required], name='dispatch')
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/course_allocation_form.html'

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        lecturer = form.cleaned_data['lecturer']
        selected_courses = form.cleaned_data['courses']
        courses = [course.pk for course in selected_courses]

        # Check if the staff has been allocated a course before
        try:
            allocation = CourseAllocation.objects.get(lecturer=lecturer)
        except CourseAllocation.DoesNotExist:
            allocation = CourseAllocation.objects.create(lecturer=lecturer)

        for course in courses:
            allocation.courses.add(course)

        allocation.save()

        # Send email to the allocated staff
        course_names = [course.title for course in selected_courses]

        subject = "You have been allocated to a course"
        template = 'emails/lecture-allocation.html'
        context = {
            'lecturer': lecturer,
            'course_names': course_names,
        }

        message = render_to_string(template, context)

        if DEBUG:
            pass
        else:
            send_mail(subject, '', 'dave@kreeck.com', [lecturer.email], html_message=message)
        return redirect('course_allocation_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Assign Course | Kreeck Academy"
        return context
@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def course_allocation_view(request):
    allocated_courses = CourseAllocation.objects.all()
    return render(request, 'course/course_allocation_view.html', {
        'title': "Course Allocations | Kreeck Academy",
        "allocated_courses": allocated_courses
    })

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    allocated = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == 'POST':
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, 'course assigned has been updated.')
            return redirect('course_allocation_view')
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(request, 'course/course_allocation_form.html', {
        'title': "Edit Course Allocated | Kreeck Academy",
        'form': form, 'allocated': pk
    }, )

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required
def deallocate_course(request, pk):
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, 'successfully deallocate!')
    return redirect("course_allocation_view")
# ########################################################


# ########################################################
# File Upload views
# ########################################################

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            uploaded_file = form.save()

            # Send email to students taking the course
            students_emails = Student.objects.values_list('student__email', flat=True)
            file_title = uploaded_file.title
            subject = f"New File Uploaded for: {course.title}"
            template = 'emails/course-file-upload.html'
            context = {
                'course': course,
                'file_title': file_title,
            }

            message = render_to_string(template, context)

            if DEBUG:
                pass
            else:
                send_mail(subject, '', 'dave@kreeck.com', students_emails, html_message=message)

            messages.success(request, (file_title + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile()

    return render(request, 'upload/upload_file_form.html', {
        'title': "File Upload | Kreeck Academy",
        'form': form,
        'course': course
    })

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = Course.objects.get(slug=slug)
    instance = Upload.objects.get(pk=file_id)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        # file_name = request.POST.get('name')
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile(instance=instance)

    return render(request, 'upload/upload_file_form.html', {
        'title': instance.title,
        'form': form, 'course': course})

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def handle_file_delete(request, slug, file_id):
    file = Upload.objects.get(pk=file_id)
    
    # Get the file's path in the media storage
    file_path = file.file.path

    # Delete the file from the media storage
    if default_storage.exists(file_path):
        default_storage.delete(file_path)

    # Delete the database record
    file.delete()

    messages.success(request, (file.title + ' has been deleted.'))
    return redirect('course_detail', slug=slug)




# ########################################################
# Video Upload views
# ########################################################
@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@lecturer_required 
def handle_video_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            uploaded_video = form.save()

            # Send email to students taking the course
            students_emails = Student.objects.values_list('student__email', flat=True)
            video_title = uploaded_video.title
            subject = f"New Video Uploaded for Course: {course.title}"
            template = 'emails/course-video-upload.html'
            context = {
                'course': course,
                'video_title': video_title,
            }

            message = render_to_string(template, context)

            if DEBUG:
                pass
            else:
                send_mail(subject, '', 'dave@kreeck.com', students_emails, html_message=message)

            messages.success(request, (video_title + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo()

    return render(request, 'upload/upload_video_form.html', {
        'title': "Video Upload | Kreeck Academy",
        'form': form,
        'course': course
    })




from datetime import timedelta

@login_required
#@lecturer_required 
#@admin_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    videos = UploadVideo.objects.filter(course=course)
    files = Upload.objects.filter(course__slug=slug)

    total_duration = timedelta()
    for video in videos:
        if video.duration is not None:
            total_duration += video.duration

    return render(request, 'video/video_playback.html', {'video': video, 'videos': videos, 'total_duration': total_duration, 'files': files,})



@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = Course.objects.get(slug=slug)
    instance = UploadVideo.objects.get(slug=video_slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo(instance=instance)

    return render(request, 'upload/upload_video_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(UploadVideo, slug=video_slug)
    # video = UploadVideo.objects.get(slug=video_slug)
    video.delete()

    messages.success(request, (video.title + ' has been deleted.'))
    return redirect('course_detail', slug=slug)
# ########################################################


# ########################################################
# Course Registration
# ########################################################
@login_required
#@student_required
def course_registration(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            student = Student.objects.get(student__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.create(student=student, course=course)
            obj.save()
            messages.success(request, 'Courses Registered Successfully!')
        return redirect('course_registration')
    else:
        # student = Student.objects.get(student__pk=request.user.id)
        student = get_object_or_404(Student, student__id=request.user.id)
        taken_courses = TakenCourse.objects.filter(student__student__id=request.user.id)
        t = ()
        for i in taken_courses:
            t += (i.course.pk,)
        current_semester = Semester.objects.get(is_current_semester=True)

        courses = Course.objects.filter(program__pk=student.department.id, level=student.level, semester=current_semester
        ).exclude(id__in=t).order_by('year')
        all_courses = Course.objects.filter(level=student.level, program__pk=student.department.id)

        no_course_is_registered = False  # Check if no course is registered
        all_courses_are_registered = False

        registered_courses = Course.objects.filter(level=student.level).filter(id__in=t)
        if registered_courses.count() == 0:  # Check if number of registered courses is 0
            no_course_is_registered = True

        if registered_courses.count() == all_courses.count():
            all_courses_are_registered = True

        total_first_semester_credit = 0
        total_sec_semester_credit = 0
        total_registered_credit = 0
        for i in courses:
            if i.semester == "First":
                total_first_semester_credit += int(i.credit)
            if i.semester == "Second":
                total_sec_semester_credit += int(i.credit)
        for i in registered_courses:
            total_registered_credit += int(i.credit)
        context = {
            "is_calender_on": True,
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "current_semester": current_semester,
            "courses": courses,
            "total_first_semester_credit": total_first_semester_credit,
            "total_sec_semester_credit": total_sec_semester_credit,
            "registered_courses": registered_courses,
            "total_registered_credit": total_registered_credit,
            "student": student,
        }
        return render(request, 'course/course_registration.html', context)
    

@login_required
@student_required
def course_drop(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            student = Student.objects.get(student__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.get(student=student, course=course)
            obj.delete()

            subject = "Course Dropped"
            template = 'emails/student-course-drop.html'
            context = {
                'student': student,
                'course': course,
            }

            message = render_to_string(template, context)

            if DEBUG:
                pass
            else:
                send_mail(subject, '', 'dave@kreeck.com', [student.student.email], html_message=message)

            messages.success(request, 'Successfully Dropped!')

        return redirect('course_registration')

# ########################################################

@cache_page(60 * 40 )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def user_course_list(request):
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id)

        return render(request, 'course/user_course_list.html', {'courses': courses})

    elif request.user.is_student:
        student = Student.objects.get(student__pk=request.user.id)
        taken_courses = TakenCourse.objects.filter(student__student__id=student.student.id)
        courses = Course.objects.filter(level=student.level).filter(program__pk=student.department.id)

        return render(request, 'course/user_course_list.html', {
            'student': student,
            'taken_courses': taken_courses,
            'courses': courses
        })

    else:
        return render(request, 'course/user_course_list.html')
