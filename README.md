# UGC Опросы

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Сайт: `http://127.0.0.1:8000/`

Админка: `http://127.0.0.1:8000/admin/`

## Тестовые данные

```powershell
python manage.py seed_demo
```

## Тесты

```powershell
python manage.py test
```

## Docker

```powershell
docker compose up --build
```
