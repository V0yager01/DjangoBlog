from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone


from .form import PostForm, CommentForm
from .models import Category, Post, User, Comment

PAGINATOR_NUM = 10


def index(request):
    post_list = (Post.objects.select_related('category', 'author', 'location')
                 .filter(is_published=True,
                 pub_date__lte=timezone.now(),
                 category__is_published=True)
                 .annotate(comment_count=Count('comment'))
                 .order_by('-pub_date')
                 )
    paginator = Paginator(post_list, PAGINATOR_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post__id=post_id)
        if post.is_published:
            return render(request, 'blog/detail.html',
                          {'post': post, 'user': user,
                           'comments': comments,
                           'form': form})
        elif request.user == post.author:
            return render(request, 'blog/detail.html',
                          {'post': post, 'user': user,
                           'comments': comments,
                           'form': form})
        raise Http404
    post = get_object_or_404(Post, id=post_id, is_published=True)
    comments = Comment.objects.filter(post__id=post_id)
    return render(request, 'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})


def category_posts(request, slug):
    category = get_object_or_404(Category,
                                 is_published=True,
                                 slug=slug)
    post_list = (Post.objects.select_related('category', 'author', 'location')
                 .filter(is_published=True,
                         pub_date__lte=timezone.now(),
                         category=category))
    paginator = Paginator(post_list, PAGINATOR_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = (Post.objects.select_related('category', 'author', 'location')
                 .filter(author__username=username)
                 .annotate(comment_count=Count('comment'))
                 .order_by('-pub_date'))
    paginator = Paginator(post_list, PAGINATOR_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required(login_url='/auth/login/')
def create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    return render(request, 'blog/create.html', {'form': form})


@login_required(login_url='/auth/login/')
def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = UserChangeForm(request.POST or None,
                          request.FILES or None,
                          instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', {'form': form})


@login_required(login_url='/auth/login/')
def edit_post(request, post_id):
    instance = get_object_or_404(Post, id=post_id)
    if not instance.author == request.user:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None,
                    request.FILES or None,
                    instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required(login_url='/auth/login/')
def delete_post(request, post_id):
    instance = get_object_or_404(Post, author=request.user, id=post_id)
    user = User.objects.get(username=request.user)
    form = PostForm(request.POST or None,
                    instance=instance)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', request.user)
    return render(request, 'blog/create.html', {'form': form, 'user': user})


@login_required(login_url='/auth/login/')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required(login_url='/auth/login/')
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user == instance.author:
        form = CommentForm(request.POST or None, instance=instance)
        if request.method == "POST" and form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
        return render(request, 'blog/create.html', {'form': form})
    return redirect('blog:post_detail', post_id)


@login_required(login_url='/auth/login/')
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id, post__id=post_id,
                                 author=request.user)
    user = User.objects.get(username=request.user)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html', {'user': user})
