from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check_firebase/', views.check_firebase, name='check_firebase'),
    path('compraCursos/', views.compraCursos, name='compraCursos'),
    path('cursosEstudiante/', views.cursosEstudiante, name='cursosEstudiante'),
    path('indexLog/', views.indexLog, name='indexLog'),
]