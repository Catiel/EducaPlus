from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check_firebase/', views.check_firebase, name='check_firebase'),
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
    #######Mirza
    path('obtener-datos-usuario/', views.obtener_datos_usuario, name='obtener_datos_usuario'),
    path('obtener-datos-instructor/', views.obtener_datos_instructor, name='obtener_datos_instructor'),
     # Ruta para la vista de edición de perfil
    path('editar-perfil/', views.edit_profile, name='editar_perfil'),

    # Ruta para obtener los datos del usuario (usada en AJAX)
    path('obtener-datos-usuario/', views.get_user_data, name='obtener_datos_usuario'),

    # Ruta para guardar los datos actualizados del usuario (usada en AJAX)
    path('guardar-datos-usuario/', views.save_user_data, name='guardar_datos_usuario'),
]