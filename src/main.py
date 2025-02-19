import os
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# Cargar configuraciones desde variables de entorno
PROCESS = Process[os.getenv('CREWAI_PROCESS', 'sequential')]
MEMORY = os.getenv('CREWAI_MEMORY', 'true').lower() == 'true'
VERBOSE = os.getenv('CREWAI_VERBOSE', 'true').lower() == 'true'

# Definir agentes
researcher = Agent(
    role='Investigador',
    goal='Recopilar datos precisos y relevantes',
    backstory='Eres un investigador con experiencia en análisis de datos',
    verbose=True
)

writer = Agent(
    role='Escritor',
    goal='Crear presentaciones convincentes basadas en la investigación',
    backstory='Eres un escritor talentoso especializado en presentaciones',
    verbose=True
)

# Definir tareas
research_task = Task(
    description='Investigar el tema de agentes múltiples en IA',
    expected_output='Un informe detallado sobre agentes múltiples en IA, tendencias actuales y casos de uso',
    agent=researcher
)

write_task = Task(
    description='Crear una presentación basada en la investigación',
    expected_output='Una presentación convincente con introducción, puntos clave, ejemplos y conclusión',
    agent=writer
)

# Crear el equipo
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=VERBOSE,
    process=PROCESS,
    memory=MEMORY
)

# Ejecutar el equipo
result = crew.kickoff()
print(result)