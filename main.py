import json
import os
from datetime import datetime


class Book:
    def __init__(self, title, author, genre, year, description):
        self.title = title
        self.author = author
        self.genre = genre
        self.year = int(year) 
        self.description = description
        self.is_read = False  
        self.is_favorite = False 

    def to_dict(self):
        """Преобразует объект Book в словарь для сохранения в JSON."""
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "year": self.year,
            "description": self.description,
            "is_read": self.is_read,
            "is_favorite": self.is_favorite
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект Book из словаря, загруженного из JSON."""
        book = cls(data['title'], data['author'], data['genre'], data['year'], data['description'])
        book.is_read = data.get('is_read', False)
        book.is_favorite = data.get('is_favorite', False)
        return book

    def __str__(self):
        """Строковое представление книги для удобного вывода."""
        status = "Прочитана" if self.is_read else "Не прочитана"
        fav = " (Избранное)" if self.is_favorite else ""
        return f"'{self.title}' - {self.author} ({self.year}) - {status}{fav}"


class Library:
    """
    Класс для управления коллекцией книг.
    """
    def __init__(self, filename="library.json"):
        self.books = []
        self.filename = filename
        self.genres_popularity = []
        self.authors_popularity = []
        self.load_from_file()

    def add_book(self, book):
        """Добавляет книгу в библиотеку."""
        self.books.append(book)
        print(f"Книга '{book.title}' успешно добавлена в библиотеку.")
        self.save_to_file()

    def remove_book(self, title, author):
        """Удаляет книгу по названию и автору."""
        for i, book in enumerate(self.books):
            if book.title.lower() == title.lower() and book.author.lower() == author.lower():
                removed_book = self.books.pop(i)
                print(f"Книга '{removed_book.title}' успешно удалена из библиотеки.")
                self.save_to_file()
                return
        print("Книга не найдена.")

    def get_all_books(self):
        """Возвращает список всех книг."""
        return self.books

    def sort_books(self, by_field):
        """Сортирует список книг по заданному полю."""
        field_mapping = {
            'название': 'title',
            'автор': 'author',
            'год': 'year',
            'жанр': 'genre'
        }
        if by_field == 'название':
            attr_name = field_mapping[by_field] 
            self.books.sort(key=lambda book: getattr(book, attr_name))
            print(f"Список книг отсортирован по '{by_field}' (алфавиту).")

        elif by_field == 'год':
            attr_name = field_mapping[by_field]
            self.books.sort(key=lambda book: getattr(book, attr_name))
            print(f"Список книг отсортирован по '{by_field}' (по возрастанию).")

        elif by_field == 'жанр':
            self.books.sort(key=lambda book: (
                book.genre,
                book.title
            ))
            print(f"Список книг отсортирован по названию жанра, затем по названию книги.")

        elif by_field == 'автор':
            self.books.sort(key=lambda book: (
                book.author,
                book.title
            ))
            print(f"Список книг отсортирован по имени автора, затем по названию книги.")

        else:
            print("Некорректное поле для сортировки.")
            print("Доступные поля: 'название', 'автор', 'год', 'жанр'")


    def filter_books(self, field, value):
        """Фильтрует книги по одному заданному полю и значению."""
        filtered_list = self.books

        if field == 'genre':
            filtered_list = [book for book in filtered_list if book.genre.lower() == value.lower()]
        elif field == 'status':
            filtered_list = [book for book in filtered_list if book.is_read == value]
        elif field == 'author':
            filtered_list = [book for book in filtered_list if book.author.lower() == value.lower()]
        elif field == 'title':
            filtered_list = [book for book in filtered_list if book.title.lower() == value.lower()]
        elif field == 'year':
            if isinstance(value, int):
                filtered_list = [book for book in filtered_list if book.year == value]
            else:
                print(f"Ошибка: Год должен быть числом. Получено: {value}")
                return []
        else:
            print(f"Ошибка: Неподдерживаемое поле фильтрации: {field}")
            return []

        return filtered_list

    def search_books(self, query):
        """Ищет книги по названию, автору или описанию."""
        query_lower = query.lower()
        found_books = [
            book for book in self.books
            if query_lower in book.title.lower() or
               query_lower in book.author.lower() or
               query_lower in book.description.lower()
        ]
        return found_books

    def mark_as_read(self, title, author):
        """Отмечает книгу как прочитанную."""
        for book in self.books:
            if book.title.lower() == title.lower() and book.author.lower() == author.lower():
                book.is_read = True
                print(f"Статус книги '{book.title}' изменен на 'Прочитана'.")
                self.save_to_file()
                return
        print("Книга не найдена.")

    def toggle_favorite(self, title, author):
        """Добавляет/удаляет книгу из избранного и обновляет списки популярности."""
        for book in self.books:
            if book.title.lower() == title.lower() and book.author.lower() == author.lower():
                old_is_favorite_state = book.is_favorite
                book.is_favorite = not book.is_favorite
                action = "добавлена в" if book.is_favorite else "удалена из"
                print(f"Книга '{book.title}' {action} избранного.")

                if book.is_favorite and not old_is_favorite_state:
                    genre_found = False
                    for entry in self.genres_popularity:
                        if entry[0].lower() == book.genre.lower():
                            entry[1] += 1 
                            genre_found = True
                            break
                    if not genre_found:
                        self.genres_popularity.append([book.genre, 1])

                    author_found = False
                    for entry in self.authors_popularity:
                        if entry[0].lower() == book.author.lower(): 
                            entry[1] += 1
                            author_found = True
                            break
                    if not author_found:
                        self.authors_popularity.append([book.author, 1])

                elif not book.is_favorite and old_is_favorite_state:
                    for i, entry in enumerate(self.genres_popularity):
                        if entry[0].lower() == book.genre.lower():
                            entry[1] -= 1
                            if entry[1] <= 0:
                                self.genres_popularity.pop(i)
                            break

                    for i, entry in enumerate(self.authors_popularity):
                        if entry[0].lower() == book.author.lower():
                            entry[1] -= 1
                            if entry[1] <= 0:
                                self.authors_popularity.pop(i)
                            break

                self.save_to_file()
                return
        print("Книга не найдена.")

    def get_favorites(self):
        """Возвращает список избранных книг."""
        return [book for book in self.books if book.is_favorite]
    
    def get_recommendations(self, limit=3):
        """Возвращает список рекомендованных книг."""
        recommendations_with_score = []

        for book in self.books:
            if book.is_favorite:
                continue

            score = 0

            for genre_entry in self.genres_popularity:
                if genre_entry[0].lower() == book.genre.lower():
                    score += genre_entry[1]
                    break 

            for author_entry in self.authors_popularity:
                if author_entry[0].lower() == book.author.lower():
                    score += author_entry[1]
                    break

            recommendations_with_score.append((book, score))

        recommendations_with_score.sort(key=lambda x: x[1], reverse=True)
        recommended_books = [item[0] for item in recommendations_with_score[:limit]]
        
        return recommended_books

    def save_to_file(self):
        """Сохраняет список книг в файл JSON."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([book.to_dict() for book in self.books], f, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в '{self.filename}'.")

    def load_from_file(self):
        """Загружает список книг из файла JSON и пересчитывает списки популярности."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books = [Book.from_dict(item) for item in data]
                print(f"Данные загружены из '{self.filename}'.")
                self.genres_popularity = []
                self.authors_popularity = []

                for book in self.books:
                    if book.is_favorite:
                        genre_found = False
                        for entry in self.genres_popularity:
                            if entry[0].lower() == book.genre.lower():
                                entry[1] += 1
                                genre_found = True
                                break
                        if not genre_found:
                            self.genres_popularity.append([book.genre, 1])
                        author_found = False
                        for entry in self.authors_popularity:
                            if entry[0].lower() == book.author.lower():
                                entry[1] += 1
                                author_found = True
                                break
                        if not author_found:
                            self.authors_popularity.append([book.author, 1])

            except FileNotFoundError:
                print(f"Файл '{self.filename}' не найден. Будет создан новый список книг.")
            except json.JSONDecodeError:
                print(f"Ошибка чтения файла '{self.filename}'. Файл поврежден или пуст.")
        else:
            print(f"Файл '{self.filename}' не найден. Будет создан новый список книг.")


class App:
    """
    Класс, управляющий основным циклом приложения.
    """
    def __init__(self):
        self.library = Library()

    def display_menu(self):
        """Отображает главное меню."""
        print("\n--- T-Библиотека ---")
        print("1. Добавить книгу")
        print("2. Просмотреть все книги")
        print("3. Найти книгу")
        print("4. Отметить книгу как прочитанную")
        print("5. Добавить/удалить из избранного")
        print("6. Показать избранное")
        print("7. Сортировать книги")
        print("8. Фильтровать книги")
        print("9. Удалить книгу")
        print("10. Получить рекомендации")
        print("0. Выход")

    def run(self):
        """Запускает основной цикл приложения."""
        while True:
            self.display_menu()
            choice = input("Выберите действие (0-9): ").strip()

            if choice == '1':
                self.handle_add_book()
            elif choice == '2':
                self.handle_view_books(self.library.get_all_books())
            elif choice == '3':
                self.handle_search_books()
            elif choice == '4':
                self.handle_mark_read()
            elif choice == '5':
                self.handle_toggle_favorite()
            elif choice == '6':
                self.handle_view_favorites()
            elif choice == '7':
                self.handle_sort_books()
            elif choice == '8':
                self.handle_filter_books()
            elif choice == '9':
                self.handle_remove_book()
            elif choice == '10':
                self.handle_get_recommendations()    
            elif choice == '0':
                print("До свидания!")
                break
            else:
                print("Некорректный выбор. Пожалуйста, введите число от 0 до 9.")

    def handle_add_book(self):
        """Обрабатывает добавление новой книги."""
        print("\n--- Добавление новой книги ---")
        title = input("Введите название: ").strip()
        author = input("Введите автора: ").strip()
        genre = input("Введите жанр: ").strip()
        year = input("Введите год издания: ").strip()
        description = input("Введите краткое описание: ").strip()

        if title and author and year.isdigit(): 
            new_book = Book(title, author, genre, year, description)
            self.library.add_book(new_book)
        else:
            print("Ошибка: Название, автор и год (число) обязательны для заполнения.")

    def handle_view_books(self, books_to_show):
        """Обрабатывает отображение списка книг."""
        if not books_to_show:
            print("\nБиблиотека пуста или по запросу ничего не найдено.")
        else:
            print("\n--- Список книг ---")
            for book in books_to_show:
                print(book)

    def handle_search_books(self):
        """Обрабатывает поиск книг."""
        query = input("\nВведите поисковый запрос (автор/название/описание книги): ").strip()
        results = self.library.search_books(query)
        self.handle_view_books(results)

    def handle_mark_read(self):
        """Обрабатывает изменение статуса 'прочитано'."""
        title = input("\nВведите название книги: ").strip()
        author = input("Введите автора книги: ").strip()
        self.library.mark_as_read(title, author)

    def handle_toggle_favorite(self):
        """Обрабатывает добавление/удаление из избранного."""
        title = input("\nВведите название книги: ").strip()
        author = input("Введите автора книги: ").strip()
        self.library.toggle_favorite(title, author)

    def handle_view_favorites(self):
        """Обрабатывает отображение избранных книг."""
        favorites = self.library.get_favorites()
        print("\n--- Избранные книги ---")
        self.handle_view_books(favorites)

    def handle_get_recommendations(self):
        """Обрабатывает получение и отображение рекомендованных книг."""
        print("\n--- Рекомендованные книги ---")
        limit_input = input("Сколько рекомендаций показать? (по умолчанию 3): ").strip()
        try:
            limit = int(limit_input) if limit_input else 3
            if limit <= 0:
                print("Количество должно быть положительным.")
                return
        except ValueError:
            print("Некорректное значение. Используем 3.")
            limit = 3

        recommended_books = self.library.get_recommendations(limit=limit)

        if not recommended_books:
            print("Нет книг для рекомендации. Добавьте книги в избранное, чтобы получить рекомендации.")
            return

        print(f"\n--- Топ-{len(recommended_books)} рекомендованных книг ---")
        for i, book in enumerate(recommended_books, 1):
            print(f"{i}. {book.title} от {book.author} (Жанр: {book.genre})")

    def handle_sort_books(self):
        """Обрабатывает сортировку книг."""
        field = input("\nВыберете сортировку по (название/автор/год/жанр): ").strip().lower()
        self.library.sort_books(field)
        self.handle_view_books(self.library.get_all_books())

    def handle_filter_books(self):
        """Обрабатывает фильтрацию книг."""
        print("\n--- Фильтрация книг ---")
        filter_choice = input("Выберите фильтрацию (жанр/автор/название/год/статус): ").strip().lower()
        field_mapping = {
            'жанр': 'genre',
            'автор': 'author',
            'название': 'title',
            'год': 'year',
            'статус': 'status'
        }
        field = field_mapping.get(filter_choice) 
        value = None

        if field is None: 
            print("Некорректный выбор фильтра.")
            return
        if field in ['genre', 'author', 'title']:
            if field == 'genre':
                prompt_text = "Введите жанр:"
            elif field == 'author':
                prompt_text = "Введите автора:"
            elif field == 'title':
                prompt_text = "Введите название:"
            value = input(prompt_text).strip()

            if not value: 
                print("Значение не может быть пустым.")
                return

        elif field == 'year':
            year_str = input("Введите год издания: ").strip()
            if not year_str.isdigit(): 
                print("Год должен быть числом.")
                return
            value = int(year_str) 

        elif field == 'status':
            status_input = input("Введите статус (прочитано/непрочитано): ").strip().lower()
            if status_input in ['прочитано', 'read']:
                value = True
            elif status_input in ['непрочитано', 'unread']:
                value = False
            else:
                print("Некорректный статус. Используйте 'прочитано' или 'непрочитано'.")
                return
        filtered_books = self.library.filter_books(field, value)
        self.handle_view_books(filtered_books)

    def handle_remove_book(self):
        """Обрабатывает удаление книги."""
        title = input("\nВведите название книги для удаления: ").strip()
        author = input("Введите автора книги для удаления: ").strip()
        self.library.remove_book(title, author)


if __name__ == "__main__":
    app = App()
    app.run()