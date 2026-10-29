from django.urls import path
from . import api, views


urlpatterns = [
    path('', views.survey_list, name='survey-list'),
    path('surveys/<int:survey_id>/', views.survey_start, name='survey-start'),
    path('surveys/<int:survey_id>/question/', views.survey_question,
         name='survey-question'),
    path('surveys/<int:survey_id>/complete/', views.survey_complete,
         name='survey-complete'),
    path('api/surveys/<int:survey_id>/next-question/', api.next_question,
         name='api-next-question'),
    path('api/surveys/<int:survey_id>/answers/', api.submit_answer,
         name='api-submit-answer'),
]
