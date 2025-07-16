from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json

from .models import Quiz, Question, Choice, QuizSubmission, Answer, UserProfile
from .forms import QuizForm, QuestionForm


def landing_page(request):
    """Landing page with animated features showcase"""
    return render(request, 'quizzes/landing.html')


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Custom logout view"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Check if user should be admin
            if request.POST.get('is_admin') == 'on':
                profile.is_admin = True
                profile.save()
            
            # Authenticate and login the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome to Quizmaster, {username}! Your account has been created successfully.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    """Enhanced dashboard for both admin and regular users"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.is_admin:
        # Admin dashboard
        quizzes = Quiz.objects.filter(creator=request.user).annotate(
            submission_count=Count('submissions')
        )
        
        # Get recent submissions for admin's quizzes
        recent_submissions = QuizSubmission.objects.filter(
            quiz__creator=request.user
        ).select_related('user', 'quiz').order_by('-submitted_at')[:10]
        
        # Calculate admin stats
        total_submissions = QuizSubmission.objects.filter(quiz__creator=request.user).count()
        avg_score = QuizSubmission.objects.filter(quiz__creator=request.user).aggregate(
            avg=Avg('score')
        )['avg'] or 0
        
        context = {
            'is_admin': True,
            'user_profile': profile,
            'quizzes': quizzes,
            'total_quizzes': quizzes.count(),
            'total_submissions': total_submissions,
            'average_score': avg_score,
            'recent_submissions': recent_submissions,
            'progress_percentage': min(100, (quizzes.count() * 20)),  # Simple progress calculation
            'user_rank': 1,  # Admin is always rank 1 for their own quizzes
        }
    else:
        # User dashboard
        submissions = QuizSubmission.objects.filter(user=request.user).select_related('quiz')
        available_quizzes = Quiz.objects.filter(is_active=True).exclude(
            submissions__user=request.user
        )[:6]  # Limit to 6 for display
        
        # Calculate user stats
        total_quizzes_taken = submissions.count()
        avg_score = submissions.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Get recent submissions
        recent_submissions = submissions.order_by('-submitted_at')[:5]
        
        # Calculate progress percentage based on quizzes taken
        total_available_quizzes = Quiz.objects.filter(is_active=True).count()
        if total_available_quizzes > 0:
            progress_percentage = (total_quizzes_taken / total_available_quizzes) * 100
        else:
            progress_percentage = 0
        
        # Get user rank (simplified ranking based on average score)
        user_rank = QuizSubmission.objects.filter(
            score__gt=avg_score
        ).values('user').distinct().count() + 1 if avg_score > 0 else None
        
        # Get top performers
        top_performers = QuizSubmission.objects.values('user__username').annotate(
            avg_score=Avg('score'),
            total_quizzes=Count('id')
        ).filter(total_quizzes__gt=0).order_by('-avg_score')[:5]
        
        context = {
            'is_admin': False,
            'user_profile': profile,
            'submissions': submissions,
            'available_quizzes': available_quizzes,
            'total_quizzes': total_quizzes_taken,
            'total_submissions': total_quizzes_taken,
            'average_score': avg_score,
            'recent_submissions': recent_submissions,
            'progress_percentage': progress_percentage,
            'user_rank': user_rank,
            'top_performers': top_performers,
        }
    
    return render(request, 'quizzes/dashboard.html', context)


@login_required
def create_quiz(request):
    """Create a new quiz (Admin only)"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_admin:
        messages.error(request, 'Only admins can create quizzes.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully!')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    return render(request, 'quizzes/create_quiz.html', {'form': form})


@login_required
def add_questions(request, quiz_id):
    """Add questions to a quiz (Admin only)"""
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.order = quiz.questions.count() + 1
            question.save()
            
            # Add choices for multiple choice questions
            if question.question_type == 'mc':
                choices_data = request.POST.getlist('choices')
                correct_choice = int(request.POST.get('correct_choice', 0))
                
                for i, choice_text in enumerate(choices_data):
                    if choice_text.strip():
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            is_correct=(i == correct_choice)
                        )
            
            messages.success(request, 'Question added successfully!')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    questions = quiz.questions.all()
    return render(request, 'quizzes/add_questions.html', {
        'quiz': quiz,
        'form': form,
        'questions': questions
    })


@login_required
def take_quiz(request, quiz_id):
    """Take a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has already taken this quiz
    if QuizSubmission.objects.filter(quiz=quiz, user=request.user).exists():
        messages.error(request, 'You have already taken this quiz.')
        return redirect('dashboard')
    
    questions = quiz.questions.prefetch_related('choices').all()
    
    if request.method == 'POST':
        # Process quiz submission
        submission = QuizSubmission.objects.create(
            quiz=quiz,
            user=request.user,
            total_points=sum(q.points for q in questions)
        )
        
        score = 0
        for question in questions:
            if question.question_type == 'mc':
                selected_choice_id = request.POST.get(f'question_{question.id}')
                if selected_choice_id:
                    selected_choice = Choice.objects.get(id=selected_choice_id)
                    is_correct = selected_choice.is_correct
                    if is_correct:
                        score += question.points
                    
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        selected_choice=selected_choice,
                        is_correct=is_correct
                    )
            elif question.question_type == 'tf':
                answer = request.POST.get(f'question_{question.id}')
                correct_answer = question.choices.filter(is_correct=True).first()
                is_correct = answer == correct_answer.choice_text if correct_answer else False
                if is_correct:
                    score += question.points
                
                Answer.objects.create(
                    submission=submission,
                    question=question,
                    text_answer=answer,
                    is_correct=is_correct
                )
        
        submission.score = score
        submission.save()
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.total_quizzes_taken += 1
        profile.total_score += score
        profile.save()
        
        messages.success(request, f'Quiz submitted! Your score: {score}/{submission.total_points}')
        return redirect('quiz_results', submission_id=submission.id)
    
    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })


@login_required
def quiz_results(request, submission_id):
    """View quiz results"""
    submission = get_object_or_404(QuizSubmission, id=submission_id, user=request.user)
    answers = submission.answers.select_related('question', 'selected_choice').all()
    
    return render(request, 'quizzes/quiz_results.html', {
        'submission': submission,
        'answers': answers
    })


@login_required
def leaderboard(request):
    """View leaderboard"""
    # Get top users by average score
    top_users = UserProfile.objects.filter(
        total_quizzes_taken__gt=0
    ).order_by('-total_score')[:10]
    
    # Get recent submissions
    recent_submissions = QuizSubmission.objects.select_related(
        'user', 'quiz'
    ).order_by('-submitted_at')[:10]
    
    return render(request, 'quizzes/leaderboard.html', {
        'top_users': top_users,
        'recent_submissions': recent_submissions
    })


@login_required
def quiz_list(request):
    """List all available quizzes for users"""
    if request.GET.get('creator'):
        creator_username = request.GET.get('creator')
        quizzes = Quiz.objects.filter(
            creator__username=creator_username,
            is_active=True
        ).exclude(submissions__user=request.user)
    else:
        quizzes = Quiz.objects.filter(is_active=True).exclude(
            submissions__user=request.user
        )
    
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


@login_required
def admin_quiz_results(request, quiz_id):
    """View all results for a specific quiz (Admin only)"""
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    submissions = quiz.submissions.select_related('user').order_by('-score')
    
    return render(request, 'quizzes/admin_quiz_results.html', {
        'quiz': quiz,
        'submissions': submissions
    })


@login_required
def delete_quiz(request, quiz_id):
    """Delete a quiz (Admin only)"""
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'quizzes/delete_quiz.html', {'quiz': quiz})


def search_creators(request):
    """AJAX endpoint to search for quiz creators"""
    query = request.GET.get('q', '')
    if query:
        creators = User.objects.filter(
            username__icontains=query,
            userprofile__is_admin=True
        ).values('username')[:10]
        return JsonResponse({'creators': list(creators)})
    return JsonResponse({'creators': []})
