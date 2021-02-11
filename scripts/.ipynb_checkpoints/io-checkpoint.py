import requests
import pandas as pd
import datetime
import os
import shutil
from bs4 import BeautifulSoup
import math

from PyPDF2 import PdfFileMerger


def make_dir(fix_path, ano,mes,dia):
    if os.path.isdir(f'{fix_path}/{ano}'):
        pass
    else:
        os.mkdir(f'{fix_path}/{ano}')

    if os.path.isdir(f'{fix_path}/{ano}/{mes}'):
        pass
    else:
        os.mkdir(f'{fix_path}/{ano}/{mes}')

    if os.path.isdir(f'{fix_path}/{ano}/{mes}/{dia}'):
        pass
    else:
        os.mkdir(f'{fix_path}/{ano}/{mes}/{dia}')
        
        
def get_month_name(month):
    mes_dict = {
        '01':'Janeiro',
        '02':'Fevereiro',
        '03':'Marco',
        '04':'Abril',
        '05':'Maio',
        '06':'Junho',
        '07':'Julho',
        '08':'Agosto',
        '09':'Setembro',
        '10':'Outubro',
        '11':'Novembro',
        '12':'Dezembro',
    }
    
    return mes_dict[month]


def merge_pdf(fix_path,ano, mes_number, dia):          
    path = f'{fix_path}/{ano}/{mes_number}/{dia}'
    pages_dict = {}
    pages = os.listdir(path)
    pages = [page for page in pages if page.split('.')[1] == 'pdf']
    for page in pages:
         pages_dict[int(page.split('_')[1].split('.')[0])] = page

    page_values = list(pages_dict.keys())
    page_values.sort()

    merger = PdfFileMerger()
    for page in page_values:

        merger.append(f'{path}/{pages_dict[page]}')

    merger.write(f"{fix_path}/{ano}/{mes_number}/{ano}-{mes_number}-{dia}.pdf")
    merger.close()

    shutil.rmtree(path, ignore_errors=True)
    
    
def get_url_last_versions(poder,ano,mes,dia,pg):

    if pg < 10:
        url = f'http://diariooficial.imprensaoficial.com.br/doflash/prototipo/{ano}/{mes}/{dia}/{poder}/pdf/pg_000{pg}.pdf'
    elif (pg>=10) & (pg<100):
        url = f'http://diariooficial.imprensaoficial.com.br/doflash/prototipo/{ano}/{mes}/{dia}/{poder}/pdf/pg_00{pg}.pdf'
    elif (pg>=100) & (pg<1000):
        url = f'http://diariooficial.imprensaoficial.com.br/doflash/prototipo/{ano}/{mes}/{dia}/{poder}/pdf/pg_0{pg}.pdf'
    elif pg>=1000:
        url = f'http://diariooficial.imprensaoficial.com.br/doflash/prototipo/{ano}/{mes}/{dia}/{poder}/pdf/pg_{pg}.pdf'
        
    return url






####====>>>> GENERIC PAGES <<<<++++####

def generic_get_number_pages(r):
    
    soup = BeautifulSoup(r.content, 'html.parser')
    
    class_id = "page-link font-weight-bold"
    
    n_pages_id = soup.find_all("span", {"id": 'content_lblDocumentosEncontrados'})

    # if n_pages_id != []:
        
    #     number_of_pages_id = soup.find_all("a", {"class": class_id})
        
    #     if number_of_pages_id !=[]:
    #         number_pages = int(number_of_pages_id[0].get_text())
    #     else:
    #         number_pages = 1
            
            
    if n_pages_id != []:
        number_pages = int(math.ceil((int(n_pages_id[0].get_text()))/15 ))
        n_docs = int(n_pages_id[0].get_text())
    else:
        number_pages = -1
        n_docs = 0

    return(number_pages, n_docs)

def generic_get_the_page(url):
    s = requests.Session()
    r = s.post(url)
    Logincookies = r.cookies
    r = s.get(url,cookies=Logincookies)
    
    return r


def generic_get_page_keys(r,number_pages,gazete_parameters,gazete_id,ano,mes_number,mes_name,dia,poder,poder_options,fix_path,n_documents):
    gazete_parameters[gazete_id] = {}
    
    keys_list = []
    links_list = []
    
    for i in range(1,number_pages+1):
        keys_list_now = []
        search_page = i
        
        
        main_url = f"https://www.imprensaoficial.com.br/DO/BuscaDO2001Resultado_11_3.aspx?filtrotipopalavraschavesalvar=FE&filtrodatafimsalvar={ano}{mes_number}{dia}&filtroperiodo={dia}%2f{mes_number}%2f{ano}+a+{dia}%2f{mes_number}%2f{ano}&filtrocadernos={poder_options[poder].capitalize()}&filtropalavraschave=+&filtrodatainiciosalvar={ano}{mes_number}{dia}&xhitlist_vpc={search_page}&filtrocadernossalvar={poder}&filtrotodoscadernos=+"

        r = generic_get_the_page(main_url)

        soup = BeautifulSoup(r.content, 'html.parser')

        docs_id = 'text-decoration: none;'
        page_keys_html = soup.find_all("a", {"style": docs_id})
        
        # print(main_url)
        for page_key in page_keys_html:
            pg_key = "pag" + page_key.get('href').split('%2fpag')[1].split('&pagina')[0]
            keys_list.append(pg_key)
            keys_list_now.append(pg_key)
        
        keys_list_now = list(dict.fromkeys(keys_list_now))
        keys_list = list(dict.fromkeys(keys_list))

        for pg_key in keys_list_now:
            if poder == 'ex1':
                pg_link = f"https://www.imprensaoficial.com.br/DO/GatewayPDF.aspx?pagina=I&caderno=Executivo%20I&data={dia}/{mes_number}/{ano}&link=/{ano}/executivo%20secao%20i/{mes_name.lower()}/{dia}/{pg_key}"
            elif poder == 'ex2':
                pg_link = f"https://www.imprensaoficial.com.br/DO/GatewayPDF.aspx?pagina=I&caderno=Executivo%20II&data={dia}/{mes_number}/{ano}&link=/{ano}/executivo%20secao%20ii/{mes_name.lower()}/{dia}/{pg_key}"
            elif poder == 'ass':
                pg_link = f"https://www.imprensaoficial.com.br/DO/GatewayPDF.aspx?pagina=1&caderno=Legislativo&data={dia}/{mes_number}/{ano}&link=/{ano}/legislativo/{mes_name.lower()}/{dia}/{pg_key}"

            
            
            # print(pg_link)
            
            
            links_list.append(pg_link)


            #DOWNLOAD THE PAGE
            with open(f'{fix_path}/{ano}/{mes_number}/{dia}/{pg_key}', 'wb') as file:
                file.write(requests.get(pg_link, stream=True).content)


        gazete_parameters[gazete_id]['number_pages'] = len(links_list)
        gazete_parameters[gazete_id]['number_documents'] = n_documents
        gazete_parameters[gazete_id]['pages_links'] = links_list
        gazete_parameters[gazete_id]['pages_keys'] = keys_list
        
    return gazete_parameters


