
# SmartOmbor

**SmartOmbor — ko'p kompaniyali ombor va savdo boshqaruv tizimi.**

Django va Django REST Framework asosida ishlab chiqilgan web-ilova. Tizim mahsulotlar, ombor qoldiqlari, kirim-chiqim, buyurtmalar, savdo va hisobotlarni boshqarish imkonini beradi.

## Asosiy imkoniyatlar

- Ko'p kompaniyali (Multi-tenant) arxitektura.
- Foydalanuvchilarni ro'yxatdan o'tkazish va autentifikatsiya.
- JWT orqali API autentifikatsiyasi.
- Kompaniya va foydalanuvchi rollarini boshqarish.
- Mahsulot va kategoriyalarni boshqarish.
- Ombor kirim-chiqim amaliyotlari.
- Buyurtmalar yaratish, yakunlash va bekor qilish.
- Kam qolgan mahsulotlarni nazorat qilish.
- Savdo va foyda hisobotlari.
- Excel va PDF hisobot eksporti.
- Gmail orqali avtomatik email xabarnomalari.
- Celery orqali fon vazifalari.
- PostgreSQL ma'lumotlar bazasi.
- Redis va Celery integratsiyasi.
- Docker orqali konteynerlashtirish.
- GitHub Actions CI/CD.
- PostgreSQL Backup va Restore.

## Foydalanilgan texnologiyalar

| Texnologiya | Vazifasi |
|---|---|
| Python 3.11 | Dasturlash tili |
| Django | Backend framework |
| Django REST Framework | REST API |
| JWT / Djoser | Autentifikatsiya |
| PostgreSQL | Ma'lumotlar bazasi |
| Redis | Celery broker |
| Celery | Fon vazifalari |
| Gunicorn | WSGI server |
| Nginx | Reverse proxy |
| Docker | Konteynerlashtirish |
| GitHub Actions | CI/CD |
| GHCR | Docker image saqlash |

## Foydalanuvchi rollari

Tizimda foydalanuvchilar kompaniya a'zoligi va rollari asosida ishlaydi.

| Rol | Vazifasi |
|---|---|
| Rahbar | Kompaniya va hisobotlarni boshqarish |
| Omborchi | Mahsulotlar va ombor harakatlari |
| Sotuvchi | Buyurtmalar va savdo |

Kompaniyalar o'rtasidagi ma'lumotlar ajratilishi tizimning asosiy xavfsizlik talablaridan biridir.

## Loyiha arxitekturasi

```text
SmartOmbor
│
├── accounts/
├── companies/
├── products/
├── inventory/
├── sales/
├── reports/
├── api/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
│
├── nginx/
│   └── default.conf
│
├── scripts/
│   ├── backup_db.ps1
│   └── backup_db.sh
│
├── .github/
│   └── workflows/
│       ├── smartombor-ci.yml
│       └── deploy.yml
│
├── compose.yaml
├── compose.prod.yaml
├── Dockerfile
├── requirements.txt
├── .env.example
└── manage.py
```

## O'rnatish va ishga tushirish

### 1. Loyihani yuklab olish

```bash
git clone https://github.com/Shahzodbek097/SmartOmbor.git
cd SmartOmbor
```

### 2. Virtual muhit yaratish

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Kutubxonalarni o'rnatish

```bash
python -m pip install -r requirements.txt
```

### 4. Muhit sozlamalari

`.env.example` faylidan `.env` yarating va haqiqiy maxfiy qiymatlarni kiriting.

Quyidagi ma'lumotlar sozlanishi kerak:

- Django SECRET_KEY
- PostgreSQL ma'lumotlari
- Redis paroli
- Gmail SMTP sozlamalari
- Celery ulanish manzillari
- DEBUG va ALLOWED_HOSTS

`.env` faylini GitHub'ga yubormang.

### 5. Docker orqali ishga tushirish

Docker Desktop ishlayotgan bo'lishi kerak.

```bash
docker compose up -d --build
```

Konteynerlar holatini tekshirish:

```bash
docker compose ps
```

Loglarni ko'rish:

```bash
docker compose logs -f
```

Sayt:

http://127.0.0.1:8000/

## Production muhitini sinash

Production Compose konfiguratsiyasi:

```bash
docker compose \
  -f compose.yaml \
  -f compose.prod.yaml \
  up -d
```

Sayt Nginx orqali:

http://127.0.0.1:8080/

## API testlari

API testlarini bajarish:

```bash
docker compose exec web python manage.py test api -v 2
```

Django tekshiruvi:

```bash
docker compose exec web python manage.py check
```

## Celery

Celery Worker:

```bash
docker compose logs -f celery_worker
```

Celery Beat:

```bash
docker compose logs -f celery_beat
```

## Backup va Restore

PostgreSQL ma'lumotlarini zaxiralash va tiklash imkoniyati mavjud.

Windows backup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\backup_db.ps1
```

Linux server backup:

```bash
bash scripts/backup_db.sh
```

Backup fayllari maxfiy ma'lumotlarni o'z ichiga olishi mumkin. Ularni ochiq repository'ga joylamang.

## CI/CD

GitHub Actions yordamida:

1. Django tekshiruvlari va API testlari bajariladi.
2. PostgreSQL va Redis xizmatlari ishga tushiriladi.
3. Docker image yig'iladi.
4. Image GitHub Container Registry'ga yuboriladi.
5. Alohida CD workflow orqali VPS deployment bajarishga tayyorlangan.

Haqiqiy VPS deployment domen, server va SSH sozlamalari kiritilgandan keyin amalga oshiriladi.

## Xavfsizlik

- Maxfiy sozlamalar `.env` orqali boshqariladi.
- PostgreSQL va Redis tashqi portlarga ochilmaydi.
- Redis parol bilan himoyalangan.
- Django CSRF himoyasi yoqilgan.
- Kompaniyalararo ma'lumotlarga kirish nazorat qilinadi.
- Backup va Restore mexanizmi mavjud.

Production muhitida HTTPS va SSL sertifikati bilan ishlash rejalashtirilgan.

## Muallif

**Shahzod Abdusattorov**

Loyiha Python, Django va Django REST Framework bo'yicha amaliy bilimlarni mustahkamlash hamda real biznes jarayonlarini avtomatlashtirish maqsadida ishlab chiqilmoqda.

---

**SmartOmbor — Ombor va savdo boshqaruv tizimi.**

