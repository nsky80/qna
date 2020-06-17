from django.contrib import admin
from ques_ans.models import QuestionGroups, Questions, Answers

# admin.site.register(QuestionGroups)
# admin.site.register(Questions)

class AnswerInline(admin.TabularInline):
    model = Answers

class QuestionInline(admin.TabularInline):
    model = Questions

class QuestionsAdmin(admin.ModelAdmin):

    inlines = [AnswerInline]
    class Meta:
        model = Questions


class QuestionGroupsAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    class Meta:
        model = QuestionGroups

admin.site.register(Questions, QuestionsAdmin)
admin.site.register(QuestionGroups, QuestionGroupsAdmin)
admin.site.register(Answers)