from django.urls import path
from .views import GetQueryResults, ListQuestions, ExecuteQueryByID


urlpatterns = [

    path('get-results', GetQueryResults.as_view()),
    path('get-questions', ListQuestions.as_view()),
    path('execute-query/<int:question_id>/', ExecuteQueryByID.as_view())
]
