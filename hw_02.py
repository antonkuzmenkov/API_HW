
# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов Superjob и HH. #Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы). Получившийся список должен #содержать в себе минимум:
#Наименование вакансии.
#Предлагаемую зарплату (отдельно минимальную, максимальную и валюту).
#Ссылку на саму вакансию.
#Сайт, откуда собрана вакансия. ### По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). #Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.



def_hh(vac):

    vac_date = []
    
    params = {
        'text': vacancy, \
        'search_field': 'name', \
        'items_on_page': '10', \
        'page': ''
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 YaBrowser/20.8.3.115 Yowser/2.5 Safari/537.36'
    }

    link = 'https://hh.ru/search/vacancy'
       
    html = requests.get(link, params=params, headers=headers)

     if html.ok:
        parsed_html = bs(html.text,'html.parser')
        
        page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            last_page = '1'
        else:
            last_page = int(page_block.find_all('a', {'class': 'HH-Pager-Control'})[-2].getText())
    
    for page in range(0, last_page):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)
        
        if html.ok:
            parsed_html = bs(html.text,'html.parser')
            
            vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
                                        .find_all('div', {'class': 'vacancy-serp-item'})
                
            for item in vacancy_items:
                vacancy_date.append(_parser_item_hh(item))
                
    return vac_date

def_item_hh(item):

    vac_date = {}
    
    # название вакансии
    vac_name = item.find('div', {'class': 'resume-search-item__name'}) \
                        .getText() \
                        .replace(u'\xa0', u' ')
    
    vac_date['vac_name'] = vac_name
    
    # название компании
    com_name = item.find('div', {'class': 'vacancy-serp-item__meta-info'}) \
                        .find('a') \
                        .getText()
    
    vac_date['com_name'] = com_name
            
    # зарплата
    sal = item.find('div', {'class': 'vacancy-serp-item__compensation'})
    if not sal:
        sal_min = None
        sal_max = None
        sal_currency = None
    else:
        sal = sal.getText() \
                        .replace(u'\xa0', u'')
        
        sal = re.split(r'\s|-', sal)
        
        if sal[0] == 'до':
            sal_min = None
            sal_max = int(sal[1])
        elif sal[0] == 'от':
            sal_min = int(sal[1])
            sal_max = None
        else:
            sal_min = int(sal[0])
            sal_max = int(sal[1])            
        
        sal_currency = sal[2]
        
    vac_date['sal_min'] = sal_min
    vac_date['sal_max'] = sal_max
    vac_date['sal_currency'] = sal_currency
    
    # ссылка
    is_ad = item.find('span', {'class': 'vacancy-serp-item__controls-item vacancy-serp-item__controls-item_last'}) \
                .getText()
    
    vaca_link = item.find('div', {'class': 'resume-search-item__name'}) \
                        .find('a')['href']
    
    if is_ad != 'Реклама':
        vacancy_link = vacancy_link.split('?')[0]
    
    vac_date['vac_link'] = vac_link 
    
    # сайт
    vac_date['site'] = 'hh.ru'
    
    return vac_date

def parser_vac(vac):
        
    vac_date = []
    vacancy_date.extend(_parser_hh(vac))
    
    pd = pd.DataFrame(vacancy_date)

    return pd