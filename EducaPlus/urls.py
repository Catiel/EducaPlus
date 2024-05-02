from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('compraCursos/<int:curso_id>/', views.compraCursos, name='compraCursos'),
    path('cursosEstudiante/', views.cursosEstudiante, name='cursosEstudiante'),
    path('indexLog/', views.indexLog, name='indexLog'),
    path('crearCursos/', views.crearCursos, name='crearCursos'),
    path('crearDatosCursos/', views.crearDatosCursos, name='crearDatosCursos'),
    path('register/', views.register, name='register'),
    path('teach/', views.teach, name='teach'),
    path('logout/', views.logout_view, name='logout'),
    path('crear_curso/', views.crear_curso, name='crear_curso'),
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
    path('api/verificar-correo/', views.verificar_correo, name='verificar_correo'),
    path('obtener-datos-usuario/', views.obtener_datos_usuario, name='obtener_datos_usuario'),
    path('obtener-datos-instructor/', views.obtener_datos_instructor, name='obtener_datos_instructor'),
    path('updateEstudiante/', views.updateEstudiante, name='updateEstudiante'),
    path('update-instructor/', views.updateInstructor, name='updateInstructor'),
]
