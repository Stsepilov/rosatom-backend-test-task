# API атом чата

## Задача
Разработать API атом чата, в котором пользователи могут общаться друг с другом в приватных каналах.

## Используемые технологии
FastAPI
SQLite3
Docker
Git

## Деплой проекта
1. Клонирование репозитория:<br>
   git clone https://github.com/Stsepilov/rosatom-backend-test-task.git
2. Перейти в папку проекта:<br>
   cd rosatom-backend-test-task
3. Запуск Docker Compose:<br>
   docker-compose up --build
4. Запуск unit-тестов для проверки всех методов API:<br>
   docker-compose exec web pytest
5. Создание тестовых данных с помощью скрипта:<br>
   docker-compose exec web python -m app.test_data
6. Доступ к приложению и документации:<br>
   Приложение: http://localhost:8000
   Документация по API: http://localhost:8000/docs
