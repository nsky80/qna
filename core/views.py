from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from core.forms import RegisterForm
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import FormView
from core.models import User
from ques_ans.models import Questions, Answers, QuestionGroups
from core.forms import LoginForm, RegisterForm
from django.contrib import messages

class DashboardView(FormView):
    def get(self, request):
        content = {}
        if request.user.is_authenticated:
            user = request.user
            # Specifying authentication backends
            user.backend = 'django.contrib.core.backends.ModelBackend'
            ques_obj = Questions.objects.filter(user=user)
            content['userdetail'] = user
            content['questions'] = ques_obj
            # ans_obj = Answers.objects.filter(question=ques_obj[0])
            # content['answers'] = ans_obj
            return render(request, 'core/dashboard.html', content)
        else:
            return redirect(reverse('core:login-view'))


class LoginView(FormView):

    content = {}
    content['form'] = AuthenticationForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        content = {}
        if request.user.is_authenticated:
            return redirect(reverse('core:dashboard-view'))
        content['form'] = AuthenticationForm
        return render(request, 'core/login.html', content)

    def post(self, request):
        content = {}
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse("core:dashboard-view"))
            else:
                raise Exception("Invalid Credentials!")
        except Exception as e:
            content = {}
            content['form'] = AuthenticationForm
            messages.error(request, e)
            print(e)
            return render(request, 'core/login.html', content)


class LogoutView(FormView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/core/login')


class RegisterView(FormView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        content = {}
        content['form'] = RegisterForm
        return render(request, 'core/register.html', content)

    def post(self, request):
        content = {}
        form = RegisterForm(request.POST, request.FILES or None)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect(reverse('core:dashboard-view'))
        content['form'] = form
        template = 'core/register.html'
        return render(request, template, content)
