# Scraper de Productos de Lencería

Este script en Python se utiliza para extraer información de productos desde el sitio web de Lencería Ría. El script realiza las siguientes tareas:

1. Inicia sesión en el sitio web.
2. Obtiene URLs de productos desde una página de listados.
3. Extrae datos de cada producto.
4. Descarga imágenes de los productos.
5. Guarda la información en archivos Excel y JSON.
6. Compara los datos actuales con los datos guardados previamente y guarda los cambios si los hay.

## Requisitos

- Python 3.x
- Librerías Python:
  - `requests`
  - `beautifulsoup4`
  - `openpyxl`
  - `json`
  
Puedes instalar las librerías necesarias usando `pip`:

```bash
pip install requests beautifulsoup4 openpyxl



El script realizará las siguientes acciones:

Iniciará sesión en el sitio web.
Extraerá URLs de productos de las páginas especificadas.
Descargar imágenes de productos y guardarlas en una carpeta images.
Guardará los datos originales en un archivo Excel con el formato products_original_<timestamp>.xlsx.
Guardará los datos modificados en un archivo Excel con el formato tabla_empretienda_<timestamp>.xlsx.
Guardará los datos actuales en un archivo JSON llamado current_products.json.
Comparará los datos actuales con los datos guardados previamente en previous_products.json y actualizará el archivo si hay cambios.
Archivos Generados
products_original_<timestamp>.xlsx: Contiene los datos originales de los productos.
tabla_empretienda_<timestamp>.xlsx: Contiene los datos modificados de los productos.
current_products.json: Contiene los datos actuales en formato JSON.
previous_products.json: Contiene los datos guardados previamente en formato JSON (si existe).
Notas
Asegúrate de tener acceso a las URLs de login y productos. Si hay cambios en la estructura del sitio web, es posible que necesites ajustar los selectores de BeautifulSoup.
El script incluye una pausa de 1 segundo entre solicitudes para evitar sobrecargar el servidor.


Autor
Alberto Damian Garcia
