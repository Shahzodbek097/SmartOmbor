# SmartOmbor

**SmartOmbor** — kichik va o‘rta savdo korxonalari uchun ko‘p kompaniyali ombor, mahsulot, buyurtma va savdo boshqaruv web tizimi.

Loyiha Python, Django va Django REST Framework asosida yaratilgan. Uning asosiy vazifasi korxonaning ombordagi mahsulot qoldiqlarini, kirim-chiqim harakatlarini, sotuvlarni va moliyaviy ko‘rsatkichlarini yagona platformada yuritishdir.

**Loyiha holati:** AWS EC2 serverida Docker orqali ishga tushirilgan. GitHub Actions orqali CI/CD jarayoni sozlangan. Production muhitida HTTPS/SSL hali yoqilmagan; hozirgi kirish HTTP orqali amalga oshadi.

## Mundarija

- [Loyihaning maqsadi](#loyihaning-maqsadi)
- [Asosiy imkoniyatlar](#asosiy-imkoniyatlar)
- [Ro‘yxatdan o‘tish va kompaniya yaratish](#ro‘yxatdan-o‘tish-va-kompaniya-yaratish)
- [Foydalanuvchi rollari](#foydalanuvchi-rollari)
- [Ma’lumotlar modeli va biznes mantiqi](#ma’lumotlar-modeli-va-biznes-mantiqi)
- [Hisobotlar](#hisobotlar)
- [REST API](#rest-api)
- [Texnologiyalar](#texnologiyalar)
- [Loyiha tuzilishi](#loyiha-tuzilishi)
- [Mahalliy muhitda ishga tushirish](#mahalliy-muhitda-ishga-tushirish)
- [Docker va production arxitekturasi](#docker-va-production-arxitekturasi)
- [CI/CD va avtomatik deploy](#cicd-va-avtomatik-deploy)
- [Backup va tiklash](#backup-va-tiklash)
- [Xavfsizlik](#xavfsizlik)

## Loyihaning maqsadi

Oddiy ombor daftarlarida mahsulotlar qoldig‘i, xarid narxi, sotish narxi va sotuvlar alohida yuritiladi. SmartOmbor bu jarayonlarni o‘zaro bog‘laydi:

1. Kompaniya ro‘yxatdan o‘tadi va uning birinchi foydalanuvchisi Rahbar bo‘ladi.
2. Rahbar kategoriyalar va mahsulotlarni yaratadi, xodimlarni tizimga qo‘shadi.
3. Omborchi mahsulot kirimi va chiqimini qayd etadi; tizim qoldiqni avtomatik yangilaydi.
4. Sotuvchi buyurtma yaratadi. Buyurtma yakunlanganda ombordagi tegishli mahsulotlar kamayadi.
5. Rahbar savdo, foyda, sotuvchilar va ombor holati bo‘yicha hisobotlarni ko‘radi.

Eng muhim arxitektura talabi — turli kompaniyalarning ma’lumotlari bir-biridan ajratilgan bo‘lishi.

## Asosiy imkoniyatlar

- Yangi foydalanuvchini ro‘yxatdan o‘tkazish va avtomatik tizimga kiritish.
- Ro‘yxatdan o‘tish paytida kompaniya yaratish va dastlabki Rahbar a’zoligini biriktirish.
- Kompaniya xodimlarini qo‘shish, tahrirlash, qidirish va faolligini boshqarish.
- Rahbar, Omborchi va Sotuvchi rollari bo‘yicha ruxsatlarni tekshirish.
- Kategoriyalar va mahsulotlarni yaratish, ko‘rish, tahrirlash va qidirish.
- Ombor kirimi va chiqimini sabab hamda miqdori bilan qayd etish.
- Buyurtma yaratish, ko‘rish, yakunlash, bekor qilish va o‘chirish amallari.
- Buyurtma yakunlanganda ombor qoldig‘ini avtomatik kamaytirish.
- Minimal qoldiqdan kamaygan mahsulotlarni aniqlash.
- Kunlik, oylik va tanlangan davr bo‘yicha savdo tahlili.
- Sotuvchilar faoliyati va mahsulotlar bo‘yicha hisobotlar.
- Hisobotlarni Excel va PDF formatlarida eksport qilish.
- Gmail SMTP orqali xabarnomalar yuborish.
- Celery va Redis orqali fon vazifalarini bajarish.
- PostgreSQL ma’lumotlar bazasi va Docker konteynerlari.
- GitHub Actions yordamida kodni tekshirish, Docker image yaratish va VPS'ga deploy qilish.
- PostgreSQL hamda media fayllar uchun zaxira nusxa olish.

## Ro‘yxatdan o‘tish va kompaniya yaratish

Veb-interfeysdagi `/accounts/register/` sahifasi orqali yangi foydalanuvchi ro‘yxatdan o‘tadi. Forma foydalanuvchi ma’lumotlari bilan birga kompaniya ma’lumotlarini ham qabul qiladi.

Ro‘yxatdan o‘tish jarayoni `transaction.atomic()` ichida bajariladi:

1. `RegisterForm` tekshiriladi va foydalanuvchi yaratiladi.
2. Kiritilgan ma’lumotlar asosida yangi `Company` yozuvi yaratiladi.
3. Foydalanuvchiga `CompanyMembership` orqali `Rahbar` roli va faol a’zolik beriladi.
4. Eski Django Group mexanizmi bilan moslik uchun foydalanuvchi `Rahbar` guruhiga ham qo‘shiladi.
5. Foydalanuvchi avtomatik login qilinadi va shaxsiy kabinetiga yo‘naltiriladi.

Keyinchalik Rahbar o‘z kompaniyasiga xodimlarni qo‘shadi va ularga Omborchi yoki Sotuvchi rolini beradi. Xodimlar alohida kompaniya ochmaydi; ular mavjud kompaniyaning a’zolari sifatida biriktiriladi.

## Foydalanuvchi rollari

| Rol | Asosiy vazifalar |
|---|---|
| **Rahbar** | Kompaniya xodimlarini boshqarish, umumiy ko‘rsatkichlar va hisobotlarni ko‘rish, Excel/PDF eksporti, mahsulot va ombor jarayonlarini nazorat qilish. |
| **Omborchi** | Kategoriyalar va mahsulotlarni yuritish, ombor kirim-chiqimlarini qayd etish, qoldiqlarni nazorat qilish. |
| **Sotuvchi** | Buyurtmalar bilan ishlash, savdoni rasmiylashtirish va o‘z ish jarayonini kuzatish. |

Ruxsatlar faqat menyuni yashirish bilan cheklanmaydi: Django view dekoratorlari va API permission class'lari server tomonida ham tekshiradi. Foydalanuvchi faqat faol kompaniya a’zoligi va o‘z roliga ruxsat etilgan amallarni bajarishi kerak.

Django Group ruxsatlari ham avtomatik boshqariladi. `accounts` ilovasidagi `post_migrate` signali `migrate` bajarilgandan keyin uchta rol guruhini yaratadi va kerakli model ruxsatlarini biriktiradi. Mavjud faol kompaniya a’zolarining guruhlari ham `CompanyMembership.role` qiymatiga moslanadi. Rahbar xodim qo‘shganda yoki rolini o‘zgartirganda guruh ruxsatlari avtomatik sinxronlanadi.

| Rol | Avtomatik ruxsatlar va menyular |
|---|---|
| **Rahbar** | Mahsulot va kategoriyalarni ko‘rish, qo‘shish va tahrirlash; xodimlarni boshqarish; kompaniya buyurtmalari va hisobotlarini ko‘rish. |
| **Omborchi** | Mahsulot va kategoriyalarni ko‘rish, qo‘shish va tahrirlash; ombor kirim-chiqimini yuritish. |
| **Sotuvchi** | Buyurtma yaratish va faqat o‘z buyurtmalarini ko‘rish, yakunlash yoki bekor qilish. |

Bosh menyu uchala rol uchun mavjud. Sotuvchiga `sales.view_order` ruxsati berilgan bo‘lsa ham, barcha buyurtmalar sahifasi alohida `Rahbar` roli bilan himoyalangan. Shu tariqa Sotuvchi boshqa xodimlarning buyurtmalarini ko‘ra olmaydi.

Yangi lokal yoki production bazasida odatdagi `python manage.py migrate` buyrug‘i rol guruhlari va ruxsatlarini ham sozlaydi.

## Ma’lumotlar modeli va biznes mantiqi

### Kompaniya va a’zolik

- `Company` kompaniya nomi, manzili, telefoni, emaili va faol holatini saqlaydi.
- `CompanyMembership` foydalanuvchini kompaniyaga bog‘laydi va uning `Rahbar`, `Omborchi` yoki `Sotuvchi` rolini belgilaydi.
- Bitta kompaniya ichida bitta foydalanuvchining takroriy a’zoligi unique constraint bilan cheklanadi.
- `get_user_company()` foydalanuvchining faol kompaniyasini aniqlash uchun ishlatiladi.

### Kategoriyalar va mahsulotlar

`Category` modelida kompaniya, kategoriya nomi va tavsifi saqlanadi. Kategoriya nomining takrorlanishi bir kompaniya doirasida cheklanadi.

`Product` modelining muhim maydonlari:

| Maydon | Ma’nosi |
|---|---|
| `nomi` | Mahsulot nomi |
| `category` | Mahsulot kategoriyasi |
| `xarid_narxi` | Mahsulotning xarid tannarxi |
| `sotish_narxi` | Mahsulotning sotish narxi |
| `qoldiq` | Ombordagi joriy miqdor |
| `min_qoldiq` | Minimal nazorat qoldig‘i |
| `company` | Mahsulot tegishli bo‘lgan kompaniya |

Mahsulot saqlanayotganda kompaniya biriktirilgani va uning kategoriyasi ham aynan shu kompaniyaga tegishli ekanligi tekshiriladi.

### Ombor harakatlari

`OmborMovement` modeli har bir kirim yoki chiqim yozuvini saqlaydi. Asosiy maydonlar: `product`, `movement_type`, `nechta`, `sababi`, `user`, `company` va `created_at`.

- `IN` — kirim: mahsulot qoldig‘iga miqdor qo‘shiladi.
- `OUT` — chiqim: mahsulot qoldig‘idan miqdor ayriladi.
- Miqdor noldan katta bo‘lishi shart.
- Chiqimda yetarli qoldiq bo‘lmasa, amal rad etiladi.
- Mahsulot qatori `select_for_update()` bilan bloklanib, parallel kirim-chiqimlar vaqtida qoldiqning noto‘g‘ri hisoblanishi oldi olinadi.
- Saqlangan ombor harakati keyinchalik tahrirlanmaydi; bu tarixiy hisobni saqlashga yordam beradi.

### Buyurtma va sotuv

`Order` buyurtma yozuvini, `OrderItem` esa buyurtma ichidagi mahsulot, miqdor (`soni`) va sotuv narxini (`narxi`) saqlaydi.

Buyurtma holatlari:

- `PENDING` — kutilmoqda.
- `COMPLETED` — yakunlangan.
- `CANCELLED` — bekor qilingan.

Buyurtma har bir kompaniya doirasida alohida tartib raqamiga ega. Buyurtma mahsulotlari ham buyurtma bilan bir kompaniyaga tegishli bo‘lishi tekshiriladi.

Buyurtma yakunlanganda `complete_order()` biznes funksiyasi savdoni yakunlaydi va har bir mahsulot uchun `OUT` turidagi `OmborMovement` yaratadi. Shu sabab mahsulot qoldig‘i oddiy qo‘lda o‘zgartirilmaydi, balki ombor harakati orqali hisoblanadi.

## Hisobotlar

Hisobotlar `reports` ilovasidagi service funksiyalari orqali tayyorlanadi. Hisobotlarda kompaniya filtri qo‘llanadi; tanlangan sana oralig‘i bo‘yicha natijalar olinishi mumkin.

Asosiy ko‘rsatkichlar:

- Yakunlangan buyurtmalar soni.
- Jami savdo summasi.
- Sotilgan mahsulotlar miqdori.
- Yalpi foyda.
- Minimal qoldiqdan kam mahsulotlar.
- Davr bo‘yicha savdo grafigi va eng ko‘p sotilgan mahsulotlar.
- Sotuvchilar bo‘yicha buyurtmalar va savdo natijalari.
- Ombor qoldiqlari va mahsulotlar kesimidagi tahlil.

Yalpi foyda amaldagi hisoblash mantiqida har bir sotilgan mahsulot uchun quyidagicha hisoblanadi:

**Yalpi foyda = (sotuv narxi − xarid narxi) × sotilgan miqdor.**

Rahbar hisobotlarni Excel (`.xlsx`) va PDF formatida yuklab olishi mumkin. Hisobotlar tanlangan sana oralig‘iga mos ravishda shakllantiriladi.

## REST API

API Django REST Framework asosida yaratilgan. Asosiy router manzili `/api/v1/`.

| Endpoint | Vazifasi |
|---|---|
| `/api/v1/categories/` | Kategoriyalar |
| `/api/v1/products/` | Mahsulotlar |
| `/api/v1/movements/` | Ombor kirim-chiqim harakatlari |
| `/api/v1/orders/` | Buyurtmalar |

Qo‘shimcha API yo‘llari:

- `POST /api/token/` — username va password orqali JWT token olish.
- `POST /api/token/refresh/` — refresh token yordamida access tokenni yangilash.
- `/api/auth/` — Djoser autentifikatsiya yo‘llari.
- `/swagger/` — Swagger API hujjatlari.
- `/redoc/` — ReDoc API hujjatlari.

API autentifikatsiyasi JWT orqali ishlaydi. So‘rovlar odatda `Authorization: Bearer <access_token>` sarlavhasi bilan yuboriladi. Sozlamalarda access token muddati 30 daqiqa, refresh token muddati 1 kun qilib belgilangan. API ruxsatlari autentifikatsiya va kompaniya/rol tekshiruvlariga tayangan.

Mahsulotlar API'sida `q` parametri orqali nom bo‘yicha qidirish va `category` orqali kategoriya bo‘yicha filtrlash mavjud. Ombor harakatlarida `product` va `movement_type` filtrlari mavjud.

## Texnologiyalar

| Texnologiya | Loyihadagi vazifasi |
|---|---|
| Python 3.11 | Asosiy dasturlash tili |
| Django 5.2 | Web backend va ORM |
| Django REST Framework | REST API |
| Simple JWT | API token autentifikatsiyasi |
| Djoser | Autentifikatsiya bilan bog‘liq API yo‘llari |
| drf-yasg | Swagger va ReDoc hujjatlari |
| PostgreSQL 16 | Production ma’lumotlar bazasi |
| SQLite | Mahalliy sodda ishlab chiqish muhiti uchun |
| Redis 7 | Celery broker va backend |
| Celery | Fon vazifalari |
| Celery Beat | Rejalashtirilgan vazifalar |
| Gunicorn | Django WSGI serveri |
| Nginx | Reverse proxy va statik/media fayllar |
| Docker Compose | Xizmatlarni konteynerlarda boshqarish |
| openpyxl | Excel hisobotlari |
| ReportLab | PDF hisobotlari |
| GitHub Actions | CI/CD avtomatlashtirish |
| GitHub Container Registry | Docker image saqlash |
| AWS EC2 | Production server |

## Loyiha tuzilishi

```text
SmartOmbor/
├── accounts/          # Ro‘yxatdan o‘tish, login, profil va foydalanuvchilar
├── companies/         # Kompaniya va kompaniya a’zoligi
├── products/          # Kategoriyalar va mahsulotlar
├── inventory/         # Ombor kirim-chiqim harakatlari
├── sales/             # Buyurtmalar va sotuv biznes mantiqi
├── reports/           # Hisobotlar, eksport va Celery vazifalari
├── api/               # DRF serializers, viewsets va permissions
├── config/            # Django settings, URL va Celery konfiguratsiyasi
├── templates/         # HTML sahifalar
├── static/            # Statik fayllar
├── nginx/             # Nginx konfiguratsiyasi
├── scripts/           # Backup skriptlari
├── .github/workflows/ # CI va CD workflow fayllari
├── compose.yaml
├── compose.prod.yaml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Mahalliy muhitda ishga tushirish

### 1. Repository'ni klonlash

```bash
git clone https://github.com/Shahzodbek097/SmartOmbor.git
cd SmartOmbor
```

### 2. Virtual muhit yaratish

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Kutubxonalarni o‘rnatish

```bash
python -m pip install -r requirements.txt
```

### 4. Muhit o‘zgaruvchilarini sozlash

`.env.example` faylidan `.env` yarating. Undagi Django maxfiy kaliti, database, Redis va email sozlamalarini o‘z muhitingizga moslang. `.env` faylini GitHub'ga yubormang.

Mahalliy SQLite konfiguratsiyasida alohida PostgreSQL xizmatini ishga tushirish shart emas. PostgreSQL ishlatmoqchi bo‘lsangiz, `.env` ichidagi database sozlamalarini moslang.

### 5. Migratsiya va Django tekshiruvi

```bash
python manage.py migrate
python manage.py check
```

### 6. Django development server

```bash
python manage.py runserver
```

Sayt odatda `http://127.0.0.1:8000/` manzilida ishlaydi. Asosiy ish sahifalari `/accounts/login/`, `/accounts/register/` va `/dashboard/` yo‘llarida joylashgan.

## Docker va production arxitekturasi

Mahalliy Docker ishga tushirish:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

Production muhitida asosiy Compose fayliga `compose.prod.yaml` qo‘shiladi:

```bash
docker compose -f compose.yaml -f compose.prod.yaml config -q
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

Production arxitekturasidagi asosiy xizmatlar:

| Xizmat | Vazifasi |
|---|---|
| `db` | PostgreSQL ma’lumotlar bazasi |
| `redis` | Celery uchun broker/backend |
| `web` | Django ilovasi va Gunicorn |
| `celery_worker` | Fon vazifalarini bajarish |
| `celery_beat` | Rejalashtirilgan vazifalarni yuborish |
| `nginx` | Docker ichidagi reverse proxy |

PostgreSQL, Redis, statik fayllar, media va Celery Beat ma’lumotlari Docker volume'larda saqlanadi. Production Compose konfiguratsiyasida Django konteyneri tashqi portga bevosita chiqarilmaydi. Docker Nginx odatda hostning faqat lokal interfeysiga bog‘langan `NGINX_HTTP_PORT` portida ishlaydi; host Nginx esa ommaviy HTTP so‘rovlarini unga uzatadi.

Production server AWS EC2 (Amazon Linux 2023) muhitida ishlaydi. Deploy jarayonida ilova konteynerlari yangilanadi, database migratsiyalari bajariladi, statik fayllar yig‘iladi va xizmatlarning healthcheck holati tekshiriladi.

## CI/CD va avtomatik deploy

GitHub Actions ikki alohida workflow orqali ishlaydi:

### CI — `.github/workflows/smartombor-ci.yml`

`main` branch'ga push yoki pull request bo‘lganda:

1. Python 3.11 muhiti tayyorlanadi va `requirements.txt` kutubxonalari o‘rnatiladi.
2. PostgreSQL va Redis test xizmatlari ishga tushiriladi.
3. `python manage.py check` bajariladi.
4. Migratsiyalar `makemigrations --check --dry-run` bilan tekshiriladi.
5. `python manage.py test api -v 2` orqali API testlari bajariladi.
6. Docker Compose konfiguratsiyalari tekshiriladi va image'lar yig‘iladi.
7. `main` branch'dagi push CI tekshiruvlaridan o‘tsa, Docker image GHCR'ga yuboriladi.

### CD — `.github/workflows/deploy.yml`

CD faqat `main` branch'ga tegishli push uchun CI muvaffaqiyatli tugagandan keyin avtomatik ishga tushadi. Shuningdek, tasdiqlash input'i bilan qo‘lda `workflow_dispatch` orqali ishga tushirish imkoniyati mavjud.

GitHub repository sozlamalarida quyidagi Actions secrets va variable bo‘lishi kerak:

| Nomi | Turi | Mazmuni |
|---|---|---|
| `VPS_HOST` | Secret | EC2 serverining joriy Public IPv4 yoki DNS manzili |
| `VPS_USER` | Secret | SSH foydalanuvchisi; ushbu serverda `ec2-user` |
| `VPS_SSH_PRIVATE_KEY` | Secret | Serverga tegishli SSH private key |
| `VPS_KNOWN_HOSTS` | Secret | Server host key tekshiruvi uchun `ssh-keyscan` natijasi |
| `VPS_APP_DIR` | Variable | Serverdagi loyiha papkasi, masalan `/home/ec2-user/SmartOmbor` |

GHCR package private bo‘lsa, `GHCR_USERNAME` va `GHCR_READ_TOKEN` secrets ham kerak bo‘ladi. Package public bo‘lsa, deploy workflow bu ikki qiymatsiz ham ishlashi mumkin.

CD jarayoni SSH orqali serverga ulanadi, repository kodini yangilaydi, mavjud database va media uchun backup oladi, GHCR'dan image'larni tortadi, konteynerlarni yangilaydi va healthcheck hamda Celery javobini tekshiradi. Yangi versiya sog‘lom ishga tushmasa, mavjud oldingi image orqali rollback qilishga urinish mavjud. Database migratsiyalari esa avtomatik ravishda orqaga qaytarilmaydi.

**Eslatma:** GitHub Actions'da `Connection timed out` xatosi chiqsa, avvalo EC2 ishlayotganini, `VPS_HOST` IP manzili to‘g‘riligini va AWS Security Group'da TCP 22/SSH kirishiga ruxsat borligini tekshiring. Bu xato odatda kod yoki private key noto‘g‘riligini emas, tarmoq orqali SSH ulanishi o‘rnatilmaganini bildiradi.

## Celery va rejalashtirilgan vazifalar

Celery vazifalari Redis broker orqali fon rejimida bajariladi. `config/settings.py` dagi Celery Beat jadvali `Asia/Tashkent` vaqt zonasidan foydalanadi.

| Vazifa | Reja |
|---|---|
| Kompaniyalarning kunlik savdo hisobotlarini tayyorlash va Rahbarlarga yuborish | Har kuni 23:55 |
| Kam qoldiq bo‘yicha Rahbarlarga email ogohlantirish yuborish | Har kuni 08:00 |

Vazifalar `reports/tasks.py` ichida joylashgan. Ular faol kompaniya va faol Rahbar a’zoliklarini tekshiradi; email yuborish uchun kompaniya Rahbarlarida email manzili bo‘lishi kerak.

## Backup va tiklash

`scripts/backup_db.sh` production Compose xizmatlaridan foydalanib:

- PostgreSQL ma’lumotlar bazasini custom dump formatida zaxiralaydi;
- Django media fayllarini `.tar.gz` arxiviga oladi;
- vaqtinchalik fayllarni tekshiradi va yakuniy backup fayllariga aylantiradi;
- backup papkasiga cheklangan ruxsatlar beradi;
- 7 kundan eski backup fayllarini tozalaydi.

Linux serverda qo‘lda backup olish:

```bash
bash scripts/backup_db.sh
```

Windows uchun `scripts/backup_db.ps1` skripti ham mavjud:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\backup_db.ps1
```

Production serverda backup jarayoni systemd service va timer orqali har kuni soat 02:00 (Asia/Tashkent) da bajariladigan qilib sozlangan. Tiklashdan oldin kerakli backup fayllarini tekshirish va alohida test database'da restore sinovini bajarish tavsiya etiladi. Backup fayllarini ochiq repository'ga joylamang.

## Xavfsizlik

- Production maxfiy qiymatlari `.env` va GitHub Actions secrets orqali boshqariladi.
- `.env`, SSH private key, database dump va media backup repository'ga kiritilmasligi kerak.
- API so‘rovlari JWT va rol/kompaniya permission tekshiruvlaridan o‘tadi.
- Model va service darajasida kompaniyalararo bog‘lanishlar tekshiriladi.
- PostgreSQL va Redis tashqi internetga ochilmasligi kerak.
- SSH faqat zarur manbalarga ruxsat berilgan Security Group qoidalari bilan himoyalanishi kerak.
- Production serverda HTTPS/SSL sertifikati hali sozlanmagan. Haqiqiy foydalanuvchi ma’lumotlari bilan ommaviy foydalanishdan oldin domen va HTTPS sozlash zarur.

## Loyiha holati va keyingi takomillashtirishlar

SmartOmbor production serverga joylashtirilgan va CI/CD, Docker, Celery hamda kunlik backup jarayonlari sozlangan. Keyingi muhim ishlar — domenni ulash, HTTPS/SSL yoqish, production monitoringni kuchaytirish va restore jarayonini muntazam sinab borish.

## Muallif

**Shahzod Abdusattorov**

SmartOmbor Python, Django va Django REST Framework bo‘yicha amaliy bilimlarni mustahkamlash hamda real savdo va ombor jarayonlarini avtomatlashtirish maqsadida ishlab chiqilgan loyiha.

**Repository:** https://github.com/Shahzodbek097/SmartOmbor

---

**SmartOmbor — ombor, mahsulot va savdo jarayonlarini yagona tizimda boshqaring.**