from django import template
# from ques_ans.models import Vote
from ques_ans.models import Questions, Answers, Activity

register = template.Library()


# checking whether user upvoted or downvoted or nothing
@register.simple_tag
def has_voted(user, question, loc): #, question):
    if loc == 1:
        obj = question.activities.filter(user=user, activity_type=Activity.UP_VOTE)
    elif loc == 2:
        obj = question.activities.filter(user=user, activity_type=Activity.DOWN_VOTE)
    else:
        obj = question.activities.filter(user=user, activity_type=Activity.FAVORITE)

    # Here if object exist then it returns a list in which first element is intended object
    if loc == 3:
        param = "bookmark_border"
    else:
        param = "grey"
    if obj:
        # means object exist and need to taken care
        new_obj = obj[0]
        # print(new_obj.activity_type, loc)
        if loc == 1 and new_obj.activity_type == "U":
            param = "green"
        elif loc == 2 and new_obj.activity_type == Activity.DOWN_VOTE:
            param = "red"
        elif loc == 3 and new_obj.activity_type == "F":
            param = "bookmark"
        else:
            param = "grey"
    return param


@register.simple_tag
def has_an_answer(question):
    if question.answers_set.all():
        return "green"
    else:
        return "yellow"


@register.simple_tag
def bookmarks(ques_obj):
    return len(ques_obj.activities.filter(activity_type=Activity.FAVORITE))


@register.simple_tag
def upvotes(ques_obj):
    return len(ques_obj.activities.filter(activity_type=Activity.UP_VOTE))


@register.simple_tag
def downvotes(ques_obj):
    return len(ques_obj.activities.filter(activity_type=Activity.DOWN_VOTE))


@register.simple_tag
def my_tag(a, b, *args, **kwargs):
    warning = kwargs['warning']
    profile = kwargs['profile']
    # print(a, b, warning, profile.username)
    return "Hi"