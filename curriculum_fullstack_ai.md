# Ruta de Aprendizaje: De Data Scientist a Full-Stack AI Engineer

Como Científico de Datos, ya dominas Python, manipulación de datos (Pandas) y lógica analítica. Para construir aplicaciones reales como **MarketSense**, necesitas dominar la **Ingeniería de Software** y la **Arquitectura Web**.

Esta es la ruta de evolución recomendada, estructurada desde las bases hasta la cima, mapeada exactamente a lo que creamos en este proyecto.

---

## Módulo 1: Fundamentos de Ingeniería y Estructura
*En Data Science trabajas en scripts o Notebooks planos. En Ingeniería, tu código debe estar estructurado y seguro.*

*   **Entornos Virtuales y Dependencias (`.venv`, `pyproject.toml`):** Aprender a aislar tu espacio de trabajo para que el código no colisione con otros proyectos en tu máquina.
*   **Gestión de Secretos (`.env`):** Por qué nunca debes escribir contraseñas (como las de AWS Dabase o Gemini) directamente en el código.
*   **Modularidad de Python:** Cómo separar el código en carpetas lógicas (ej: `backend/db/`, `backend/api/`) y unirlas usando archivos `__init__.py`.

## Módulo 2: Bases de Datos y ORMs (El Corazón de los Datos)
*Ya sabes hacer `SELECT * FROM`. Ahora debes hacerlo de forma estructurada en Python.*

*   **Cloud Databases (AWS RDS):** Entender cómo tu servidor local se conecta a una base de datos PostgreSQL alojada kilómetros de distancia en Amazon.
*   **SQLAlchemy (El Patrón ORM):** El concepto más importante. Aprenderás a mapear una tabla de Base de Datos convirtiéndola en una **Clase de Python**. En lugar de escribir sentencias SQL en texto, en MarketSense creamos el archivo `modelos.py` para interactuar con los datos usando puro código Python.
*   **Pydantic:** Validar rigurosamente que los datos que entran y salen del sistema tengan los tipos correctos (ej: asegurar que el precio sea siempre un *float*).

## Módulo 3: Creación de la API (El Puente de Comunicación)
*Tus modelos o datos no le sirven al usuario si no tiene cómo interactuar con ellos por internet. Necesitas construir una API.*

*   **Protocolo HTTP y REST:** Entender qué significa hacer un `GET` (pedir información) o un `POST` (enviar información, como el mensaje del chat).
*   **FastAPI:** El framework más rápido de Python. Con él expusimos todo tu pipeline financiero a internet. Aprenderás a crear "endpoints" (URLs o rutas) en `backend/api/main.py`.
*   **CORS:** Reglas de seguridad web que permiten que tu servidor Python (puerto 8000) acepte solicitudes de tu página web Next.js (puerto 3000).

## Módulo 4: Agentes de Inteligencia Artificial (El Cerebro)
*Ya sabes usar LLMs. Ahora vas a hacer que el LLM sea autónomo y ejecute acciones en la Base de Datos sin intervención humana.*

*   **Herramientas para LLMs (Tools Calling):** Cómo tomar una función normal de Python (como `calcular_cagr` o la herramienta SQL) y "explicársela" a Google Gemini para que sepa cómo ejecutarla.
*   **LangGraph (State Graphs):** El orquestador del nivel "Dios". Ya no es un simple chat (LangChain convencional). LangGraph permite crear ciclos "Pensar -> Usar Herramienta -> Observar -> Responder" (Arquitectura ReAct). Es lo que hicimos en `financial_analyst.py`.

## Módulo 5: RAG y VectorStores (Memoria Inteligente)
*El LLM de Inteligencia Artificial no sabe qué dijo la Reserva Federal ayer. Debemos inyectarle la información antes de que responda.*

*   **Embeddings:** Cómo convertir texto plano (ej: noticias de Apple) en vectores numéricos de cientos de dimensiones usando modelos de Google Bedrock/Gemini.
*   **Bases de Datos Vectoriales (FAISS):** Aprender cómo realizar búsquedas matemáticas de "similitud semántica" (Retriever) para encontrar noticias relacionadas rápidamente sin usar palabras clave exactas.

## Módulo 6: El Frontend (Lo que ve el Usuario) 
*(Opcional - Muchos Data Scientists se quedan en el Backend)*
*Si no le pones una "cara" bonita, la gente no usará tu algoritmo.*

*   **React y Next.js:** Aprender los fundamentos del renderizado en pantalla (estado `useState`, efectos secundarios `useEffect`).
*   **Consumo de APIs (Fetch API):** Cómo pedirle a Javascript que hable con tu servidor FastAPI en Python para inyectar los JSON en las tarjetas visuales.
*   **TailwindCSS:** Cómo darle márgenes, colores, efectos "modo oscuro" escribiendo clases.

---

### ¿Cómo abordaremos esto en nuestro "Coding Dojo"?

Como tu Tutor, mi meta es no abrumarte. Con el comando interactivo que diseñé (`/dojo quiz [tema]` o `/dojo reescribe [archivo]`), **podemos ir sección por sección**. 

No tienes que entender el Módulo 6 para dominar cómo conectar a AWS (Módulo 2). Iremos pelando esta cebolla gajo por gajo.
