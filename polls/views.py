from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group  # Add this import
from django.db import IntegrityError
from .models import Choice, Question, Vote
from .forms import QuestionForm, ChoiceFormSet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    paginate_by = 5
    
    def get_queryset(self):
        """Return questions filtered by search query if provided."""
        queryset = Question.objects.order_by('-pub_date')
        
        # Get search query from URL parameters
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            # Search in question text (case-insensitive)
            queryset = queryset.filter(
                question_text__icontains=search_query
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_admin'] = is_admin(self.request.user)
        
        # Pass search query to template to maintain it in the search box
        context['search_query'] = self.request.GET.get('search', '')
        return context

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if current user has voted on this question
        if self.request.user.is_authenticated:
            user_vote = Vote.objects.filter(
                user=self.request.user, 
                question=self.object
            ).first()
            context['user_vote'] = user_vote
        
        return context
    
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


# Helper function to check if user is admin
# Fixed version (works for both superusers and Admins group members)
def is_admin(user):
    return user.is_superuser or user.is_staff .exists()



@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # Handle non-POST requests
    if request.method != 'POST':
        return redirect('polls:detail', question_id=question_id)
    
    # Check if user has already voted on this question
    existing_vote = Vote.objects.filter(user=request.user, question=question).first()
    if existing_vote:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': f"You have already voted on this poll. You selected '{existing_vote.choice.choice_text}'.",
        })
    
    # Get choice ID from POST data
    choice_id = request.POST.get('choice')
    
    # Check if choice was provided
    if not choice_id:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    
    # Try to get the selected choice
    try:
        selected_choice = question.choice_set.get(pk=choice_id)
    except Choice.DoesNotExist:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Invalid choice selected.",
        })
    
    # Create vote record and increment choice votes
    try:
        Vote.objects.create(
            user=request.user,
            question=question,
            choice=selected_choice
        )
        selected_choice.votes += 1
        selected_choice.save()
        
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    except IntegrityError:
        # Handle race condition - user somehow voted twice simultaneously
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You have already voted on this poll.",
        })
@login_required
@user_passes_test(is_admin)
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


@login_required
@user_passes_test(is_admin)
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


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically assign to Voters group
            voters_group, created = Group.objects.get_or_create(name='Voters')
            user.groups.add(voters_group)
            login(request, user)  # Auto-login after registration
            return redirect('polls:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def get_queryset(self):
    """Return questions with enhanced search capabilities."""
    queryset = Question.objects.order_by('-pub_date')
    
    search_query = self.request.GET.get('search', '').strip()
    
    if search_query:
        # Search in both question text and choice text
        queryset = queryset.filter(
            models.Q(question_text__icontains=search_query) |
            models.Q(choice__choice_text__icontains=search_query)
        ).distinct()
    
    return queryset
