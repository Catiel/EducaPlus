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
    path('add_cart/<int:curso_id>/', views.add_cart, name='add_cart'),
    path('obtener_contador_carrito/', views.obtener_contador_carrito, name='obtener_contador_carrito'),
    path('login/', views.login_view, name='login'),
    path('recuperarContraseña/', views.olvideContraseña, name='olvide_contraseña'),
    path('correoEnviar/', views.correoEnviar, name='correoEnviar'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    ]
