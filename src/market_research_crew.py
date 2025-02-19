from crewai import Agent, Task, Crew, Process
try:
    from langchain.tools import tool
except ImportError:
    from crewai.tools import tool
import os
import json
from datetime import date

# Configuración desde variables de entorno
PROCESS = Process[os.getenv('CREWAI_PROCESS', 'sequential')]
MEMORY = os.getenv('CREWAI_MEMORY', 'true').lower() == 'true'
VERBOSE = os.getenv('CREWAI_VERBOSE', 'true').lower() == 'true'

# Herramientas personalizadas
@tool
def search_ai_agents(query: str) -> str:
    """Busca información sobre agentes de IA y empresas que los desarrollan."""
    # Implementar lógica real de búsqueda o integración con API
    return f"Resultados de búsqueda sobre agentes de IA: {query}"

@tool
def analyze_ai_trends(agent_type: str) -> str:
    """Analiza tendencias actuales en el mercado de agentes de IA por tipo."""
    # Implementar lógica de análisis
    return f"Análisis de tendencias para agentes de IA de tipo: {agent_type}"

@tool
def compare_agent_capabilities(agents_list: str) -> str:
    """Compara capacidades de diferentes agentes de IA."""
    # Implementar comparación
    return f"Comparación de capacidades entre: {agents_list}"

@tool
def generate_ai_market_charts(data: str) -> str:
    """Genera visualizaciones basadas en datos del mercado de IA."""
    # Implementar generación de gráficos
    return f"Gráficos del mercado de IA generados basados en: {data}"

# Definir agentes
investigador = Agent(
    role='Investigador de Tecnologías de IA',
    goal='Recopilar datos precisos sobre agentes de IA, sus desarrolladores, capacidades y modelos de negocio',
    backstory='Especialista en investigación tecnológica con amplia experiencia en el seguimiento de avances en inteligencia artificial y agentes autónomos.',
    verbose=VERBOSE,
    tools=[search_ai_agents, analyze_ai_trends]
)

analista = Agent(
    role='Analista de Mercado de IA',
    goal='Identificar patrones significativos y oportunidades en el mercado de agentes de IA',
    backstory='Analista con experiencia en evaluación de tecnologías emergentes y visualización de datos sobre adopción de IA.',
    verbose=VERBOSE,
    tools=[compare_agent_capabilities, generate_ai_market_charts]
)

estratega = Agent(
    role='Estratega de Tecnologías de IA',
    goal='Generar recomendaciones estratégicas para posicionamiento en el mercado de agentes de IA',
    backstory='Consultor tecnológico especializado en estrategias de implementación y monetización de sistemas de IA.',
    verbose=VERBOSE
)

redactor = Agent(
    role='Redactor Técnico especializado en IA',
    goal='Crear informes ejecutivos claros y persuasivos sobre tecnologías de agentes de IA',
    backstory='Comunicador técnico con experiencia traduciendo conceptos complejos de IA a lenguaje accesible para decisores empresariales.',
    verbose=VERBOSE
)

# Definir tareas
tarea_investigacion = Task(
    description='Investigar el mercado actual de agentes de IA. Identifica al menos 5 plataformas principales de agentes (como CrewAI, AutoGPT, LangChain, BabyAGI) y 3 tendencias emergentes en arquitecturas multiagente.',
    expected_output='Informe detallado sobre plataformas de agentes de IA (arquitectura, capacidades, precios, limitaciones) y análisis de tendencias con ejemplos de implementaciones.',
    agent=investigador
)

tarea_analisis = Task(
    description='Analizar los datos recopilados para identificar patrones de adopción, nichos de mercado y barreras técnicas en sistemas multiagente de IA.',
    expected_output='Análisis con visualizaciones que muestren comparativas de capacidades, casos de uso óptimos y métricas de rendimiento entre diferentes arquitecturas de agentes.',
    agent=analista,
    context=[tarea_investigacion]
)

tarea_estrategia = Task(
    description='Desarrollar recomendaciones estratégicas para implementación o desarrollo de sistemas multiagente basadas en el análisis de plataformas existentes.',
    expected_output='Lista priorizada de recomendaciones de arquitecturas según caso de uso, con justificación técnica, beneficios esperados y consideraciones de implementación.',
    agent=estratega,
    context=[tarea_analisis]
)

tarea_informe = Task(
    description='''
    Crear un informe ejecutivo final en formato Markdown que sintetice la investigación sobre agentes de IA, 
    análisis de plataformas y recomendaciones para implementación. Usa el siguiente esquema:
    
    # Investigación de Mercado: Agentes y Arquitecturas de IA
    ## Resumen Ejecutivo
    ## 1. Panorama Actual de Plataformas de Agentes IA
       * Comparativa de plataformas
       * Análisis de capacidades clave
       * Modelos de precios y licenciamiento
    ## 2. Tendencias Emergentes
       * Arquitecturas multiagente innovadoras
       * Casos de uso en crecimiento
       * Barreras y limitaciones técnicas
    ## 3. Análisis Comparativo
       * Métricas de rendimiento
       * Visualizaciones de capacidades
       * Nichos de mercado identificados
    ## 4. Recomendaciones Estratégicas
       * Por caso de uso empresarial
       * Consideraciones de implementación
       * Proyección de desarrollo futuro
    ## 5. Conclusiones
    ## Apéndice: Recursos Adicionales
    ''',
    expected_output='Informe ejecutivo técnico en Markdown, siguiendo la estructura especificada, con comparativa detallada de arquitecturas de agentes, visualizaciones referenciadas, y recomendaciones específicas para diferentes casos de uso.',
    agent=redactor,
    context=[tarea_investigacion, tarea_analisis, tarea_estrategia]
)

# Crear el equipo
crew_investigacion_ai = Crew(
    agents=[investigador, analista, estratega, redactor],
    tasks=[tarea_investigacion, tarea_analisis, tarea_estrategia, tarea_informe],
    verbose=VERBOSE,
    process=PROCESS,
    memory=MEMORY
)

# Ejecutar el equipo
if __name__ == "__main__":
    resultado_obj = crew_investigacion_ai.kickoff()
    
    # Extraer el resultado como texto
    try:
        # Para versiones recientes de CrewAI que devuelven CrewOutput
        if hasattr(resultado_obj, 'raw_output'):
            resultado = str(resultado_obj.raw_output)
        elif hasattr(resultado_obj, 'result'):
            resultado = str(resultado_obj.result)
        else:
            # Si es directamente una cadena
            resultado = str(resultado_obj)
    except Exception as e:
        print(f"Error al procesar el resultado: {e}")
        resultado = str(resultado_obj)
    
    print("\n\nRESULTADO FINAL DE LA INVESTIGACIÓN DE MERCADO DE AGENTES DE IA:")
    print(resultado)
    
    # Guardar el resultado en un archivo markdown
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'informe_agentes_ia.md')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resultado)
        print(f"\nInforme guardado exitosamente en: {file_path}")
    except Exception as e:
        print(f"Error al guardar el informe: {e}")
        
    # Crear una versión simple HTML sin dependencias adicionales
    try:
        html_path = os.path.join(os.path.dirname(__file__), 'informe_agentes_ia.html')
        # Crear contenido HTML simple
        html_content = resultado.replace('\n', '<br/>')
        html_content = html_content.replace('# ', '<h1>')
        html_content = html_content.replace('## ', '<h2>')
        html_content = html_content.replace('### ', '<h3>')
        html_content = html_content.replace('* ', '<li>')
        
        simple_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Investigación de Mercado: Agentes y Arquitecturas de IA</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ color: #3498db; margin-top: 30px; }}
        h3 {{ color: #2980b9; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        pre {{ background: #f4f4f4; padding: 15px; overflow: auto; border-radius: 3px; }}
        blockquote {{ background: #f9f9f9; border-left: 10px solid #ccc; margin: 1.5em 10px; padding: 1em 10px; }}
        img {{ max-width: 100%; height: auto; }}
        strong {{ font-weight: bold; }}
        em {{ font-style: italic; }}
        li {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>'''
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(simple_html)
        print(f"Versión HTML simple guardada en: {html_path}")
    except Exception as e:
        print(f"Error al generar versión HTML: {e}")
        
    # También guardar una versión JSON para fácil procesamiento
    try:
        # Crear una estructura básica para JSON
        sections = {
            "title": "Investigación de Mercado: Agentes y Arquitecturas de IA",
            "content": resultado,
            "date": str(date.today()),
            "sections": {}
        }
            
        # Dividir el texto por líneas y buscar secciones con ##
        lines = resultado.split('\n')
        current_section = ""
        section_content = []
        
        for line in lines:
            if line.startswith('## '):
                # Si ya estábamos en una sección, guardarla
                if current_section and section_content:
                    sections["sections"][current_section] = "\n".join(section_content)
                
                # Nueva sección
                current_section = line.replace('## ', '').strip()
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Guardar la última sección
        if current_section and section_content:
            sections["sections"][current_section] = "\n".join(section_content)
            
        # Guardar JSON
        json_path = os.path.join(os.path.dirname(__file__), 'informe_agentes_ia.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)
        print(f"Versión JSON guardada en: {json_path}")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
