from django.urls import path
from . import views
from . import profile_views
from . import api_views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-quiz/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/add-questions/', views.add_questions, name='add_questions'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/results/', views.admin_quiz_results, name='admin_quiz_results'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('submission/<int:submission_id>/results/', views.quiz_results, name='quiz_results'),
    path('leaderboard/', profile_views.leaderboard, name='leaderboard'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('search-creators/', views.search_creators, name='search_creators'),
    path('profile/', profile_views.profile_view, name='profile'),
    path('profile/<str:username>/', profile_views.profile_view, name='profile'),
    path('profile/edit/', profile_views.edit_profile, name='edit_profile'),
    path('api/user-stats/', profile_views.api_user_stats, name='api_user_stats'),
    path('api/notifications/', api_views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', api_views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/read-all/', api_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/quiz/<int:quiz_id>/feedback/', api_views.submit_quiz_feedback, name='submit_quiz_feedback'),
    path('api/streak/', api_views.get_user_streak, name='get_user_streak'),
    path('api/dashboard-stats/', api_views.dashboard_stats, name='dashboard_stats'),
]
