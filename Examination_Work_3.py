import requests
from bs4 import BeautifulSoup
import sqlite3


class BlogArticle:
    """Класс для представления статьи блога."""

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def to_dict(self):
        """Преобразует объект в словарь."""
        return {
            'title': self.title,
            'text': self.text
        }

    @classmethod
    def from_dict(cls, data):
        """Создаёт объект из словаря."""
        return cls(data['title'], data['text'])


class BlogParser:
    """Класс для парсинга блога."""

    def __init__(self, url):
        self.url = url

    def fetch_html(self):
        """Получает HTML-код страницы."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as ex:
            print(f"Ошибка при загрузке страницы: {ex}")
            return None

    def parse_articles(self, html):
        """Извлекает данные статей из HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        article_blocks = soup.find_all('div', class_='styles_cardBody__qP0jN')

        for block in article_blocks:
            title_tag = block.find('h1')
            text_tag = block.find('p')

            if title_tag and text_tag:
                title = title_tag.get_text(strip=True)
                text = text_tag.get_text(strip=True)
                articles.append(BlogArticle(title, text))

        return articles


class DatabaseManager:
    """Класс для работы с базой данных SQLite."""

    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        """Устанавливает соединение с базой данных."""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        """Создаёт таблицу articles, если она не существует."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                text TEXT
            )
        ''')
        self.connection.commit()

    def save_article(self, article):
        """Сохраняет статью в базу данных."""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO articles (title, text) VALUES (?, ?)
            ''', (article.title, article.text))
            self.connection.commit()
        except sqlite3.Error as ex:
            print(f"Ошибка при сохранении статьи: {ex}")

    def count_saved_articles(self):
        """Подсчитывает количество сохранённых статей."""
        self.cursor.execute('SELECT COUNT(*) FROM articles')
        return self.cursor.fetchone()[0]

    def get_last_five_articles(self):
        """Возвращает последние 5 добавленных статей."""
        self.cursor.execute('SELECT title, text FROM articles ORDER BY id DESC LIMIT 5')
        return self.cursor.fetchall()

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.connection:
            self.connection.close()


def main():
    # URL блога
    blog_url = "https://msk.top-academy.ru/blog"

    # Создание парсера
    parser = BlogParser(blog_url)

    # Загрузка HTML-кода
    print("Парсинг страницы https://msk.top-academy.ru/blog...")
    html = parser.fetch_html()
    if not html:
        print("Не удалось загрузить страницу.")
        return

    # Извлечение данных статей
    articles = parser.parse_articles(html)
    if not articles:
        print("Нет статей для обработки.")
        return

    print(f"Найдено {len(articles)} статей.")

    # Сохранение данных в базу данных
    db_manager = DatabaseManager("top_academy_blog.db")
    db_manager.connect()
    db_manager.create_table()

    print("Сохранение данных в базу данных...")
    for article in articles:
        db_manager.save_article(article)

    saved_count = db_manager.count_saved_articles()
    print(f"Успешно сохранено {saved_count} статей в top_academy_blog.db.")

    # Вывод последних 5 статей
    print("\nПоследние 5 добавленных статей:")
    print("-" * 60)
    last_five_articles = db_manager.get_last_five_articles()
    for idx, (title, text) in enumerate(last_five_articles, start=1):
        print(f"{idx}. Заголовок: \"{title}\"")
        print(f"   Текст: \"{text[:100]}...\"")
        print("-" * 60)

    # Закрытие базы данных
    db_manager.close()
    print("\nПарсинг завершен успешно. Все данные сохранены в базе.")


if __name__ == "__main__":
    main()