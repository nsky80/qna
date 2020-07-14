from django.contrib import admin
from ques_ans.models import Questions, Answers, Activity #, Vote
from tinymce.widgets import TinyMCE
from django.db import models

class AnswerInline(admin.TabularInline):
    model = Answers


class AnswerOverride(admin.ModelAdmin):   
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
        }


class QuestionsAdmin(admin.ModelAdmin):

    inlines = [AnswerInline]
    class Meta:
        model = Questions



admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers, AnswerOverride)
admin.site.register(Activity)
