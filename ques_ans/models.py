from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


# from ques_ans.models import Activity
class Activity(models.Model):
    FAVORITE = 'F'
    LIKE = 'L'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (LIKE, 'Like'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )

    # user = models.ForeignKey(User)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)

    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    # Below the mandatory fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return str(self.object_id) + " " + str(self.activity_type) + " " + str(self.content_type) + " username: " + self.user.username
    
    class Meta:
        verbose_name_plural = "Activity/Votes"


class Questions(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(verbose_name="Question Title/Heading", null=False, blank=False, max_length=500)
    # group = models.ForeignKey('QuestionGroups', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(default=timezone.now)
    question_description = models.TextField(null=True)
    # It will keep track of number of upvotes, downvotes and bookmarks
    # Users can up vote/down vote and favorite it.
    activities = GenericRelation(Activity)

    views = models.IntegerField(default=0)
    slug = models.SlugField()
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title[:80])
        super(Questions, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Questions"


class Answers(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    # answer_text = models.TextField()
    answer_text = models.TextField("Main Content", help_text='Write here your message!')

    created_on = models.DateTimeField(default=timezone.now)
    is_anonymous = models.BooleanField(default=False)
    # with the Answer model, user can only up vote/down vote
    votes = GenericRelation(Activity)

    def __str__(self):
        return str(self.id) + " " + self.answer_text[:20]
    
    class Meta:
        verbose_name_plural = "Answers"




# class Vote(models.Model):
#     VOTE_CHOICES = (
#         (1, 'up'),
#         (2, 'down'),
#         (3, 'N/A'),
#     )
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
#     question = models.ForeignKey(Questions, on_delete=models.CASCADE, null=False)
#     user_vote = models.IntegerField(choices=VOTE_CHOICES, null=True)

#     class Meta:
#         unique_together = ('user', 'question',)


#     def __str__(self):
#         return self.question.title + " username: " + self.user.username
