from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from core.forms import RegisterForm
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import FormView
from django.views import View
from core.models import User
from ques_ans.models import Questions, Answers
from core.forms import LoginForm, RegisterForm, AskQuestionForm, WriteAnswerForm
from django.contrib import messages
from django.core.paginator import Paginator
from taggit.models import Tag


class WriteAnswerView(FormView):
    content = {}
    # conten
    content['form'] = WriteAnswerForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WriteAnswerView, self).dispatch(request, *args, **kwargs)

    def get(self, request, question_id, question_slug):
        if request.user.is_authenticated:
            question = Questions.objects.get(pk=question_id)
            # It counts the number of views to question
            if question.user != request.user:
                question.views += 1
                question.save()
            self.content["question"] = question
            return render(request, 'core/write_answer.html', self.content)
        else:
            messages.info(request, "Login Required!")
            return redirect(reverse("core:login-view"))

    def post(self, request, question_id, question_slug):

        form = WriteAnswerForm(request.POST, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.question = Questions.objects.get(pk=question_id)
            obj.save()
            messages.success(request, "Answer Posted Successfully!")
            return redirect(reverse('core:dashboard-view'))

        template = 'core/write_answer.html'
        return render(request, template, self.content)

class IndexView(View):
    content = {}
    def get(self, request):
        questions_list = Questions.objects.order_by("-created_on")
        page = request.GET.get('page', 1)

        paginator = Paginator(questions_list, 10)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        self.content["page_obj"] = page_obj
        return render(request, 'core/index.html', self.content)

class DashboardView(FormView):
    def get(self, request):
        content = {}
        if request.user.is_authenticated:
            user = request.user
            # Specifying authentication backends
            user.backend = 'django.contrib.core.backends.ModelBackend'
            content['userdetail'] = user
            questions_list = Questions.objects.filter(user=user).order_by("-created_on")
            page = request.GET.get('page', 1)

            paginator = Paginator(questions_list, 5)
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            content["page_obj"] = page_obj
            return render(request, 'core/dashboard.html', content)
        else:
            messages.info(request, "Login Required!")
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
        return HttpResponseRedirect('/login')


class RegisterView(FormView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("core:dashboard-view"))
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


class AskQuestionView(FormView):
    content = {}
    content['form'] = AskQuestionForm
    content["common_tags"] = Questions.tags.most_common()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AskQuestionView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'core/ask_question.html', self.content)
        else:
            messages.info(request, "Login Required!")
            return redirect(reverse("core:login-view"))

    def post(self, request):

        form = AskQuestionForm(request.POST, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            # without this next line the tags won't be saved
            form.save_m2m()

            messages.success(request, "Question Posted Successfully!")
            return redirect(reverse('core:dashboard-view'))

        template = 'core/ask_question.html'
        return render(request, template, self.content)

def tagged(request, slug):
    content = {}
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Questions.tags.most_common()[:4]
    # question = Questions.objects.filter(tags=tag)

    questions_list = Questions.objects.filter(tags=tag).order_by("-created_on")
    page = request.GET.get('page', 1)
    paginator = Paginator(questions_list, 10)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    content["page_obj"] = page_obj
    return render(request, 'core/index.html', content)
