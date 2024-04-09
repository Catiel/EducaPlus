import firebase_admin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Student, Instructor, Curso, Compra
from django.contrib.auth.models import Group
from .decorators import group_required
from django.shortcuts import get_object_or_404
from django.db.models import Case, When


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        birthdate = request.POST['birthdate']

        if password == password_confirm:
            if User.objects.filter(username=email).exists():
                messages.error(request, 'El correo electrónico ya está en uso')
                return redirect('index')
            else:
                user = User.objects.create_user(username=email, password=password, email=email, first_name=name,
                                                last_name=surname)
                Student.objects.create(user=user, birthdate=birthdate)
                user.save()
                group = Group.objects.get(name='Estudiantes')
                user.groups.add(group)
                login(request, user)
                messages.success(request, 'Te has registrado exitosamente')
                return redirect('indexLog')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('index')
    else:
        return render(request, 'index.html')


def teach(request):
    if request.method == 'POST':
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['passwordConfirm']
        birthdate = request.POST['birthdate1']
        specialization = request.POST['specialization']

        if password == password_confirm:
            if User.objects.filter(username=email).exists():
                messages.error(request, 'El correo electrónico ya está en uso')
                return redirect('index')
            else:
                user = User.objects.create_user(username=email, password=password, email=email, first_name=name,
                                                last_name=surname)
                Instructor.objects.create(user=user, birthdate=birthdate, specialization=specialization)
                user.save()
                group = Group.objects.get(name='Instructores')
                user.groups.add(group)
                login(request, user)
                messages.success(request, 'Te has registrado exitosamente como instructor')
                return redirect('crearCursos')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('index')
    else:
        return render(request, 'index.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('index')


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Estudiantes').exists():
            return redirect('indexLog')
        elif request.user.groups.filter(name='Instructores').exists():
            return redirect('crearCursos')

    categorias, cursos = obtener_categorias_cursos_ordenados()
    return render(request, 'index.html', {'cursos': cursos, 'categorias': categorias})


@login_required
@group_required('Estudiantes', redirect_route='crearCursos')
def indexLog(request):
    categorias, cursos = obtener_categorias_cursos_ordenados()
    return render(request, 'indexLog.html', {'cursos': cursos, 'categorias': categorias})


def obtener_categorias_cursos_ordenados():
    orden_categorias = ['Tecnología', 'Economía', 'Humanidades', 'Medicina', 'Ciencias jurídicas', 'Arquitectura']
    categorias = list(Curso.objects.values_list('categoria', flat=True).distinct())
    categorias.sort(key=lambda x: orden_categorias.index(x) if x in orden_categorias else len(orden_categorias))
    cursos = Curso.objects.all().order_by('nombre')
    return categorias, cursos


@login_required
@group_required('Estudiantes', redirect_route='crearCursos')
def compraCursos(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    return render(request, 'compraCursos.html', {'curso': curso})


@login_required
@group_required('Estudiantes', redirect_route='crearCursos')
def cursosEstudiante(request):
    return render(request, 'cursosEstudiante.html')


@login_required
@group_required('Instructores', redirect_route='indexLog')
def crearCursos(request):
    cursos_del_instructor = Curso.objects.filter(instructor__user=request.user)
    return render(request, 'crearCurso.html', {'cursos_del_instructor': cursos_del_instructor})


@login_required
@group_required('Instructores', redirect_route='indexLog')
def crearDatosCursos(request):
    return render(request, 'crearDatosCurso.html')


@login_required
@group_required('Instructores', redirect_route='indexLog')
def crear_curso(request):
    if request.method == 'POST':
        nombre = request.POST['courseName']
        descripcion = request.POST['courseDescription']
        categoria = request.POST['courseCategory']
        duracion = request.POST['courseDuration']
        nivel = request.POST['courseDifficulty']
        coursePayment = request.POST['coursePayment']
        precio = request.POST['courseCost'] if coursePayment == 'pago' else 0.0
        curso = Curso(nombre=nombre, descripcion=descripcion, categoria=categoria, duracion=duracion,
                      nivel=nivel, precio=precio, instructor=request.user.instructor)
        curso.save()

        messages.success(request, 'Curso creado exitosamente')
        return redirect('crearCursos')
    else:
        return render(request, 'crearCurso.html')


@csrf_exempt
def procesar_pago(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')
        estudiante_id = request.POST.get('estudiante_id')
        # Si el pago es exitoso, crea una nueva instancia de Compra
        compra = Compra(estudiante_id=estudiante_id, curso_id=curso_id)
        compra.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed'})


def check_firebase(request):
    try:
        firebase_admin.get_app()
        return HttpResponse("Firebase app initialized successfully")
    except ValueError as e:
        return HttpResponse(f"Error initializing Firebase app: {e}")
