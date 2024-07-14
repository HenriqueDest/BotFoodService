import requests
from bs4 import BeautifulSoup
import sqlite3
import re


# Configurar o banco de dados e criar as tabelas, se não existirem
def setup_database():
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT,
        local TEXT,
        porcentagem TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS culinaria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT,
        tipo TEXT,
        porcentagem TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS aberturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT,
        title TEXT,
        maiores_aberturas TEXT,
        menores_aberturas TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS franquias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT,
        fechamento TEXT,
        vendas TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT,
        taxa_franquias TEXT,
        taxa_royalties TEXT
    )
    ''')

    conn.commit()
    conn.close()


setup_database()


# Função para extrair o HTML do site
def extract_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        return None


# Função de scraping para extrair dados do site Mercado e Consumo
def scrape_mercadoeconsumo():
    url = 'https://mercadoeconsumo.com.br/04/10/2023/foodservice/brasil-possui-16-milhao-de-estabelecimentos-ativos-no-foodservice/'
    soup = extract_html(url)

    if soup:
        title = soup.find('h1', class_='jeg_post_title').get_text(strip=True)

        maiores_aberturas = []
        menores_aberturas = []

        maiores_lista = soup.find('ol')
        for li in maiores_lista.find_all('li'):
            maiores_aberturas.append(li.get_text(strip=True))

        menores_lista = maiores_lista.find_next_sibling('ol')
        for li in menores_lista.find_all('li'):
            menores_aberturas.append(li.get_text(strip=True))

        store_aberturas_in_db('mercadoeconsumo', title, maiores_aberturas, menores_aberturas)


def store_aberturas_in_db(site, title, maiores_aberturas, menores_aberturas):
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO aberturas (site, title, maiores_aberturas, menores_aberturas)
    VALUES (?, ?, ?, ?)
    ''', (site, title, '; '.join(maiores_aberturas), '; '.join(menores_aberturas)))

    conn.commit()
    conn.close()


# Função de scraping para extrair dados do site E-commerce Brasil
def scrape_ecommercebrasil():
    url = 'https://www.ecommercebrasil.com.br/noticias/franquias-brasil-resultados-2023'
    soup = extract_html(url)

    if soup:
        paragraphs = soup.find_all('p')
        fechamento = None
        vendas = None

        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)
            if "Enquanto 5,9% das operações fecharam às portas" in text:
                fechamento = re.search(r'(\d+,\d+%) das operações fecharam às portas', text).group(1)
                vendas = re.search(r'(\d+,\d+%)', text.split('chegou a')[1]).group(1)
                break

        store_franquias_in_db(url, fechamento, vendas)


def store_franquias_in_db(site, fechamento, vendas):
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO franquias (site, fechamento, vendas)
    VALUES (?, ?, ?)
    ''', (site, fechamento, vendas))

    conn.commit()
    conn.close()


# Função de scraping para extrair dados do site Central do Franqueado
def scrape_centraldofranqueado():
    url = 'https://centraldofranqueado.com.br/franchising/taxa-de-franquia/'
    soup = extract_html(url)

    if soup:
        paragraphs = soup.find_all('p')
        taxa_franquias = None
        taxa_royalties = None

        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)
            if "R$10 mil" in text and "R$15 mil" in text:
                taxa_franquias = "R$10 mil a R$15 mil"
            if "4%" in text and "10%" in text:
                taxa_royalties = "4% a 10% do faturamento bruto"

        store_taxas_in_db(url, taxa_franquias, taxa_royalties)


def store_taxas_in_db(site, taxa_franquias, taxa_royalties):
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO taxas (site, taxa_franquias, taxa_royalties)
    VALUES (?, ?, ?)
    ''', (site, taxa_franquias, taxa_royalties))

    conn.commit()
    conn.close()


# Função de scraping para extrair dados do site Mapa das Franquias
def scrape_mapadasfranquias():
    url = 'https://mapadasfranquias.com.br/'
    soup = extract_html(url)

    if soup:
        div = soup.find('div', {'class': 'f-unidades-regioes', 'id': 'unidades'})
        if div:
            items = div.find_all('li')
            for item in items:
                percentage = item.find('span').get_text(strip=True)
                region = item.get_text(strip=True).replace(percentage, '').strip()
                store_locais_in_db(url, region, percentage)


# Função de scraping para extrair dados do site ABF
def scrape_abf():
    url = 'https://www.abf.com.br/franquias-de-food-service/'
    soup = extract_html(url)

    if soup:
        paragraphs = soup.find_all('p')
        locais = []
        culinarias = []

        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)
            if "A Pesquisa Setorial de Food Service 2022 apontou" in text:
                match_locais = re.search(
                    r'(\d+%) dos estabelecimentos estão na rua.*?(\d+%) em shoppings.*?(\d+%) em outros lugares', text)
                if match_locais:
                    locais.append(('rua', match_locais.group(1)))
                    locais.append(('shoppings', match_locais.group(2)))
                    locais.append(('outros lugares', match_locais.group(3)))

                match_culinarias = re.findall(r'(\w+)\s\((\d+%)\)', text)
                culinarias.extend(match_culinarias)

        for local, porcentagem in locais:
            store_locais_in_db(url, local, porcentagem)

        for tipo, porcentagem in culinarias:
            store_culinaria_in_db(url, tipo, porcentagem)


def store_locais_in_db(site, local, porcentagem):
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM locais WHERE site=? AND local=? AND porcentagem=?', (site, local, porcentagem))
    if cursor.fetchone() is None:
        cursor.execute('''
        INSERT INTO locais (site, local, porcentagem)
        VALUES (?, ?, ?)
        ''', (site, local, porcentagem))

    conn.commit()
    conn.close()


def store_culinaria_in_db(site, tipo, porcentagem):
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM culinaria WHERE site=? AND tipo=? AND porcentagem=?', (site, tipo, porcentagem))
    if cursor.fetchone() is None:
        cursor.execute('''
        INSERT INTO culinaria (site, tipo, porcentagem)
        VALUES (?, ?, ?)
        ''', (site, tipo, porcentagem))

    conn.commit()
    conn.close()


# Função para verificar os dados armazenados no banco de dados
def fetch_all_data(table):
    conn = sqlite3.connect('dados_franquias.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()


# Executar todas as etapas
setup_database()

# Executar os scrapers e armazenar os dados no banco de dados
scrape_mercadoeconsumo()
scrape_ecommercebrasil()
scrape_centraldofranqueado()
scrape_mapadasfranquias()
scrape_abf()

# Consultar os dados armazenados
print("Dados armazenados na tabela 'locais':")
fetch_all_data('locais')

print("Dados armazenados na tabela 'culinaria':")
fetch_all_data('culinaria')

print("Dados armazenados na tabela 'aberturas':")
fetch_all_data('aberturas')

print("Dados armazenados na tabela 'franquias':")
fetch_all_data('franquias')

print("Dados armazenados na tabela 'taxas':")
fetch_all_data('taxas')

print("Dados extraídos e armazenados com sucesso.")
