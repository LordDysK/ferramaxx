FROM python:3.11-slim

# Instalar las dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo requirements.txt y instalar las dependencias
COPY requirements.txt .
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Establecer las variables de entorno necesarias
ENV DJANGO_SETTINGS_MODULE=appferra.settings
ENV PYTHONUNBUFFERED=1

# Ejecutar las migraciones y recolectar los archivos estáticos
RUN /opt/venv/bin/python manage.py migrate --noinput
RUN /opt/venv/bin/python manage.py collectstatic --noinput

# Exponer el puerto en el que Django va a ejecutarse
EXPOSE 8000

# Definir el comando por defecto para ejecutar la aplicación
CMD ["/opt/venv/bin/gunicorn", "--chdir", "appferra", "appferra.wsgi:application", "--bind", "0.0.0.0:8000"]
