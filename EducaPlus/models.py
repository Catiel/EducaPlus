from django.db import models
from django.db import models
from django.contrib.auth.models import User


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
    nombre = models.CharField(max_length=255)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    descripcion = models.TextField(default="Sin descripción")
    nivel = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    categoria = models.CharField(max_length=255)
    duracion = models.IntegerField(default=0)  # Add this line

    def __str__(self):
        return self.nombre
# Create your models here.
