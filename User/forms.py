from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    ACCOUNT_TYPES = [
        ('Manager', 'Manager'),
        ('Organizer', 'Organizer'),
        ('Exhibitor', 'Exhibitor'),
    ]

    email = forms.EmailField(required=True)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "account_type")

    def clean_email(self):
        # 获取表单中的email字段
        email = self.cleaned_data.get('email')
        # 检查数据库中是否已经存在该邮箱
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if not User.objects.filter(username=username).exists():
            self.add_error('username', 'User does not exist.')
            raise ValidationError("User does not exist.")
        user = User.objects.get(username=username)
        if not user.check_password(password):
            self.add_error('password', 'Incorrect password.')
            raise ValidationError("Incorrect password.")
        return cleaned_data


class ReplyMessageForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'id': 'messageTitle'}), max_length=100)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'id': 'messageContent'}), max_length=1000)

    def clean(self):
        cleaned_data = super(ReplyMessageForm, self).clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        if not title:
            self.add_error('title', 'Title cannot be empty.')
            raise ValidationError("Title cannot be empty.")
        if not content:
            self.add_error('content', 'Content cannot be empty.')
            raise ValidationError("Content cannot be empty.")
        return cleaned_data
