from datetime import datetime

from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login, logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt

from .decorators import group_required
from .models import Student, Instructor, Curso, Compra, Cart


@csrf_exempt
def verificar_correo_teach(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', None)
        if correo:
            try:
                user_obj = User.objects.get(email=correo)
                return JsonResponse({'existe': True})
            except User.DoesNotExist:
                return JsonResponse({'existe': False})
        else:
            return JsonResponse(
                {'error': 'Correo no proporcionado en la solicitud'},
                status=400)

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.groups.filter(name='Instructores').exists():
                login(request, user)
                return JsonResponse(
                    {'success': True, 'userType': 'Instructor'})
            elif user.groups.filter(name='Estudiantes').exists():
                login(request, user)
                return JsonResponse(
                    {'success': True, 'userType': 'Estudiante'})
        else:
            # Verificar el tipo de error
            try:
                existing_user = User.objects.get(email=email)
                if existing_user:
                    return JsonResponse(
                        {'success': False, 'errorType': 'incorrectPassword'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'errorType': 'emailNotFound'})
    return JsonResponse({'success': False, 'errorType': 'incorrectCredentials'})


@csrf_exempt
def verificar_correo(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', None)
        if correo:
            try:
                user_obj = User.objects.get(email=correo)
                return JsonResponse({'existe': True})
            except User.DoesNotExist:
                return JsonResponse({'existe': False})
        else:
            return JsonResponse(
                {'error': 'Correo no proporcionado en la solicitud'},
                status=400)

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        birthdate = request.POST['birthdate']

        if password == password_confirm:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está en uso')
                return redirect('index')
            else:
                user = User.objects.create_user(username=email,
                                                password=password, email=email,
                                                first_name=name,
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
                user = User.objects.create_user(username=email,
                                                password=password, email=email,
                                                first_name=name,
                                                last_name=surname)
                Instructor.objects.create(user=user, birthdate=birthdate,
                                          specialization=specialization)
                user.save()
                group = Group.objects.get(name='Instructores')
                user.groups.add(group)
                login(request, user)
                messages.success(request,
                                 'Te has registrado exitosamente como '
                                 'instructor')
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
    return render(request, 'index.html',
                  {'cursos': cursos, 'categorias': categorias})


@login_required
@group_required('Estudiantes', redirect_route='crearCursos')
def indexLog(request):
    categorias, cursos = obtener_categorias_cursos_ordenados()
    return render(request, 'indexLog.html',
                  {'cursos': cursos, 'categorias': categorias})


def obtener_categorias_cursos_ordenados():
    orden_categorias = ['Tecnología', 'Economía', 'Humanidades', 'Medicina',
                        'Ciencias jurídicas', 'Arquitectura']
    categorias = list(
        Curso.objects.values_list('categoria', flat=True).distinct())
    categorias.sort(key=lambda x: orden_categorias.index(
        x) if x in orden_categorias else len(orden_categorias))
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
    compras = Compra.objects.filter(estudiante_id=request.user.student.id)
    cursos = [compra.curso for compra in compras]
    return render(request, 'cursosEstudiante.html', {'cursos': cursos})


@login_required
@group_required('Instructores', redirect_route='indexLog')
def crearCursos(request):
    cursos_del_instructor = Curso.objects.filter(instructor__user=request.user)
    return render(request, 'crearCurso.html',
                  {'cursos_del_instructor': cursos_del_instructor})


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
        coursepayment = request.POST['coursePayment']
        precio = request.POST['courseCost'] if coursepayment == 'pago' else 0.0
        curso = Curso(nombre=nombre, descripcion=descripcion,
                      categoria=categoria, duracion=duracion,
                      nivel=nivel, precio=precio,
                      instructor=request.user.instructor)
        curso.save()

        messages.success(request, 'Curso creado exitosamente')
        return redirect('crearCursos')
    else:
        return render(request, 'crearCurso.html')


@login_required
@group_required('Estudiantes', redirect_route='crearCursos')
@csrf_exempt
def procesar_pago(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')
        estudiante_id = request.POST.get('estudiante_id')

        if Compra.objects.filter(estudiante_id=estudiante_id,
                                 curso_id=curso_id).exists():
            return JsonResponse(
                {'status': 'failed', 'message': 'Ya has comprado este curso'})

        # Si el pago es exitoso, crea una nueva instancia de Compra
        compra = Compra(estudiante_id=estudiante_id, curso_id=curso_id)
        compra.save()

        messages.success(request, 'Pago procesado exitosamente')
        return redirect('cursosEstudiante')
    else:
        return JsonResponse({'status': 'failed'})


@login_required
def add_cart(request, curso_id):
    # Obtiene el carrito de compras del usuario actual
    cart, created = Cart.objects.get_or_create(student=request.user.student)

    # Obtiene el curso que se va a agregar al carrito
    curso = get_object_or_404(Curso, id=curso_id)

    # Verifica si el curso ya está en el carrito
    if cart.courses.filter(id=curso_id).exists():
        # Si el curso ya está en el carrito, devuelve un error
        return JsonResponse(
            {'success': False, 'error': 'El curso ya está en el carrito'})

    # Si el curso no está en el carrito, lo agrega
    cart.add_course(curso)

    # Devuelve una respuesta JSON con el número de cursos en el carrito
    return JsonResponse(
        {'success': True, 'cart_count': cart.courses.count()})


@login_required
def obtener_contador_carrito(request):
    # Obtiene el carrito de compras del usuario actual
    cart, created = Cart.objects.get_or_create(student=request.user.student)

    # Devuelve el contador del carrito como una respuesta JSON
    return JsonResponse({'success': True, 'cart_count': cart.courses.count()})


def olvideContraseña(request):
    return render(request, 'olvideContraseña.html')


def correoEnviar(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = get_user_model().objects.filter(email=email).first()
        token_generator = PasswordResetTokenGenerator()
        if user:
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            mail_subject = 'Restablecer contraseña'
            message = render_to_string('restablecerContraseña.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, '', 'eduplus720@gmail.com', [email],
                      html_message=message)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (
            TypeError, ValueError, OverflowError,
            get_user_model().DoesNotExist):
        user = None

    token_generator = PasswordResetTokenGenerator()
    if user is not None and token_generator.check_token(user, token):
        # El token es válido, mostrar el formulario de restablecimiento de contraseña
        return render(request, 'nuevaContraseña.html', {'validlink': True, 'uid':
            uidb64, 'token': token})
    else:
        # El token no es válido, mostrar un mensaje de error
        return render(request, 'nuevaContraseña.html', {'validlink': False})


def change_password(request, uidb64):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password != confirm_password:
            return HttpResponse('Las contraseñas no coinciden', status=400)

        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)

        # Verifica que la nueva contraseña no sea la misma que la antigua
        if check_password(new_password, user.password):
            return HttpResponse('La nueva contraseña no puede ser la misma que la antigua', status=400)

        user.password = make_password(new_password)
        user.save()

        return redirect('index')

    return HttpResponse('Método no permitido', status=405)


@csrf_exempt
def check_same_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        uidb64 = request.POST.get('uidb64')

        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)

        if check_password(new_password, user.password):
            return JsonResponse({'same_password': True})
        else:
            return JsonResponse({'same_password': False})

    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
@login_required
def obtener_datos_usuario(request):
    # Obtener el estudiante actual
    estudiante = request.user.student

    # Verificar si el estudiante existe
    if estudiante:
        data = {
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'fecha_nacimiento': estudiante.birthdate.strftime('%Y-%m-%d')
        }
        print(data)  # Debugging para verificar los datos antes de enviar la respuesta
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No se pudo obtener los datos del estudiante'}, status=400)


@login_required
def obtener_datos_instructor(request):
    instructor = request.user.instructor

    if instructor:
        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_of_birth': instructor.birthdate.strftime('%Y-%m-%d'),
            'specialization': instructor.specialization  # Ajusta este campo según tu modelo de usuario
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No se pudo obtener los datos del instructor'}, status=400)


@login_required
def updateEstudiante(request):
    if request.method == 'POST':
        # Obtener el usuario y estudiante actual
        user = request.user
        estudiante = user.student

        # Actualizar los datos del usuario y estudiante
        user.first_name = request.POST['nombre']
        user.last_name = request.POST['apellido']
        user.save()
        fecha_nacimiento_str = request.POST['fecha_nacimiento']

        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            estudiante.birthdate = fecha_nacimiento
            estudiante.save()
        except ValueError:
            print(f"Error: La fecha {fecha_nacimiento_str} no está en el formato correcto 'YYYY-MM-DD'")

        # Agregar mensaje de éxito
        messages.success(request, '¡Los cambios se guardaron correctamente!')

        # Redirigir al usuario a la página que desees
        return redirect('indexLog')
    else:
        # Devolver una respuesta HTTP con un código de estado 405 (Método no permitido)
        return HttpResponseNotAllowed(['POST'])


@login_required
def updateInstructor(request):
    if request.method == 'POST':
        # Obtener el usuario y el instructor actual asociado a ese usuario
        user = request.user
        instructor = user.instructor

        # Actualizar los datos del usuario e instructor con los datos del formulario
        user.first_name = request.POST.get('firstName', '')
        user.last_name = request.POST.get('lastName', '')
        user.save()

        # Convertir la fecha de nacimiento a formato de fecha
        fecha_nacimiento_str = request.POST.get('dob', '')
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            instructor.birthdate = fecha_nacimiento
            instructor.save()  # Guardar el objeto instructor después de cambiar la fecha de nacimiento
        except ValueError:
            print(f"Error: La fecha {fecha_nacimiento_str} no está en el formato correcto 'YYYY-MM-DD'")

        # Actualizar la especialización del instructor
        instructor.specialization = request.POST.get('specialization', '')
        instructor.save()
        # Agregar mensaje de éxito utilizando el framework de mensajes de Django
        messages.success(request, '¡Los cambios se guardaron correctamente!')

        # Redirigir al usuario a la página deseada
        return redirect('indexLog')
    else:
        # Devolver una respuesta HTTP con un código de estado 405 (Método no permitido)
        return HttpResponseNotAllowed(['POST'])