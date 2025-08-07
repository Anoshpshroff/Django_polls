from django import forms
from .models import Question, Choice
from django.forms import inlineformset_factory
from django.utils import timezone


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'pub_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('pub_date'):
            self.initial['pub_date'] = timezone.now()

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=['choice_text'],
    extra=3,         
    can_delete=False  
)

