## EducaPlus




## Requisitos previos

Este proyecto requiere que tengas instalado Anaconda en tu sistema. Si no lo tienes, puedes descargarlo e instalarlo desde [aquí](https://www.anaconda.com/products/distribution).

## Instalación

Para instalar las dependencias del proyecto, sigue estos pasos:

1. Crea un nuevo entorno de Anaconda (opcional):

```bash
conda create --name myenv
conda activate myenv
```
2. Instala las dependencias de Python:
```bash
python -m pip install --upgrade pip
pip install django==4.2
pip install firebase_admin
python manage.py runserver
```