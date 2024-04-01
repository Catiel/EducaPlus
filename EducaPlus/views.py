from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponse
import firebase_admin


# Create your views here.
def index(request):
    return render(request, 'index.html')


def indexLog(request):
    return render(request, 'indexLog.html')


def compraCursos(request):
    return render(request, 'compraCursos.html')


def cursosEstudiante(request):
    return render(request, 'cursosEstudiante.html')


def check_firebase(request):
    try:
        app = firebase_admin.get_app()
        return HttpResponse("Firebase app initialized successfully")
    except ValueError as e:
        return HttpResponse(f"Error initializing Firebase app: {e}")
