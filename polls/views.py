from django.shortcuts import get_object_or_404, render , redirect
from django.http import HttpResponse , HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question
from .forms import QuestionForm, ChoiceFormSet


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def create(request):
    # Your logic here (render the form, process submission, etc.)
    return render(request, 'polls/create.html')

def create_poll(request):
    if request.method == 'POST':
        # Create question manually from form data
        question_text = request.POST.get('question_text')
        pub_date = request.POST.get('pub_date')
        
        if question_text and pub_date:
            # Create the question
            question = Question.objects.create(
                question_text=question_text,
                pub_date=pub_date
            )
            
            # Handle formset choices
            formset = ChoiceFormSet(request.POST)
            if formset.is_valid():
                choices = formset.save(commit=False)
                for choice in choices:
                    if choice.choice_text and choice.choice_text.strip():
                        choice.question = question
                        choice.save()
            
            # Handle dynamic choices
            dynamic_choices = request.POST.getlist('dynamic_choices')
            for choice_text in dynamic_choices:
                if choice_text.strip():
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text.strip(),
                        votes=0
                    )
            
            return redirect('polls:index')
    
    # For GET requests
    question_form = QuestionForm()
    formset = ChoiceFormSet()
    
    return render(request, 'polls/create_poll.html', {
        'question_form': question_form,
        'formset': formset
    })
    
def edit_polls(request):
    """View to manage questions and choices - add or delete them"""
    questions = Question.objects.all().order_by('-pub_date')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_question':
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=question_id)
            question.delete()
            return redirect('polls:editpoll')
        
        elif action == 'add_choice':
            question_id = request.POST.get('question_id')
            choice_text = request.POST.get('choice_text')
            if choice_text:
                question = get_object_or_404(Question, id=question_id)
                Choice.objects.create(question=question, choice_text=choice_text)
            return redirect('polls:editpoll')
        
        elif action == 'delete_choice':
            choice_id = request.POST.get('choice_id')
            choice = get_object_or_404(Choice, id=choice_id)
            choice.delete()
            return redirect('polls:editpoll')
    
    return render(request, 'polls/edit_polls.html', {'questions': questions})