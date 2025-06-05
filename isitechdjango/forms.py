from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Article, Comment, Categorie, UserProfile, Tag

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Category name')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Category description')}),
            'couleur': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'categorie', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Article title')}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Article content')}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['nom', 'email', 'contenu']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Your Name')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Your Email')}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Your comment')}),
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='user'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Choose a username')})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Enter your email address')})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Create a password')})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Confirm your password')})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create or update user profile with selected role
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.save()
        return user

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Enter your username')})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Enter your password')})

class AdvancedSearchForm(forms.Form):
    """Advanced search form with multiple criteria"""
    SORT_CHOICES = [
        ('relevance', _('Relevance')),
        ('recent', _('Most Recent')),
        ('popular', _('Most Popular')),
        ('alphabetic', _('Alphabetical')),
    ]
    
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search articles, titles, content...'),
            'id': 'search-input',
            'autocomplete': 'off'
        })
    )
    
    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'category-filter'
        })
    )
    
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(articles__isnull=False).distinct(),
        required=False,
        empty_label=_("All Authors"),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'author-filter'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'date-from'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'date-to'
        })
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='relevance',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'sort-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update author queryset to only include authors with published articles
        self.fields['author'].queryset = User.objects.filter(
            articles__statut='published'
        ).distinct().order_by('username')
        
        # Update tags queryset to only include tags with articles
        self.fields['tags'].queryset = Tag.objects.filter(
            articles__statut='published'
        ).distinct().order_by('nom')