from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .decorators import group_required
from .models import Student, Instructor, Curso, Compra


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
                                 'Te has registrado exitosamente como instructor')
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


from django.http import JsonResponse


def añadir_al_carrito(request, curso_id):
    # Aquí va la lógica para añadir el curso al carrito
    # ...

    # Obtiene la lista de cursos en el carrito de la sesión
    cart = request.session.get('cart', [])

    # Verifica si el curso ya está en el carrito
    if curso_id in cart:
        # Si el curso ya está en el carrito, devuelve un error
        return JsonResponse(
            {'success': False, 'error': 'El curso ya está en el carrito'})

    # Si el curso no está en el carrito, lo agrega
    cart.append(curso_id)
    request.session['cart'] = cart

    # Incrementa 'cart_count' en la sesión
    request.session['cart_count'] = len(cart)

    # Y luego devuelves una respuesta JSON
    return JsonResponse(
        {'success': True, 'cart_count': request.session['cart_count']})


def compraCarrito(request):
    # Obtiene la lista de ID de cursos en el carrito de la sesión
    cart = request.session.get('cart', [])

    # Obtiene los cursos en el carrito de la base de datos
    cursos_en_carrito = Curso.objects.filter(id__in=cart)
    total = sum(curso.precio for curso in cursos_en_carrito)

    # Pasa los cursos en el carrito a la plantilla
    return render(request, 'compraCursosCarrito.html', {'cursos_en_carrito':
                                                            cursos_en_carrito,
                                                        'total': total})


@login_required
@group_required('Estudiantes', redirect_route='crearCursos')
@csrf_exempt
def procesar_pago_cursos(request):
    if request.method == 'POST':
        curso_ids = request.POST.getlist('curso_id')  # Obtiene una lista de ID de cursos
        estudiante_id = request.POST.get('estudiante_id')

        # Obtiene la lista de cursos en el carrito de la sesión
        cart = request.session.get('cart', [])

        for curso_id in curso_ids:
            if Compra.objects.filter(estudiante_id=estudiante_id, curso_id=curso_id).exists():
                return JsonResponse({'status': 'failed', 'message': 'Ya has comprado uno o más cursos'})

            # Si el pago es exitoso, crea una nueva instancia de Compra
            compra = Compra(estudiante_id=estudiante_id, curso_id=curso_id)
            compra.save()

            # Elimina el curso del carrito en la sesión
            if curso_id in cart:
                cart.remove(curso_id)

        # Guarda la lista de cursos actualizada en la sesión
        request.session['cart'] = cart
        request.session['cart_count'] = len(cart)

        messages.success(request, 'Pago procesado exitosamente')
        return redirect('cursosEstudiante')  # Redirige al usuario a la vista
        # de 'miscursos'
    else:
        return JsonResponse({'status': 'failed'})



@login_required
@csrf_exempt
def eliminar_curso_carrito(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')  # Obtiene el ID del curso de los datos POST

        # Obtiene la lista de cursos en el carrito de la sesión
        cart = request.session.get('cart', [])

        # Verifica si el curso está en el carrito
        if curso_id in cart:
            # Si el curso está en el carrito, lo elimina
            cart.remove(curso_id)

            # Guarda la lista de cursos actualizada en la sesión
            request.session['cart'] = cart
            request.session['cart_count'] = len(cart)

            return JsonResponse({'success': True, 'cart_count': request.session['cart_count']})
        else:
            return JsonResponse({'success': False, 'error': 'El curso no está en el carrito'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
