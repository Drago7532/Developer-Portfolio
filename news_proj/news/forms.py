from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Publisher, Newsletter

# Article form
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher']

# Signup form
ROLE_CHOICES = (
    ('reader', 'Reader'),
    ('journalist', 'Journalist'),
)

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role',)

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('Journalist', 'Journalist'),
        ('Editor', 'Editor'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'role', )