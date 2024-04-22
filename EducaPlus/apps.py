from django.apps import AppConfig


class EducaplusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "EducaPlus"


from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la página de recuperación de contraseña
@app.route('/forgot-password/')
def forgot_password():
    # Aquí puedes agregar cualquier lógica relacionada con la recuperación de contraseña
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(debug=True)

