from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('achievement', 'Achievement'),
        ('quiz_result', 'Quiz Result'),
        ('rank_change', 'Rank Change'),
        ('new_quiz', 'New Quiz'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class QuizAnalytics(models.Model):
    """Store quiz analytics data"""
    quiz = models.OneToOneField('Quiz', on_delete=models.CASCADE)
    total_attempts = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)
    difficulty_rating = models.FloatField(default=0.0)
    time_spent_avg = models.IntegerField(default=0)  # in seconds
    
    def __str__(self):
        return f"Analytics for {self.quiz.title}"

class StudyStreak(models.Model):
    """Track user study streaks"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} days"
    
    def update_streak(self):
        """Update streak based on activity"""
        today = timezone.now().date()
        
        if self.last_activity == today:
            # Already updated today
            return
        
        if self.last_activity == today - timezone.timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
        elif self.last_activity < today - timezone.timedelta(days=1):
            # Streak broken
            self.current_streak = 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_activity = today
        self.save()

class QuizFeedback(models.Model):
    """User feedback on quizzes"""
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['quiz', 'user']
    
    def __str__(self):
        return f"{self.user.username} rated {self.quiz.title}: {self.rating}/5"
