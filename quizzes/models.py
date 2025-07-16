from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(default=timezone.now)
    time_limit = models.IntegerField(default=30)  # in minutes
    max_attempts = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_submissions(self):
        return self.submissions.count()

    class Meta:
        ordering = ['-created_at']


class Question(models.Model):
    QUESTION_TYPES = (
        ('mc', 'Multiple Choice'),
        ('tf', 'True/False'),
        ('sa', 'Short Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default='mc')
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.question_text[:50]}..."
    
    class Meta:
        ordering = ['order']


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.choice_text


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions')
    score = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(default=timezone.now)
    time_taken = models.DurationField(null=True, blank=True)  # Time taken to complete
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}/{self.total_points}"
    
    @property
    def percentage_score(self):
        if self.total_points > 0:
            return round((self.score / self.total_points) * 100, 2)
        return 0
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['quiz', 'user']  # One submission per user per quiz


class Answer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)  # For short answer questions
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.submission.user.username} - {self.question.question_text[:30]}..."


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-trophy')
    color = models.CharField(max_length=20, default='text-warning')
    requirement = models.IntegerField()  # Number for requirement (e.g., 5 quizzes)
    achievement_type = models.CharField(max_length=20, choices=[
        ('quiz_count', 'Quiz Count'),
        ('high_score', 'High Score'),
        ('streak', 'Streak'),
        ('perfect_score', 'Perfect Score')
    ])
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    total_quizzes_taken = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    joined_date = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    achievements = models.JSONField(default=list, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Admin' if self.is_admin else 'User'}"
    
    @property
    def average_score(self):
        if self.total_quizzes_taken > 0:
            return round(self.total_score / self.total_quizzes_taken, 2)
        return 0
    
    @property
    def get_avatar_url(self):
        """Get user avatar URL or return default"""
        if self.profile_picture:
            return self.profile_picture.url
        return None
    
    @property
    def get_initials(self):
        """Get user initials for avatar fallback"""
        names = self.user.get_full_name().split() if self.user.get_full_name() else [self.user.username]
        return ''.join([name[0].upper() for name in names[:2]])
    
    def add_achievement(self, achievement_name):
        """Add achievement to user profile"""
        if achievement_name not in self.achievements:
            self.achievements.append(achievement_name)
            self.save()
    
    def get_rank(self):
        """Get user's rank based on average score"""
        users_with_higher_score = UserProfile.objects.filter(
            total_quizzes_taken__gt=0,
            total_score__gt=self.total_score
        ).count()
        return users_with_higher_score + 1 if self.total_quizzes_taken > 0 else None


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
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['quiz', 'user']
    
    def __str__(self):
        return f"{self.user.username} rated {self.quiz.title}: {self.rating}/5"
