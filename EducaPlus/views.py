import firebase_admin
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def indexLog(request):
    return render(request, 'indexLog.html')


def compraCursos(request):
    return render(request, 'compraCursos.html')


def cursosEstudiante(request):
    return render(request, 'cursosEstudiante.html')


def crearCursos(request):
    return render(request, 'crearCurso.html')


def crearDatosCursos(request):
    return render(request, 'crearDatosCurso.html')


def check_firebase(request):
    try:
        firebase_admin.get_app()
        return HttpResponse("Firebase app initialized successfully")
    except ValueError as e:
        return HttpResponse(f"Error initializing Firebase app: {e}")
