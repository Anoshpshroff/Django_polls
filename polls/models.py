import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
    
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure one vote per user per question
        unique_together = ('user', 'question')
    
    def __str__(self):
        return f"{self.user.username} voted on {self.question.question_text}"
# Optional: Automatically assign new users to "Voters" group
@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        voters_group, created = Group.objects.get_or_create(name='Voters')
        instance.groups.add(voters_group)