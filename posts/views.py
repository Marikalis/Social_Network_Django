from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import User, Follow, Group, Post
from .settings import PAGE_SIZE


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not form.is_valid():
        return render(request, 'new_post.html', {
            'form': form,
            'edit': False
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_following = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'is_following': is_following
    })


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post,
        author__username=username,
        id=post_id
    )
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    following = Follow.objects.filter(
        author=post.author.id,
        user=request.user.id
    )
    followers = post.author.following.count()
    follow = post.author.follower.count()
    context = {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments,
        'following': following,
        'followers': followers,
        'follow': follow
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'new_post.html', {
            'form': form,
            'edit': True
        })

    form.save()
    return redirect('post', username, post_id)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {
        "path": request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    username = request.user
    post = Post.objects.filter(author__following__user=username)
    paginator = Paginator(post, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html", {'page': page}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    subscription = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if author != request.user and subscription is False:
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('profile', username=username)
