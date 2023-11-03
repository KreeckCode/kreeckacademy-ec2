from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BlogForm
from .models import Blog, Category, Message

@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog:blog_list')
    else:
        form = BlogForm()
    return render(request, 'blog/create_blog.html', {'form': form})

def blog_list(request):
    blog = Blog.objects.all()
    category = Category.objects.all()
    message = Message.objects.all()
    recent_blogs = Blog.objects.order_by('-timestamp')[:5]


    context = {
        'blog':blog,
        'category':category,
        'message':message,
        'recent_blogs': recent_blogs,

    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    return render(request, 'blog/blog_detail.html', {'blog': blog})
