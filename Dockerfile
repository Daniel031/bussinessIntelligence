# Usar la imagen oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos en el contenedor
COPY requirements.txt requirements.txt

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación en el contenedor
COPY . .

# Exponer el puerto en el que correrá la aplicación Flask
EXPOSE 5000

# Comando para ejecutar los seeders y luego iniciar la aplicación
CMD ["sh", "-c", "python load_data.py && python app.py"]
