from django.contrib import admin
from ques_ans.models import Questions, Answers, Vote

# admin.site.register(QuestionGroups)
# admin.site.register(Questions)

class AnswerInline(admin.TabularInline):
    model = Answers

class QuestionsAdmin(admin.ModelAdmin):

    inlines = [AnswerInline]
    class Meta:
        model = Questions



admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers)
admin.site.register(Vote)
