import time
import requests
import schedule
import os
from bs4 import BeautifulSoup

def get_book_data(book_url: str) -> dict:
    """
    Парсит данные о книге со страницы сайта Books to Scrape.
    
    Args:
        book_url (str): URL страницы книги.
        
    Returns:
        dict: Словарь с информацией о книге, включающий название, цену, рейтинг, 
              наличие, описание и дополнительные характеристики из таблицы.
    """

    try:
        response = requests.get(book_url, timeout=10)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Название
        title_element = soup.find('h1')
        title = title_element.text.strip() if title_element else 'Информация отсутствует'

        # Цена
        price_element = soup.find('p', class_='price_color')
        price = price_element.text.strip() if price_element else 'Информация отсутствует'
       
        # Рейтинг
        rating_element = soup.find('p', class_='star-rating')
        rating = 'Информация отсутствует'
        if rating_element:
            rating_classes = rating_element.get('class', [])
            rating_classes = [cls for cls in rating_classes if cls != 'star-rating']
            if rating_classes:
                rating = rating_classes[0].capitalize()

        # Наличие
        availability_element = soup.find('p', class_='instock availability')
        availability = 'Информация отсутствует'
        if availability_element:
            availability_text = availability_element.text.strip()
            availability = 'In stock' if 'In stock' in availability_text else 'Out of stock'

        # Описание
        description = 'Информация отсутствует'
        product_description = soup.find('div', id='product_description')
        if product_description:
            next_p = product_description.find_next('p')
            if next_p:
                description = next_p.text.strip()

        # Создание словаря с основной информацией о книге
        book_data = {
            'title': title,
            'price': price,
            'rating': rating,
            'availability': availability,
            'description': description,
        }

        # Обработка таблицы дополнительных характеристик и добавление их в словарь
        table = soup.find('table', class_='table table-striped')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                header_element = row.find('th')
                value_element = row.find('td')
                if header_element and value_element:
                    header = (
                        header_element.text.strip()
                        .lower()
                        .replace(' ', '_')
                        )
                    value = value_element.text.strip()
                    book_data[header] = value

        return book_data

    except requests.exceptions.HTTPError as e:
        print(f'HTTP ошибка для {book_url}: {e}')
        return {}
    except requests.exceptions.ConnectionError as e:
        print(f'Ошибка подключения к {book_url}: {e}')
        return {}
    except requests.exceptions.Timeout as e:
        print(f'Таймаут запроса к {book_url}: {e}')
        return {}
    except requests.exceptions.RequestException as e:
        print(f'Ошибка запроса к {book_url}: {e}')
        return {}
    except Exception as e:
        print(f'Неожиданная ошибка при обработке {book_url}: {e}')
        return {}

def scrape_books(is_save: bool = False) -> list:
    """
    Парсит книги со всех страниц сайта Books to Scrape.
    
    Args:
        is_save (bool): Если True, сохраняет данные в файл books_data.txt
        
    Returns:
        list: Список словарей с информацией о всех книгах
    """

    base_url = 'http://books.toscrape.com/catalogue/page-{}.html'
    page = 1
    list_books = []

    # Бесконечный цикл для обхода всех страниц
    while True:
        url = base_url.format(page)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            break
        except requests.exceptions.RequestException:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        if not books:
            break

        # Обрабатываем каждую книгу на текущей странице
        for book in books:
            link_tag = book.find('h3').find('a')
            if link_tag and link_tag.get('href'):
                link = link_tag['href']
                if link.startswith('../../../'):
                    book_url = link[9:]
                else:
                    book_url = link
                
                full_book_url = 'http://books.toscrape.com/catalogue/' + book_url
                book_data = get_book_data(full_book_url)
                if book_data:
                    list_books.append(book_data)

        # Проверяем наличие кнопки <next> для перехода на следующую страницу
        next_btn = soup.find('li', class_='next')
        if not next_btn:
            break
        page += 1

    # Если флаг сохранения установлен и есть данные для сохранения
    if is_save and list_books:
        try:
            file_path = 'D:/books_scraper/artifacts/books_data.txt'
            with open(file_path, 'w', encoding='utf-8') as f:
                for i, book in enumerate(list_books, 1):
                    book_text = f'Book №{i}\n'  
                    for key, value in book.items():
                        book_text += f'{key}: {value}\n'
                    f.write(book_text)
        except Exception as e:
            print(f'Ошибка при сохранении файла: {e}')

    return list_books 

def schedule_scrape_books() -> None:
    """
    Автоматически парсит книги со всех страниц сайта Books to Scrape.
    Расписание:
    - Основной запуск: ежедневно в 19:00
    - Дополнительный тест (для проверки работоспособности программы): 
      каждые 30 минут
    """
    # Настройка ежедневного автоматического парсинга в 19:00
    schedule.every().day.at('19:00').do(scrape_books, is_save=True)

    # Проверки выполнения запланированных задач (каждые 60 секунд)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_scrape_books()