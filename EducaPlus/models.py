from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Curso(models.Model):
    nombre = models.CharField(max_length=70)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    descripcion = models.TextField(default="Sin descripción", max_length=1404)
    nivel = models.CharField(max_length=15)
    precio = models.DecimalField(max_digits=50, decimal_places=2)
    categoria = models.CharField(max_length=20)
    duracion = models.IntegerField(default=0)  # Add this line

    def __str__(self):
        return self.nombre


# Create your models here.


class Compra(models.Model):
    estudiante = models.ForeignKey(Student, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
