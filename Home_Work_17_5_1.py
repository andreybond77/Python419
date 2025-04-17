
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def fetch_currency_rate(date, currency_code):
    """
    Функция для получения курса валюты за конкретную дату.
    :param date: Дата в формате 'DD.MM.YYYY'
    :param currency_code: Код валюты (например, CNY, USD, EUR, AUD)
    :return: Словарь с данными о валюте или None при ошибке
    """
    url = f"https://www.cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To={date}"

    try:
        response = requests.get(url=url, timeout=20)  # Увеличенный таймаут
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'data'})

        if not table:
            print(f"Ошибка: Таблица с курсами валют не найдена для даты {date}.")
            return None

        rates = {}
        found_currency = False
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                code = cols[1].text.strip()
                if code == currency_code:
                    found_currency = True
                    try:
                        unit = int(cols[2].text.strip())
                        value = float(cols[4].text.replace(',', '.'))
                        rates[code] = {
                            'value': value,
                            'unit': unit,
                            'date': date
                        }
                    except ValueError:
                        print(f"Ошибка при обработке данных для валюты {code} на дату {date}.")
                        continue

        if not found_currency:
            print(f"Валюта {currency_code} не найдена для даты {date}.")
            return None

        return rates

    except requests.exceptions.RequestException as ex:
        print(f'Ошибка при запросе для даты {date}: {ex}')
        return None


def parse_currency_rates(start_date, end_date, currency_code):
    """
    Функция для получения курсов валют за указанный период.
    :param start_date: Начальная дата в формате 'YYYY-MM-DD'
    :param end_date: Конечная дата в формате 'YYYY-MM-DD'
    :param currency_code: Код валюты (например, CNY, USD, EUR, AUD)
    :return: Список словарей с данными о валюте
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        if start > end:
            print("Ошибка: Начальная дата не может быть позже конечной даты.")
            return []

    except ValueError:
        print("Ошибка: Неверный формат даты. Пожалуйста, используйте формат YYYY-MM-DD.")
        return []

    all_rates = []
    current_date = start

    while current_date <= end:
        date_str = current_date.strftime('%d.%m.%Y')
        rates = fetch_currency_rate(date_str, currency_code)
        if rates:
            all_rates.append(rates)
        current_date += timedelta(days=1)

    return all_rates


if __name__ == '__main__':
    # Ввод начальной даты
    start_date = input("Введите начальную дату (в формате YYYY-MM-DD): ").strip()

    # Ввод конечной даты
    end_date = input("Введите конечную дату (в формате YYYY-MM-DD): ").strip()

    # Ввод кода валюты
    currency_code = input("Введите код валюты (например, CNY, USD, EUR, AUD): ").strip().upper()

    # Получение курсов валют
    result = parse_currency_rates(start_date, end_date, currency_code)

    if result:
        print(f'\nАктуальные курсы валют {currency_code} за указанный период:')
        for rates in result:
            for code, data in rates.items():
                print(f'{data["date"]}: {data["value"]} RUB за {data["unit"]} {code}')
    else:
        print(f"Не удалось получить данные о курсах валют для {currency_code}.")






