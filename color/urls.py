from django.urls import path
from color import views


urlpatterns = [
    path('', views.color_list, name='color_list'),
    path('color_detail/<int:color_id>', views.color_detail, name='color_detail'),
    path('new_color/', views.new_color, name='new_color'),
    path('edit_color/<int:color_id>/', views.edit_color, name='edit_color'),
    path('delete_color/<int:color_id>/', views.delete_color, name='delete_color'),
    path('question_start/', views.question_start, name='question_start'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    path('result/', views.result, name='result'),
    path('processing', views.processing, name='processing'),
]
