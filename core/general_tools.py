from ques_ans.models import Questions, Answers, Activity
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from taggit.models import Tag


# Here obj is list of content which is used to convert into pages
def create_page_object(request, obj, no_of_obj, serial):
    page = request.GET.get('page' + str(serial))

    paginator = Paginator(obj, no_of_obj)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj
