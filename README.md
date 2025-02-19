# Proyecto CrewAI

## Configuración de variables de entorno

1. Edita el archivo `.env` para añadir tus claves de API:
```
OPENAI_API_KEY=tu_clave_de_api_openai
ANTHROPIC_API_KEY=tu_clave_de_api_anthropic
```

Nota: Al menos una de estas claves de API es necesaria para que CrewAI funcione correctamente.

## Configuración y uso

### Construir y ejecutar con Docker

1. Construir la imagen:
```bash
cd ~/Desktop/crewai_project
docker-compose build
```

2. Iniciar el contenedor:
```bash
docker-compose up -d
```

3. Ejecutar los scripts disponibles:

   **Ejemplo básico:**
   ```bash
   docker-compose exec crewai python src/main.py
   ```

   **Web a Keynote:**
   ```bash
   docker-compose exec crewai python src/web_to_keynote.py
   ```

4. Para acceder al shell del contenedor:
```bash
docker-compose exec crewai bash
```

## Scripts disponibles

### 1. main.py
Ejemplo básico de CrewAI con dos agentes: un investigador y un escritor.

### 2. web_to_keynote.py
Flujo completo que:
1. Navega una web (por defecto apple.com) extrayendo su contenido
2. Convierte el contenido a markdown formateado
3. Genera una estructura para presentación tipo Keynote

Para cambiar la URL a explorar, modifica la variable `TARGET_URL` en el archivo.

Los resultados se guardan en la carpeta `output/`:
- `contenido_web.md`: Contenido en formato markdown
- `presentacion_keynote.json`: Estructura para presentación

### Utilización del CLI de CrewAI dentro del contenedor

Una vez dentro del contenedor, puedes utilizar los comandos de CrewAI:

```bash
python -m crewai create crew multiagentkeynote
```

### Notas adicionales

- Todos los archivos que crees o modifiques en la carpeta `~/Desktop/crewai_project` estarán disponibles dentro del contenedor en `/app`.
- Si necesitas instalar paquetes adicionales, agrégalos al archivo `requirements.txt` y reconstruye la imagen.
