# Ideas CrawlChat

## Descripción

Ideas CrawlChat es una aplicación diseñada para rastrear sitios web, extraer contenido y procesarlo utilizando modelos de lenguaje. La aplicación permite definir un conjunto de prompts que se aplicarán al contenido extraído para generar respuestas automatizadas.

## Características principales

- **Rastreo de sitios web**: Utiliza Playwright para navegar y extraer contenido de sitios web.
- **Procesamiento de contenido**: Aplica modelos de lenguaje a los contenidos extraídos para generar respuestas a los prompts definidos.
- **Interfaz gráfica**: Proporciona una interfaz gráfica para definir nuevos batches, ver resultados y gestionar el proceso de rastreo.
- **Persistencia de datos**: Utiliza SQLAlchemy para gestionar la base de datos y almacenar los resultados del rastreo y procesamiento.

## Dependencias

Para ejecutar este proyecto, necesitarás instalar las siguientes dependencias:

- **Python 3.8+**
- **SQLAlchemy/SQLLite**: ORM para gestionar la base de datos SqlLite.
- **Playwright**: Herramienta para la automatización de navegadores.
- **ttkbootstrap**: Biblioteca para mejorar la apariencia de la interfaz gráfica.
- **asyncio**: Biblioteca estándar de Python para programación asíncrona.

Puedes instalar las dependencias utilizando `pip`:

```sh
pip install sqlalchemy playwright ttkbootstrap asyncio
```

## Instalación y configuración

1. **Clonar el repositorio**:
    ```sh
    git clone https://github.com/tu_usuario/Ideas_CrawlChat.git
    cd Ideas_CrawlChat
    ```

2. **Instalar las dependencias**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Configurar Playwright**:
    ```sh
    playwright install
    ```

4. **Configurar la base de datos**:
    La base de datos se inicializa automáticamente al ejecutar la aplicación por primera vez.

## Uso

1. **Ejecutar la aplicación**:
    ```sh
    python src/mainApp.py
    ```

2. **Crear un nuevo batch**:
    - Abre la interfaz gráfica y define los parámetros del nuevo batch, incluyendo la URL inicial, la profundidad de rastreo, el número máximo de sitios y los prompts.

3. **Ver resultados**:
    - Utiliza la interfaz gráfica para ver los resultados del batch, incluyendo el contenido extraído y las respuestas generadas por los modelos de lenguaje.

## Crear un ejecutable con PyInstaller

Para crear un ejecutable de la aplicación, sigue estos pasos:

1. **Navega al directorio del proyecto**:
    ```sh
    cd /path/to/your/project
    ```

2. **Ejecuta PyInstaller**:
    ```sh
    pyinstaller CrawlerGPT.spec
    ```

    Esto generará un ejecutable en el directorio `dist`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor sigue estos pasos:

1. **Fork el repositorio**.
2. **Crea una nueva rama** (`git checkout -b feature/nueva-caracteristica`).
3. **Realiza tus cambios** y **haz commit** (`git commit -am 'Agregar nueva característica'`).
4. **Envía tus cambios** (`git push origin feature/nueva-caracteristica`).
5. **Abre un Pull Request**.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
