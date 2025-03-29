
import logging
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(filename='user_registration.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def register_user(username):
    if not username or not username.isalpha():
        logging.error("Ошибка: Имя пользователя не предоставлено.")
        return "Ошибка: Имя пользователя не предоставлено."

    logging.info(f"Пользователь {username} успешно зарегистрирован.")

    next_registration_date = datetime.now() + timedelta(days=7)
    return f"Дата повторной регистрации: {next_registration_date.strftime('%Y-%m-%d')}"

class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, username):
        result = register_user(username)
        if "успешно зарегистрирован" in result:
            self.users.append(username)  # Добавляем пользователя в список
        return result

    def show_users(self):
        if not self.users:
            print("Список пользователей пуст.")
        else:
            print("Зарегистрированные пользователи:")
            for user in self.users:
                print(user)

def main():
    user_manager = UserManager()

    while True:
        try:
            command = input("""
            Меню программы для логирования событий
            1 - Создание нового пользователя.
            2 - Список зарегистрированных пользователей.
            3 - Выход из программы.
            Ваш выбор: """)

            if command == "1":
                username = input('Введите имя пользователя: ')
                print(user_manager.add_user(username))
            elif command == "2":
                user_manager.show_users()  # Выводим список пользователей
            elif command == "3":
                print("Программа завершена.")
                break
            else:
                print("Неизвестная команда. Попробуйте снова.")
        except KeyboardInterrupt:
            print("\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
