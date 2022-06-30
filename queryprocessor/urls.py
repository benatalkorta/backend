from django.urls import path
from .views import ListQuestions, ExecuteQueryByID, InsertStudentInDatabase, DeleteStudentInDatabase


urlpatterns = [

    path('get-questions', ListQuestions.as_view()),
    path('execute-query/<int:question_id>/', ExecuteQueryByID.as_view()),
    path('insert-student', InsertStudentInDatabase.as_view()),
    path('delete-student', DeleteStudentInDatabase.as_view())

]