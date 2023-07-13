from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from .form import PostForm
from .models import Category, Post, User


INDEX_POST_NUM = 5


def index(request):
    post_list = (Post.objects.select_related('category')
                 .filter(is_published=True,
                 pub_date__lte=timezone.now(),
                 category__is_published=True)[:INDEX_POST_NUM])
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post,
                                 author__username=request.user,
                                 id=post_id)
        user = User.objects.get(username=request.user)
    else:
        user = None
        post = get_object_or_404(Post,
                                 is_published=True,
                                 category__is_published=True,
                                 pub_date__lte=timezone.now(),
                                 id=post_id)
    return render(request, 'blog/detail.html', {'post': post, 'user': user})


def category_posts(request, slug):
    category = get_object_or_404(Category,
                                 is_published=True,
                                 slug=slug)
    post_list = (Post.objects.select_related('category')
                 .filter(is_published=True,
                         pub_date__lte=timezone.now(),
                         category=category))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('category', 'author').filter(author__username=username)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.save()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_profile(request):
    instance = User.objects.get(username=request.user)
    form = UserChangeForm(request.POST or None, instance=instance)
    print(form)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', {'form': form})
