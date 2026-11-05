# Usar una imagen base ligera de Python
FROM python:3.11-alpine

# Crear un usuario sin privilegios root para mayor seguridad
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar ciertas librerías de Python
RUN apk add --no-cache build-base

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY ./app ./app

# Cambiar la propiedad de los archivos al usuario no root
RUN chown -R appuser:appgroup /app

# Cambiar al usuario seguro
USER appuser

# Exponer el puerto interno (no se mapea al host, solo a Nginx)
EXPOSE 8000

# Comando para ejecutar FastAPI usando Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]