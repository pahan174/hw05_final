from django.shortcuts import redirect, render
from .models import Follow, Post, Group, User, Comment
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


POSTS_PER_PAGE = 10


def index(request):

    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    cnt_posts = posts.count()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author) or None
    else:
        following = None

    context = {
        'cnt_posts': cnt_posts,
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=get_object_or_404(Post, id=post_id))
    posts_author = Post.objects.filter(author=post.author)
    cnt_posts = posts_author.count()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'cnt_posts': cnt_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user

        post.save()

        return redirect('posts:profile', username=request.user)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post or None)
        if form.is_valid():
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id=post_id)
        else:
            context = {
                'form': form,
                'is_edit': True,
            }
        return render(request, 'posts/create_post.html', context)
    else:
        return redirect('login')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''Отображение постов подписанных авторов '''
    title = 'Новые посты ваших авторов'
    follow_author = Follow.objects.filter(user=request.user).values_list(
        'author_id',
        flat=True
    )
    posts = Post.objects.filter(author_id__in=follow_author)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    '''Подписаться на автора'''
    author = get_object_or_404(User, username=username)
    if request.user != author:
        created_object = Follow.objects.get_or_create(
            user=get_object_or_404(User, username=request.user),
            author=get_object_or_404(User, username=username)
        )
        print(created_object)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    '''Дизлайк, отписка'''
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
