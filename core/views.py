from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404, Http404
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
from ques_ans.models import Questions, Answers, Activity #, Vote
from core.forms import LoginForm, RegisterForm, AskQuestionForm, WriteAnswerForm
from django.contrib import messages
from django.core.paginator import Paginator
from taggit.models import Tag
from core.general_tools import create_page_object
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class WriteAnswerView(FormView):
    content = {}
    # conten
    content['form'] = WriteAnswerForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WriteAnswerView, self).dispatch(request, *args, **kwargs)

    def get(self, request, question_id, question_slug):
        question = Questions.objects.get(pk=question_id)
        if request.user.is_authenticated:
            # It counts the number of views to question
            if question.user != request.user:
                question.views += 1
                question.save()
        self.content["question"] = question
        return render(request, 'core/write_answer.html', self.content)

    def post(self, request, question_id, question_slug):

        form = WriteAnswerForm(request.POST, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.question = Questions.objects.get(pk=question_id)
            obj.save()
            messages.success(request, "Answer Posted Successfully!")
            return redirect(request.path)

        template = 'core/write_answer.html'
        return render(request, template, self.content)

class IndexView(View):
    content = {}
    def get(self, request):
        questions_list = Questions.objects.order_by("-created_on")
        self.content["page_title"] = "Recently Asked Questions"
        self.content["questions"] = create_page_object(request, questions_list, 10, 1)
        return render(request, 'core/index.html', self.content)

class DashboardView(FormView):
    def get(self, request):
        content = {}
        if request.user.is_authenticated:
            user = request.user
            # Specifying authentication backends
            user.backend = 'django.contrib.core.backends.ModelBackend'
            # content['userdetail'] = user
            questions_list = Questions.objects.filter(user=user).order_by("-created_on")
            # List where current user has answered
            answers_list = Questions.objects.filter(pk__in=Answers.objects.filter(user=user).values_list("question", flat=True))
            # Users bookmarked Questions
            # Here in below 2 lines we are trying to access all the objects from generic key
            ct = ContentType.objects.get_for_model(Questions)
            bookmarks_list = Questions.objects.filter(pk__in=Activity.objects.filter(content_type=ct, user=user, activity_type="F").values_list("object_id", flat=True))
            content["questions"] = create_page_object(request, questions_list, 4, 1)
            content["answers"] = create_page_object(request, answers_list, 4, 2)
            content["bookmarks"] = create_page_object(request, bookmarks_list, 4, 3)
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
                messages.success(request, "Logged in as " + str(username))
                next_url = request.GET.get('next')
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return redirect("/dashboard/")
            else:
                raise Exception("Invalid Credentials!")
        except Exception as e:
            content = {}
            content['form'] = AuthenticationForm
            messages.error(request, e)
            # print(e)
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
    content["common_tags"] = Questions.tags.most_common()[:10]

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

# if user click any tag then this view called
def tagged(request, slug):
    content = {}
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Questions.tags.most_common()[:4]
    # question = Questions.objects.filter(tags=tag)
    questions_list = Questions.objects.filter(tags=tag).order_by("-created_on")
    content["page_title"] = "Tag: " + str(slug)
    content["questions"] = create_page_object(request, questions_list, 10, 1)
    return render(request, 'core/index.html', content)


# This open all the available tags
def tags(request):
    content = {}
    content["tags"] = Tag.objects.all()
    return render(request, "core/tags.html", content)


# Here object_type stands for whether it is a question object or answer object
# It also support voting of a answer as well
def question_vote(request, object_type, question_id, vote_type):
    if request.user.is_authenticated:
        if object_type == "question":
            question = Questions.objects.get(pk=question_id)
        elif object_type == "answer":
            question = Answers.objects.get(pk=question_id)
        else:
            raise Http404
        user = request.user

        # first check whether it is voting or it is bookmarking a question by a user
        if vote_type == "up" or vote_type == "down":
            act = question.activities.filter(user=user, activity_type = Activity.UP_VOTE) or question.activities.filter(user=user, activity_type = Activity.DOWN_VOTE)
            # if already upvoted then do operation on that i.e. no need for creating new object
            # if earlier vote had upvote and again upvote coming then delete the object because
            # user wanted to undo the operation
            if act:
                obj = act[0]
                if vote_type == "up":
                    # it means user earlier upvoted this question but now he wants to undo that opr
                    if obj.activity_type == Activity.UP_VOTE:
                        obj.delete()
                    else:
                        obj.activity_type = Activity.UP_VOTE
                        obj.save()
                        messages.success(request, "Upvoted Successfully!")
                else:
                    if obj.activity_type == Activity.DOWN_VOTE:
                        obj.delete()
                    else:
                        obj.activity_type = Activity.DOWN_VOTE
                        obj.save()
                        messages.success(request, "Downvoted Successfully!")
            # it means object doesn't exist as of now, need to create new table with vote
            else:
                if vote_type == "up":
                    Activity.objects.create(content_object=question, activity_type=Activity.UP_VOTE, user=request.user)
                    messages.success(request, "Upvoted Successfully!")
                # now it must be down vote
                else:
                    Activity.objects.create(content_object=question, activity_type=Activity.DOWN_VOTE, user=request.user)
                    messages.success(request, "Downvoted Successfully!")

        # Here we are handling with bookmarking of question by perticular user
        else:
            act = question.activities.filter(user=user, activity_type = Activity.FAVORITE)
            if act:
                obj = act[0]
                obj.delete()
            else:
                Activity.objects.create(content_object=question, activity_type=Activity.FAVORITE, user=request.user)
                messages.success(request, "Bookmarked/Saved Successfully!")

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)
        else:
            return redirect("/")
    raise Http404


# It will handle for editing question
def edit_question(request, question_id):
    if request.user.is_authenticated:
        obj = Questions.objects.get(pk=question_id)

        if request.method == "POST":
            form = AskQuestionForm(request.POST, instance=obj)

            if form.is_valid():
                try:
                    # edited_obj = form.save(commit=False)
                    # edited_obj.updated_on = timezone.now
                    # edited_obj.save()
                    edited_obj = form.save()
                    edited_obj.updated_on = timezone.now()
                    edited_obj.save()
                    messages.success(request, "Edited Successfully!")
                    next = "/questions/%d/%s/"%(obj.id, obj.slug)
                    return redirect(next)
                except Exception as ex:
                    messages.error(request, f"Please Feedback error {ex}")
        else:
            form = AskQuestionForm(instance=obj)
            args = {'form': form}
            return render(request=request,
                            template_name="core/ask_question.html",
                            context=args)
    else:
        return HttpResponseNotFound()         


def trending(request):
    return HttpResponse("Algorithm is in development!")