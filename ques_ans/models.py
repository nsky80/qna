from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from taggit.managers import TaggableManager

class Questions(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField()
    # group = models.ForeignKey('QuestionGroups', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(default=timezone.now)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
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
    answer_text = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    is_anonymous = models.BooleanField(default=False)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id) + " " + self.answer_text[:20]
    
    class Meta:
        verbose_name_plural = "Answers"

