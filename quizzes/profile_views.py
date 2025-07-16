from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import UserProfile, Quiz, QuizSubmission, Achievement, UserAchievement
import json


@login_required
def profile_view(request, username=None):
    """View user profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user's quiz submissions with detailed stats
    submissions = QuizSubmission.objects.filter(user=user).select_related('quiz')
    
    # Recent activity
    recent_submissions = submissions.order_by('-submitted_at')[:5]
    
    # Subject-wise performance
    subject_performance = {}
    for submission in submissions:
        subject = submission.quiz.subject
        if subject not in subject_performance:
            subject_performance[subject] = {'total': 0, 'scores': []}
        subject_performance[subject]['total'] += 1
        subject_performance[subject]['scores'].append(submission.score)
    
    # Calculate averages
    for subject in subject_performance:
        scores = subject_performance[subject]['scores']
        subject_performance[subject]['average'] = sum(scores) / len(scores) if scores else 0
    
    # Get achievements
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
    
    # Check for new achievements
    check_achievements(user)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'recent_submissions': recent_submissions,
        'subject_performance': subject_performance,
        'user_achievements': user_achievements,
        'is_own_profile': request.user == user,
    }
    
    return render(request, 'quizzes/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile fields
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.website = request.POST.get('website', '')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        # Update preferences
        preferences = {
            'theme': request.POST.get('theme', 'light'),
            'notifications': request.POST.get('notifications') == 'on',
            'public_profile': request.POST.get('public_profile') == 'on'
        }
        profile.preferences = preferences
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'quizzes/edit_profile.html', {'profile': profile})


@login_required
def leaderboard(request):
    """Show leaderboard with top users"""
    # Get top users by average score
    top_users = UserProfile.objects.filter(
        total_quizzes_taken__gt=0
    ).annotate(
        avg_score=F('total_score') / F('total_quizzes_taken')
    ).order_by('-avg_score')[:50]
    
    # Get current user's rank
    current_user_profile = UserProfile.objects.get(user=request.user)
    current_user_rank = current_user_profile.get_rank()
    
    context = {
        'top_users': top_users,
        'current_user_rank': current_user_rank,
        'current_user_profile': current_user_profile
    }
    
    return render(request, 'quizzes/leaderboard.html', context)


def check_achievements(user):
    """Check and award achievements to user"""
    profile = UserProfile.objects.get(user=user)
    
    # Define achievement criteria
    achievement_checks = [
        {
            'name': 'First Steps',
            'description': 'Complete your first quiz',
            'icon': 'fa-star',
            'color': 'text-success',
            'requirement': 1,
            'type': 'quiz_count'
        },
        {
            'name': 'Quiz Master',
            'description': 'Complete 10 quizzes',
            'icon': 'fa-trophy',
            'color': 'text-warning',
            'requirement': 10,
            'type': 'quiz_count'
        },
        {
            'name': 'Perfect Score',
            'description': 'Score 100% on a quiz',
            'icon': 'fa-gem',
            'color': 'text-primary',
            'requirement': 100,
            'type': 'high_score'
        },
        {
            'name': 'Consistent Performer',
            'description': 'Complete 25 quizzes',
            'icon': 'fa-chart-line',
            'color': 'text-info',
            'requirement': 25,
            'type': 'quiz_count'
        }
    ]
    
    for achievement_data in achievement_checks:
        # Check if achievement exists
        achievement, created = Achievement.objects.get_or_create(
            name=achievement_data['name'],
            defaults={
                'description': achievement_data['description'],
                'icon': achievement_data['icon'],
                'color': achievement_data['color'],
                'requirement': achievement_data['requirement'],
                'achievement_type': achievement_data['type']
            }
        )
        
        # Check if user has earned this achievement
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            earned = False
            
            if achievement_data['type'] == 'quiz_count':
                earned = profile.total_quizzes_taken >= achievement_data['requirement']
            elif achievement_data['type'] == 'high_score':
                earned = QuizSubmission.objects.filter(
                    user=user, 
                    score__gte=achievement_data['requirement']
                ).exists()
            
            if earned:
                UserAchievement.objects.create(user=user, achievement=achievement)


@csrf_exempt
@login_required
def api_user_stats(request):
    """API endpoint for user statistics"""
    if request.method == 'GET':
        profile = UserProfile.objects.get(user=request.user)
        
        # Get monthly quiz data for chart
        monthly_data = []
        for month in range(1, 13):
            count = QuizSubmission.objects.filter(
                user=request.user,
                submitted_at__month=month,
                submitted_at__year=timezone.now().year
            ).count()
            monthly_data.append(count)
        
        # Get subject performance
        subject_stats = {}
        submissions = QuizSubmission.objects.filter(user=request.user).select_related('quiz')
        
        for submission in submissions:
            subject = submission.quiz.subject
            if subject not in subject_stats:
                subject_stats[subject] = {'count': 0, 'total_score': 0}
            subject_stats[subject]['count'] += 1
            subject_stats[subject]['total_score'] += submission.score
        
        # Calculate averages
        for subject in subject_stats:
            subject_stats[subject]['average'] = round(
                subject_stats[subject]['total_score'] / subject_stats[subject]['count'], 2
            )
        
        data = {
            'monthly_quizzes': monthly_data,
            'subject_performance': subject_stats,
            'total_quizzes': profile.total_quizzes_taken,
            'average_score': profile.average_score,
            'rank': profile.get_rank()
        }
        
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
