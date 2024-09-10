import requests
from bs4 import BeautifulSoup
import os
import openpyxl
import json
import time
from datetime import datetime
import random

# Función para iniciar sesión y obtener una sesión autenticada
def login(username, password):
    login_url = 'https://www.lenceriario.com/login.php'
    payload = {
        'usuari': username,
        'passwd': password,
        'login': 's'
    }
    session = requests.Session()
    response = session.post(login_url, data=payload)
    
    if response.status_code == 200:
        print('Inicio de sesión exitoso')
        return session
    else:
        print('Error en el inicio de sesión')
        return None

# Función para obtener los URLs de productos de una página de listados
def fetch_product_urls(session, page):
    url = f'https://www.lenceriario.com/exclusive--brand--8--view--grilla-{page*20}'
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    product_containers = soup.find_all('div', class_='product')
    
    product_urls = []
    base_url = 'https://www.lenceriario.com/'
    
    for container in product_containers:
        product_link = container.find('a', href=True)
        if product_link:
            full_url = product_link['href']
            if not full_url.startswith('http'):
                full_url = base_url + full_url
            product_urls.append(full_url)
    
    return product_urls

# Función para extraer datos de un producto dado su URL
def fetch_product_data(session, product_url):
    try:
        response = session.get(product_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product = {
            'title': soup.find('title').text if soup.find('title') else 'N/A',
            'description': soup.find('meta', {'name': 'Description'})['content'] if soup.find('meta', {'name': 'Description'}) else 'N/A',
            'name': soup.find('meta', {'name': 'twitter:title'})['content'] if soup.find('meta', {'name': 'twitter:title'}) else 'N/A',
            'short_description': soup.find('meta', {'name': 'twitter:description'})['content'] if soup.find('meta', {'name': 'twitter:description'}) else 'N/A',
            'brand': soup.find('meta', {'name': 'product:brand'})['content'] if soup.find('meta', {'name': 'product:brand'}) else 'N/A',
            'price': soup.find('meta', {'name': 'product:price:amount'})['content'] if soup.find('meta', {'name': 'product:price:amount'}) else 'N/A',
            'availability': soup.find('meta', {'name': 'product:availability'})['content'] if soup.find('meta', {'name': 'product:availability'}) else 'N/A',
            'image_url': soup.find('meta', {'property': 'og:image'})['content'] if soup.find('meta', {'property': 'og:image'}) else 'N/A',
            'product_url': soup.find('meta', {'property': 'og:url'})['content'] if soup.find('meta', {'property': 'og:url'}) else product_url
        }
        
        # Extraer talles y colores
        sizes = []
        colors = []

        # Buscar el elemento de selección de talles y extraer los valores
        talle_select = soup.find('select', id='lista-talles')
        if talle_select:
            sizes = [option.text.strip() for option in talle_select.find_all('option')]

        # Buscar el elemento de selección de colores y extraer los valores
        color_select = soup.find('select', id='lista-colores')
        if color_select:
            colors = [option.text.strip() for option in color_select.find_all('option')]

        # Asignar los talles y colores al producto
        product['sizes'] = "; ".join(sizes)
        product['colors'] = "; ".join(colors)

        return product
    
    except Exception as e:
        print(f'Error extrayendo datos del producto {product_url}: {e}')
        return None

# Función para descargar una imagen desde una URL
def download_image(url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    response = requests.get(url)
    if response.status_code == 200:
        filename = os.path.join(folder, url.split('/')[-1])
        with open(filename, 'wb') as file:
            file.write(response.content)
        return url  # Devolver la URL completa en lugar del nombre del archivo
    return None

# Función para guardar productos en un archivo Excel con los datos originales
def save_to_excel_original(products, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Products'

    # Definir los encabezados del archivo Excel original
    fieldnames = ['title', 'description', 'name', 'short_description', 'brand', 'price', 'availability', 'sizes', 'colors', 'image_url', 'product_url']
    sheet.append(fieldnames)

    # Escribir los datos en el archivo Excel original
    for product in products:
        row = [product.get(field, '') for field in fieldnames]
        sheet.append(row)

    workbook.save(filename)
    print(f"Datos guardados en {filename}")

# Función para guardar productos en un archivo Excel con las columnas modificadas
def save_to_excel_modified(products, filename):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Products'

    # Define los nuevos encabezados y sus campos correspondientes
    field_mapping = {
        'Nombre': 'title',
        'Stock': lambda product: random.randint(1, 8),  # Asignar aleatoriamente un stock entre 1 y 8
        'SKU': lambda product: f"{product['brand']}-{product['name'].replace(' ', '-')}",
        'Precio': lambda product: round((round((float(product['price']) + 1.21) * 2, 2) + 49.99) // 50 * 50, 2) if product['price'] != 'N/A' else 'N/A',
        'Precio oferta': '',
        'Nombre atributo 1': 'Talle',
        'Valor atributo 1': 'sizes',
        'Nombre atributo 2': 'Color',
        'Valor atributo 2': 'a disposición de stock',
        'Nombre atributo 3': '',
        'Valor atributo 3': '',
        'Categorías': lambda product: f"{product['short_description'].split()[0]}",
        'Peso': '0.15',
        'Alto': '15',
        'Ancho': '30',
        'Profundidad': '30',
        'Mostrar en tienda': 'Si',
        'Descripción': 'short_description'
    }
    sheet.append(list(field_mapping.keys()))

    # Escribir los datos en el archivo Excel modificado
    for product in products:
        row = [field_mapping[field](product) if callable(field_mapping[field]) else product.get(field_mapping[field], '') if field_mapping[field] in product else field_mapping[field] for field in field_mapping]
        sheet.append(row)

    workbook.save(filename)
    print(f"Datos guardados en {filename}")

# Función para leer los datos guardados previamente
def load_previous_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Función para guardar los datos actuales
def save_current_data(products, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

# Función principal para ejecutar el script
def main():
    username = 'aqui va tu mail'
    password = 'aqui va tu contraseña'

    session = login(username, password)
    if not session:
        return

    all_product_urls = []
    page = 1
    max_pages = 500

    while page <= max_pages:
        print(f'Procesando página de listados {page}...')
        product_urls = fetch_product_urls(session, page)
        
        if not product_urls:
            print(f'No se encontraron productos en la página {page}, terminando.')
            break
        
        all_product_urls.extend(product_urls)
        page += 1
        time.sleep(1)

    all_products = []

    for product_url in all_product_urls:
        print(f'Extrayendo datos del producto {product_url}...')
        product = fetch_product_data(session, product_url)
        
        if product:
            image_url = product.get('image_url')
            if image_url:
                product['image_url'] = download_image(image_url, 'images')
            all_products.append(product)
        time.sleep(1)

    # Comprobar si hay modificaciones
    timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
    current_data_file = 'current_products.json'
    previous_data_file = 'previous_products.json'
    previous_data = load_previous_data(previous_data_file)

    if all_products != previous_data:
        print('Se detectaron cambios en los datos del producto.')

        excel_file_original = f'products_original_{timestamp}.xlsx'
        excel_file_modified = f'tabla_empretienda_{timestamp}.xlsx'

        save_to_excel_original(all_products, excel_file_original)
        save_to_excel_modified(all_products, excel_file_modified)

        # Guardar los datos actuales como archivo JSON
        save_current_data(all_products, current_data_file)

if __name__ == "__main__":
    main()
