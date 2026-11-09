# SmartOmbor — System Architecture

## 1. Umumiy arxitektura

```mermaid
flowchart TB
    U["Foydalanuvchi"] --> N["Nginx Reverse Proxy"]

    N -->|HTTP so'rovlar| G["Gunicorn"]
    G --> D["Django + DRF"]

    N -->|Static va Media| F["Static / Media Volumes"]

    subgraph Application["Django Application"]
        D --> A["Accounts"]
        D --> C["Companies"]
        D --> P["Products"]
        D --> I["Inventory"]
        D --> S["Sales"]
        D --> R["Reports"]
        D --> API["REST API"]
    end

    A --> DB["PostgreSQL"]
    C --> DB
    P --> DB
    I --> DB
    S --> DB
    R --> DB

    D --> RD["Redis"]
    RD --> CW["Celery Worker"]
    CB["Celery Beat"] --> RD
    CW --> DB
    CW --> GM["Gmail SMTP"]
```

## 2. CI/CD arxitekturasi

```mermaid
flowchart LR
    DEV["Developer"] --> GH["GitHub Repository"]
    GH --> CI["GitHub Actions CI"]
    CI --> TEST["Django Tests"]
    TEST --> BUILD["Docker Build"]
    BUILD --> REG["GitHub Container Registry"]
    REG --> VPS["Production VPS"]
    VPS --> NG["Nginx"]
    NG --> APP["SmartOmbor"]
```

## 3. Asosiy modullar

| Modul | Vazifasi |
|---|---|
| accounts | Foydalanuvchilar va autentifikatsiya |
| companies | Kompaniyalar va a'zolik |
| products | Mahsulot va kategoriyalar |
| inventory | Ombor kirim-chiqimi |
| sales | Buyurtmalar va savdo |
| reports | Hisobot va eksport |
| api | REST API va ruxsatlar |
| config | Django va Celery konfiguratsiyasi |

## 4. Ma'lumotlar xavfsizligi

- Foydalanuvchilarning kompaniyalarga a'zoligi tekshiriladi.
- Kompaniyalararo ma'lumotlarga kirish cheklanadi.
- PostgreSQL ma'lumotlar bazasi Docker volume orqali saqlanadi.
- Redis parol bilan himoyalangan.
- Maxfiy sozlamalar `.env` orqali boshqariladi.
- Backup va Restore mexanizmi mavjud.

## 5. Avtomatik vazifalar

Celery va Redis orqali:

- Kam qolgan mahsulotlar haqida Rahbarga xabar yuborish.
- Kunlik savdo hisobotlarini tayyorlash va yuborish.
- Buyurtma yakunlanganda mijozga email yuborish.

## 6. Backup va tiklash

PostgreSQL bazasi va Media fayllar alohida zaxiralanadi.

Linux serverda backup manzili:

`/var/backups/smartombor/`

## 7. Deployment

Production muhiti Docker Compose, Nginx, Gunicorn, PostgreSQL, Redis va Celery asosida ishlaydi.

GitHub Actions orqali Docker image GHCR'ga yuboriladi. VPS mavjud bo'lgach, SSH orqali avtomatik deploy faollashtiriladi.
```

