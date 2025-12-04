from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import get_user_model, logout
from .forms import SignUpForm, ArticleForm, NewsletterForm
from django.contrib.auth import login
from .models import CustomUser, Publisher, Article, Newsletter
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.http import JsonResponse

User = get_user_model()

def assign_role(user, role):
    user.role = role
    user.save()  # save role first

    if role == 'journalist':
        # Journalists shouldn't have reader fields
        user.subscribed_publishers.clear()
        user.subscribed_journalists.clear()

        publisher = Publisher.objects.first()
        if publisher:
            publisher.journalists.add(user)

    elif role == 'reader':
        # Readers shouldn't have journalist fields
        user.published_articles.clear()
        user.published_newsletters.clear()

    # Add user to the correct group
    group = Group.objects.get(name=role.capitalize())
    user.groups.add(group)
    user.save()


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.role == 'editor':
        # Only show content for THIS editor’s publisher
        publisher = user.editor_publisher.first()

        if publisher:
            context['pending_articles'] = Article.objects.filter(
                publisher=publisher,
                approved_by_editor=False
            )
            context['pending_newsletters'] = Newsletter.objects.filter(
                publisher=publisher,
                approved_by_editor=False
            )
            context['publisher'] = publisher
        else:
            context['pending_articles'] = []
            context['pending_newsletters'] = []
            context['publisher'] = None

    elif user.role == 'journalist':
        # Journalist sees their own content
        context['my_articles'] = Article.objects.filter(author=user)
        context['my_newsletters'] = Newsletter.objects.filter(author=user)

        # Show assigned publisher + editors
        publisher = user.publishers_journalists.first()
        context['publisher'] = publisher

    elif user.role == 'reader':
        # Reader sees only approved content
        context['articles'] = Article.objects.filter(approved_by_editor=True)
        context['newsletters'] = Newsletter.objects.filter(approved_by_editor=True)

    return render(request, 'news/dashboard.html', context)


def public_articles(request):
    articles = Article.objects.filter(approved_by_editor=True)

    newsletters = Newsletter.objects.filter(
        approved_by_editor=True
    )

    return render(request, "news/home.html", {
        "articles": articles,
        "newsletters": newsletters,
    })


def all_newsletters(request):
    newsletters = Newsletter.objects.filter(approved_by_editor=True)
    return render(request, 'news/all_newsletters.html', {'newsletters': newsletters})

def all_articles(request):
    articles = Article.objects.filter(approved_by_editor=True)
    return render(request, 'news/all_articles.html', {"articles": articles})



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.save()

            role = form.cleaned_data['role']
            assign_role(new_user, role)

            # Assign journalist to a publisher
            if role == "journalist":
                publisher = Publisher.objects.first()
                if publisher:
                    publisher.journalists.add(new_user)

            login(request, new_user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'news/signup.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('news:public_articles')

# Article Detail
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    # Only allow readers to see approved articles
    if request.user.is_authenticated and request.user.role == 'reader' and not article.approved_by_editor:
        return redirect('news:home')
    if not request.user.is_authenticated and not article.approved_by_editor:
        return redirect('news:home')
    return render(request, 'news/article_detail.html', {'article': article})


# Editor: Helper Function
def is_editor(user):
    return user.groups.filter(name='Editor').exists() or user.role == 'editor'

# Editor: Review List
@login_required
@user_passes_test(is_editor, login_url='home')
def article_review_list(request):
    articles = Article.objects.filter(approved_by_editor=False)
    return render(request, 'news/editor/article_review_list.html', {
        'articles': articles
    })

# Editor: Approve Article
@login_required
@user_passes_test(is_editor, login_url='home')
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        article.approved_by_editor = True
        article.save()

        return redirect('news:article_review_list')

    return render(request, 'news/editor/approve_article.html', {
        'article': article
    })

def view_newsletter_public(request, newsletter_id):
    # Only show newsletters that are approved and published
    newsletter = get_object_or_404(
        Newsletter,
        id=newsletter_id,
        approved_by_editor=True
    )
    return render(request, 'news/view_newsletter.html', {'newsletter': newsletter})


@login_required
@user_passes_test(is_editor, login_url='home')
def newsletter_review_list(request):
    newsletters = Newsletter.objects.filter(approved_by_editor=False)
    return render(request, 'news/editor/newsletter_review_list.html', {'newsletters': newsletters})

@login_required
@user_passes_test(is_editor, login_url='home')
def approve_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.method == "POST":
        newsletter.approved_by_editor = True
        newsletter.save()
        return redirect('news:newsletter_review_list')

    return render(request, 'news/editor/approve_newsletter.html', {'newsletter': newsletter})


def is_journalist(user):
    return user.role == 'journalist'

# Journalist: Create Article
@login_required
@user_passes_test(is_journalist, login_url='home')
def create_article(request):
    # Assign publisher automatically based on the journalist's publisher
    publisher = request.user.publishers_journalists.first()

    if not publisher:
        return HttpResponse(
            "You are not assigned to any publisher",
            status=403
        )

    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        article = Article.objects.create(
            title=title,
            content=content,
            author=request.user,
            publisher=publisher,
            approved_by_editor=False
        )
        return redirect('news:dashboard')

    return render(request, 'news/journalist/create_article.html')

@login_required
@user_passes_test(is_journalist, login_url='home')
def create_newsletter(request):

    # Assign publisher automatically based on the journalist's publisher
    publisher = request.user.publishers_journalists.first()

    if not publisher:
        return HttpResponse(
            "You are not assigned to any publisher",
            status=403
        )

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        newsletter = Newsletter.objects.create(
            title=title,
            content=content,
            author=request.user,
            publisher=publisher,
            approved_by_editor=False
        )

        return redirect('news:dashboard')

    return render(request, 'news/journalist/create_newsletter.html')

@login_required
@user_passes_test(is_journalist)
def view_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)
    return render(request, 'news/journalist/view_article.html', {'article': article})


@login_required
@user_passes_test(is_journalist)
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('news:my_articles')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'news/journalist/edit_article.html', {'form': form})

@login_required
@user_passes_test(is_journalist)
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)

    if request.method == "POST":
        article.delete()
        return redirect('news:my_articles')

    return render(request, 'news/journalist/delete_article.html', {'article': article})

@login_required
def my_articles(request):
    user = request.user
    articles = Article.objects.filter(author=user)
    return render(request, 'news/journalist/my_articles.html', {'items': articles, 'page_type': 'Articles'})

@login_required
def my_newsletters(request):
    user = request.user
    newsletters = Newsletter.objects.filter(author=user)
    return render(request, 'news/journalist/my_newsletters.html', {'items': newsletters, 'page_type': 'Newsletters'})


@user_passes_test(is_journalist)
def view_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)
    return render(request, 'news/journalist/view_newsletter.html', {
        'newsletter': newsletter
    })


@login_required
@user_passes_test(is_journalist)
def edit_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            return redirect('news:my_newsletters')
    else:
        form = NewsletterForm(instance=newsletter)

    return render(request, 'news/journalist/edit_newsletter.html', {
        'form': form,
        'newsletter': newsletter
    })


@login_required
@user_passes_test(is_journalist)
def delete_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)

    if request.method == "POST":
        newsletter.delete()
        return redirect('news:my_newsletters')

    return render(request, 'news/journalist/delete_newsletter.html', {
        'newsletter': newsletter
    })

# ==============
# Subscriptions
# ==============

@login_required
def all_publishers(request):
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role='journalist')
    return render(request, 'news/all_publishers.html', {
        'publishers': publishers,
        'journalists': journalists,
    })


@login_required
def subscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    request.user.subscribed_publishers.add(publisher)
    return redirect('news:all_publishers')


@login_required
def unsubscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    request.user.subscribed_publishers.remove(publisher)
    return redirect('news:all_publishers')


@login_required
def subscribe_journalist(request, journalist_id):
    journalist = get_object_or_404(CustomUser, id=journalist_id, role='journalist')
    request.user.subscribed_journalists.add(journalist)
    return redirect('news:all_publishers')


@login_required
def unsubscribe_journalist(request, journalist_id):
    journalist = get_object_or_404(CustomUser, id=journalist_id, role='journalist')
    request.user.subscribed_journalists.remove(journalist)
    return redirect('news:all_publishers')

@login_required
def subscription_feed(request):
    # Get all approved articles from subscribed publishers and journalists
    articles = Article.objects.filter(
        approved_by_editor=True,
        publisher__in=request.user.subscribed_publishers.all()
    ) | Article.objects.filter(
        approved_by_editor=True,
        author__in=request.user.subscribed_journalists.all()
    )

    # Order by most recent
    articles = articles.order_by('-created_at')

    # Pagination (5 articles per page)
    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/subscriptions.html', {
        'page_obj': page_obj
    })

# For auto testing
@login_required
def subscription_feed_api(request):
    user = request.user
    articles = Article.objects.filter(
        approved_by_editor=True,
        publisher__in=user.subscribed_publishers.all()
    ) | Article.objects.filter(
        approved_by_editor=True,
        author__in=user.subscribed_journalists.all()
    )
    data = [{"id": a.id, "title": a.title, "content": a.content} for a in articles]
    return JsonResponse(data, safe=False)



def home(request):
    publisher = None
    limit = 3  # Number of items to show on the homepage

    if request.user.is_authenticated:
        user = request.user

        if user.role == 'editor':
            articles = Article.objects.filter(approved_by_editor=True).order_by('-created_at')[:limit]
            newsletters = Newsletter.objects.filter(approved_by_editor=True).order_by('-created_at')[:limit]

        elif user.role == 'journalist':
            publisher = user.publishers_journalists.first()
            articles = Article.objects.filter(author=user).order_by('-created_at')[:limit]
            newsletters = Newsletter.objects.filter(author=user).order_by('-created_at')[:limit]

        else:  # readers
            articles = Article.objects.filter(approved_by_editor=True).order_by('-created_at')[:limit]
            newsletters = Newsletter.objects.filter(approved_by_editor=True).order_by('-created_at')[:limit]

    else:
        articles = Article.objects.filter(approved_by_editor=True).order_by('-created_at')[:limit]
        newsletters = Newsletter.objects.filter(approved_by_editor=True).order_by('-created_at')[:limit]

    return render(request, 'news/home.html', {
        'articles': articles,
        'newsletters': newsletters,
        'publisher': publisher
    })



