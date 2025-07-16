from django.contrib import admin
from .models import Quiz, Question, Choice, QuizSubmission, Answer, UserProfile


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'created_at', 'is_active', 'total_questions', 'total_submissions']
    list_filter = ['is_active', 'created_at', 'creator']
    search_fields = ['title', 'description', 'creator__username']
    inlines = [QuestionInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('questions', 'submissions')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz', 'points']
    search_fields = ['question_text', 'quiz__title']
    inlines = [ChoiceInline]
    ordering = ['quiz', 'order']


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['choice_text', 'question__question_text']


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total_points', 'percentage_score', 'submitted_at']
    list_filter = ['submitted_at', 'quiz', 'score']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['submitted_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'quiz')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'is_correct', 'selected_choice', 'text_answer']
    list_filter = ['is_correct', 'question__question_type']
    search_fields = ['submission__user__username', 'question__question_text']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submission__user', 'question', 'selected_choice')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_admin', 'total_quizzes_taken', 'total_score', 'average_score']
    list_filter = ['is_admin', 'total_quizzes_taken']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['average_score']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
