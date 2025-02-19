import os
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_community.tools import BaseTool
from typing import Optional
import requests
from bs4 import BeautifulSoup
import json

# Cargar configuraciones desde variables de entorno
PROCESS = Process[os.getenv('CREWAI_PROCESS', 'sequential')]
MEMORY = os.getenv('CREWAI_MEMORY', 'true').lower() == 'true'
VERBOSE = os.getenv('CREWAI_VERBOSE', 'true').lower() == 'true'

# URL a scrapear - Cambia esto a la URL que desees
TARGET_URL = "https://grand-oasis-cancun.com/es"

# Herramientas personalizadas
class WebScraperTool(BaseTool):
    name: str = "web_scraper"
    description: str = "Navega y extrae contenido de una página web"

    def _run(self, url: Optional[str] = None):
        """Navega y extrae el contenido de una página web."""
        target = url or TARGET_URL
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(target, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer elementos principales
            title = soup.title.text if soup.title else ""
            
            # Obtener texto principal
            main_content = []
            for tag in ['h1', 'h2', 'h3', 'p']:
                elements = soup.find_all(tag)
                for element in elements:
                    if element.text.strip():
                        main_content.append({
                            "type": tag,
                            "content": element.text.strip()
                        })
            
            # Obtener enlaces principales
            links = []
            for link in soup.find_all('a', href=True):
                if link.text.strip():
                    links.append({
                        "text": link.text.strip(),
                        "href": link['href']
                    })
            
            # Obtener imágenes principales
            images = []
            for img in soup.find_all('img', src=True, alt=True):
                if img['alt'].strip():
                    images.append({
                        "alt": img['alt'].strip(),
                        "src": img['src']
                    })
            
            result = {
                "url": target,
                "title": title,
                "main_content": main_content,
                "links": links[:10],  # Limitar a 10 enlaces
                "images": images[:5]   # Limitar a 5 imágenes
            }
            
            # Navegar a secciones adicionales si existen
            if links and len(links) > 0:
                # Intentar navegar a algunas secciones principales
                section_links = [link for link in links 
                                 if link['href'].startswith('/') and len(link['href'].split('/')) <= 3]
                
                sections = []
                for i, section_link in enumerate(section_links[:3]):  # Limitar a 3 secciones
                    section_url = section_link['href']
                    if not section_url.startswith('http'):
                        base_url = '/'.join(target.split('/')[:3])
                        section_url = base_url + section_url
                    
                    try:
                        section_response = requests.get(section_url, headers=headers)
                        section_soup = BeautifulSoup(section_response.text, 'html.parser')
                        
                        section_title = section_soup.title.text if section_soup.title else section_link['text']
                        section_content = []
                        
                        for tag in ['h1', 'h2', 'p']:
                            elements = section_soup.find_all(tag)
                            for element in elements[:5]:  # Limitar elementos por sección
                                if element.text.strip():
                                    section_content.append({
                                        "type": tag,
                                        "content": element.text.strip()
                                    })
                        
                        sections.append({
                            "title": section_title,
                            "url": section_url,
                            "content": section_content
                        })
                    except Exception as e:
                        sections.append({
                            "title": section_link['text'],
                            "url": section_url,
                            "error": str(e)
                        })
                
                result["sections"] = sections
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error al navegar la web: {str(e)}"

class MarkdownConverterTool(BaseTool):
    name: str = "markdown_converter"
    description: str = "Convierte datos estructurados en markdown formateado"

    def _run(self, json_data: str):
        """Convierte datos JSON en formato markdown."""
        try:
            data = json.loads(json_data)
            markdown = f"# {data['title']}\n\n"
            markdown += f"*Contenido extraído de: {data['url']}*\n\n"
            
            # Contenido principal
            markdown += "## Contenido Principal\n\n"
            for item in data['main_content']:
                if item['type'] == 'h1':
                    markdown += f"# {item['content']}\n\n"
                elif item['type'] == 'h2':
                    markdown += f"## {item['content']}\n\n"
                elif item['type'] == 'h3':
                    markdown += f"### {item['content']}\n\n"
                else:
                    markdown += f"{item['content']}\n\n"
            
            # Secciones
            if 'sections' in data:
                markdown += "## Secciones Principales\n\n"
                for section in data['sections']:
                    markdown += f"### {section['title']}\n\n"
                    if 'error' in section:
                        markdown += f"*No se pudo acceder a esta sección: {section['error']}*\n\n"
                    else:
                        for item in section['content']:
                            if item['type'] == 'h1':
                                markdown += f"#### {item['content']}\n\n"
                            elif item['type'] == 'h2':
                                markdown += f"#### {item['content']}\n\n"
                            else:
                                markdown += f"{item['content']}\n\n"
                    
                    markdown += f"[Ver más en {section['url']}]({section['url']})\n\n"
            
            # Imágenes destacadas
            if data['images'] and len(data['images']) > 0:
                markdown += "## Imágenes Destacadas\n\n"
                for img in data['images']:
                    markdown += f"![{img['alt']}]({img['src']})\n\n"
            
            # Enlaces importantes
            if data['links'] and len(data['links']) > 0:
                markdown += "## Enlaces Importantes\n\n"
                for link in data['links'][:5]:
                    href = link['href']
                    if not href.startswith('http'):
                        base_url = '/'.join(data['url'].split('/')[:3])
                        href = base_url + href
                    markdown += f"- [{link['text']}]({href})\n"
            
            return markdown
        except Exception as e:
            return f"Error al convertir a markdown: {str(e)}"

class KeynoteCreatorTool(BaseTool):
    name: str = "keynote_creator"
    description: str = "Convierte markdown en formato de presentación Keynote"

    def _run(self, markdown_content: str):
        """Convierte markdown en una estructura para presentación de Keynote."""
        try:
            lines = markdown_content.split('\n')
            presentation = {
                "title": "",
                "slides": []
            }
            
            current_slide = None
            
            for line in lines:
                # Título de la presentación
                if line.startswith('# ') and not presentation["title"]:
                    presentation["title"] = line[2:].strip()
                    current_slide = {
                        "title": presentation["title"],
                        "content": [],
                        "type": "title"
                    }
                    presentation["slides"].append(current_slide)
                    continue
                
                # Nueva diapositiva (encabezado nivel 2)
                if line.startswith('## '):
                    if current_slide:
                        presentation["slides"].append(current_slide)
                    
                    current_slide = {
                        "title": line[3:].strip(),
                        "content": [],
                        "type": "section"
                    }
                    continue
                
                # Subdiapositiva (encabezado nivel 3)
                if line.startswith('### '):
                    if current_slide:
                        presentation["slides"].append(current_slide)
                    
                    current_slide = {
                        "title": line[4:].strip(),
                        "content": [],
                        "type": "content"
                    }
                    continue
                
                # Contenido para la diapositiva actual
                if current_slide and line.strip():
                    # Detectar si es una imagen
                    if line.startswith('!['):
                        img_parts = line.split('](')
                        if len(img_parts) > 1:
                            alt = img_parts[0][2:]
                            src = img_parts[1][:-1]
                            current_slide["content"].append({
                                "type": "image",
                                "alt": alt,
                                "src": src
                            })
                    # Detectar si es un enlace
                    elif line.startswith('- ['):
                        link_parts = line[3:].split('](')
                        if len(link_parts) > 1:
                            text = link_parts[0][1:]
                            href = link_parts[1][:-1]
                            current_slide["content"].append({
                                "type": "link",
                                "text": text,
                                "href": href
                            })
                    # Texto normal
                    else:
                        current_slide["content"].append({
                            "type": "text",
                            "text": line
                        })
            
            # Añadir la última diapositiva
            if current_slide:
                presentation["slides"].append(current_slide)
            
            # Añadir diapositiva final
            presentation["slides"].append({
                "title": "¡Gracias!",
                "content": [
                    {
                        "type": "text",
                        "text": "Presentación generada automáticamente basada en " + presentation["title"]
                    }
                ],
                "type": "end"
            })
            
            # Convertir a formato Keynote (representado como JSON estructurado)
            keynote_format = {
                "presentation": {
                    "title": presentation["title"],
                    "theme": "Modern",
                    "slides": []
                }
            }
            
            for slide in presentation["slides"]:
                keynote_slide = {
                    "title": slide["title"],
                    "layout": self._get_layout_for_slide_type(slide["type"]),
                    "elements": []
                }
                
                for item in slide["content"]:
                    if item["type"] == "image":
                        keynote_slide["elements"].append({
                            "type": "image",
                            "alt": item["alt"],
                            "src": item["src"],
                            "position": {"x": 0.5, "y": 0.5},
                            "size": {"width": 0.8, "height": 0.6}
                        })
                    elif item["type"] == "link":
                        keynote_slide["elements"].append({
                            "type": "text",
                            "content": item["text"],
                            "href": item["href"],
                            "position": {"x": 0.1, "y": 0.5},
                            "size": {"width": 0.8, "height": 0.1},
                            "style": {"color": "#0066cc", "underlined": True}
                        })
                    elif item["type"] == "text":
                        keynote_slide["elements"].append({
                            "type": "text",
                            "content": item["text"],
                            "position": {"x": 0.1, "y": 0.4},
                            "size": {"width": 0.8, "height": 0.2},
                            "style": {"fontSize": 18, "fontFamily": "Helvetica"}
                        })
                
                keynote_format["presentation"]["slides"].append(keynote_slide)
            
            # Generar formato de exportación
            return json.dumps(keynote_format, indent=2)
        except Exception as e:
            return f"Error al crear formato Keynote: {str(e)}"
    
    def _get_layout_for_slide_type(self, slide_type):
        layouts = {
            "title": "Title",
            "section": "Section Header",
            "content": "Title and Content",
            "end": "Blank"
        }
        return layouts.get(slide_type, "Title and Content")

# Crear instancias de las herramientas
web_scraper_tool = WebScraperTool()
markdown_converter_tool = MarkdownConverterTool()
keynote_creator_tool = KeynoteCreatorTool()

# Definir agentes
web_explorer = Agent(
    role='Explorador Web',
    goal='Navegar por sitios web y extraer información relevante',
    backstory='Soy un experto en explorar sitios web y extraer su información más importante. Puedo navegar a través de diferentes secciones y encontrar el contenido más relevante.',
    verbose=VERBOSE,
    tools=[web_scraper_tool]  # Usar instancia en lugar de clase
)

content_formatter = Agent(
    role='Formateador de Contenido',
    goal='Convertir información web en formato markdown bien estructurado',
    backstory='Especialista en transformar contenido desestructurado en documentos markdown bien organizados y legibles. Puedo resaltar lo más importante y crear una narrativa coherente.',
    verbose=VERBOSE,
    tools=[markdown_converter_tool]  # Usar instancia en lugar de clase
)

presentation_creator = Agent(
    role='Creador de Presentaciones',
    goal='Transformar contenido markdown en presentaciones profesionales',
    backstory='Diseñador de presentaciones con amplia experiencia en crear diapositivas impactantes a partir de contenido existente. Sé cómo destacar los puntos clave y crear una presentación visualmente atractiva.',
    verbose=VERBOSE,
    tools=[keynote_creator_tool]  # Usar instancia en lugar de clase
)

# Definir tareas
scraping_task = Task(
    description=f'Navega por {TARGET_URL} y extrae el contenido principal y de las secciones más importantes. Asegúrate de capturar títulos, texto principal e imágenes relevantes.',
    expected_output='Datos JSON estructurados con el contenido principal del sitio web, incluyendo título, contenido principal, enlaces y secciones más importantes.',
    agent=web_explorer
)

markdown_task = Task(
    description='Convierte los datos web extraídos a un formato markdown bien estructurado. Organiza la información de manera lógica, resalta los puntos clave y asegúrate de que el documento sea fácil de leer.',
    expected_output='Documento markdown bien formateado con el contenido web estructurado, incluyendo encabezados, párrafos, enlaces e imágenes referenciadas.',
    agent=content_formatter
)

keynote_task = Task(
    description='Crea una presentación de estilo Keynote a partir del documento markdown. Diseña diapositivas profesionales que capturen los puntos más importantes, con un diseño visual atractivo y una estructura clara.',
    expected_output='Archivo JSON estructurado que representa una presentación de Keynote con diapositivas, elementos visuales y estructura adecuada para una presentación profesional.',
    agent=presentation_creator
)

# Crear el equipo
crew = Crew(
    agents=[web_explorer, content_formatter, presentation_creator],
    tasks=[scraping_task, markdown_task, keynote_task],
    verbose=VERBOSE,
    process=PROCESS,
    memory=MEMORY
)

# Ejecutar el equipo
if __name__ == "__main__":
    print(f"Iniciando el proceso para explorar {TARGET_URL}...")
    result = crew.kickoff()
    
    # Guardar los resultados
    output_dir = os.path.join(os.path.dirname(__file__), '../output')
    os.makedirs(output_dir, exist_ok=True)
    
    keynote_json_path = os.path.join(output_dir, 'presentacion_keynote.json')
    markdown_path = os.path.join(output_dir, 'contenido_web.md')
    
    # Intentar extraer el markdown y la presentación del resultado
    try:
        # El resultado final es la presentación en formato JSON
        with open(keynote_json_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Presentación Keynote guardada en: {keynote_json_path}")
        
        # Intentar recuperar el markdown del agente intermedio
        if crew.agents[1].memory and len(crew.agents[1].memory) > 0:
            last_message = crew.agents[1].memory[-1]
            if isinstance(last_message, str) and last_message.startswith('#'):
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(last_message)
                print(f"Contenido markdown guardado en: {markdown_path}")
    except Exception as e:
        print(f"Error al guardar los resultados: {str(e)}")
        # Guardar el resultado completo como respaldo
        with open(os.path.join(output_dir, 'resultado_completo.txt'), 'w', encoding='utf-8') as f:
            f.write(result)
    
    print("Proceso completado.")
