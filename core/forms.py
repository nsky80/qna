from django import forms
from django.contrib.auth.forms import AuthenticationForm
from core.models import User
from ques_ans.models import Questions, Answers
from tinymce.widgets import TinyMCE

# TinyMCE editer for writing new content used both end User and Admin
class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'hi',
        }
))


class AskQuestionForm(forms.ModelForm):
    question_description = forms.CharField(label="Question Description", 
        widget=TinyMCEWidget(
            attrs={'required': True, 'cols': 40, 'rows': 10}
        )
    )
    class Meta:
        model = Questions
        fields = ['title', 'question_description', 'tags']


class WriteAnswerForm(forms.ModelForm):
    answer_text = forms.CharField(label="Main Content", 
        widget=TinyMCEWidget(
            attrs={'required': True, 'cols': 40, 'rows': 10}
        )
    )

    class Meta:
        model = Answers
        fields = ['answer_text', 'is_anonymous']