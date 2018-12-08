from django.urls import path
from color import views


urlpatterns = [
    path('', views.color_list, name='color_list'),
    path('color_detail/<int:color_id>', views.color_detail, name='color_detail'),
    path('question_start/', views.question_start, name='question_start'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    path('result/', views.result, name='result'),
    path('processing', views.processing, name='processing'),
]
