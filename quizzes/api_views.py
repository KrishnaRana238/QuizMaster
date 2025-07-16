from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Notification, StudyStreak, QuizFeedback, UserProfile
import json

@login_required
@csrf_exempt
def get_notifications(request):
    """Get user notifications"""
    if request.method == 'GET':
        notifications = Notification.objects.filter(user=request.user, read=False)[:10]
        
        data = []
        for notification in notifications:
            data.append({
                'id': notification.id,
                'type': notification.type,
                'title': notification.title,
                'message': notification.message,
                'created_at': notification.created_at.isoformat(),
            })
        
        return JsonResponse({
            'notifications': data,
            'unread_count': notifications.count()
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notification not found'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def submit_quiz_feedback(request, quiz_id):
    """Submit feedback for a quiz"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating = data.get('rating')
            comment = data.get('comment', '')
            
            if not rating or rating < 1 or rating > 5:
                return JsonResponse({'error': 'Invalid rating'}, status=400)
            
            from .models import Quiz
            quiz = Quiz.objects.get(id=quiz_id)
            
            feedback, created = QuizFeedback.objects.get_or_create(
                quiz=quiz,
                user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            
            if not created:
                feedback.rating = rating
                feedback.comment = comment
                feedback.save()
            
            return JsonResponse({'success': True})
        except Quiz.DoesNotExist:
            return JsonResponse({'error': 'Quiz not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def get_user_streak(request):
    """Get user's study streak"""
    streak, created = StudyStreak.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        'current_streak': streak.current_streak,
        'longest_streak': streak.longest_streak,
        'last_activity': streak.last_activity.isoformat()
    })

def create_notification(user, notification_type, title, message):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message
    )

def update_user_streak(user):
    """Update user's study streak"""
    streak, created = StudyStreak.objects.get_or_create(user=user)
    old_streak = streak.current_streak
    streak.update_streak()
    
    # Create notification for streak milestones
    if streak.current_streak > old_streak and streak.current_streak % 5 == 0:
        create_notification(
            user,
            'achievement',
            f'{streak.current_streak} Day Streak!',
            f'Congratulations! You\'ve maintained a {streak.current_streak} day study streak!'
        )

@login_required
def dashboard_stats(request):
    """Get comprehensive dashboard statistics"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    streak, created = StudyStreak.objects.get_or_create(user=request.user)
    
    # Get recent notifications
    notifications = Notification.objects.filter(user=request.user, read=False)[:5]
    
    # Get user feedback count
    feedback_count = QuizFeedback.objects.filter(user=request.user).count()
    
    data = {
        'profile': {
            'total_quizzes': profile.total_quizzes_taken,
            'average_score': profile.average_score,
            'rank': profile.get_rank(),
            'bio': profile.bio,
            'location': profile.location,
            'joined_date': profile.joined_date.isoformat(),
        },
        'streak': {
            'current': streak.current_streak,
            'longest': streak.longest_streak,
        },
        'notifications': [{
            'id': n.id,
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'created_at': n.created_at.isoformat(),
        } for n in notifications],
        'feedback_count': feedback_count,
    }
    
    return JsonResponse(data)
