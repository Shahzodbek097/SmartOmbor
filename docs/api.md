
# SmartOmbor REST API Documentation

## 1. API haqida

SmartOmbor REST API Django REST Framework asosida yaratilgan.

API orqali:
- Kategoriyalarni boshqarish.
- Mahsulotlarni boshqarish.
- Ombor kirim-chiqimlarini boshqarish.
- Buyurtmalar yaratish va boshqarish.
- JWT orqali autentifikatsiya qilish mumkin.

## 2. API manzillari

| Xizmat | URL |
|---|---|
| API asosiy manzili | `/api/v1/` |
| JWT token olish | `/api/token/` |
| JWT token yangilash | `/api/token/refresh/` |
| Swagger UI | `/swagger/` |
| ReDoc | `/redoc/` |
| Djoser autentifikatsiya | `/api/auth/` |

## 3. Autentifikatsiya

API JWT Bearer Token orqali himoyalangan.

### Token olish

**POST** `/api/token/`

Request:

```json
{
  "username": "shahzod",
  "password": "your-password"
}
```

Response:

```json
{
  "refresh": "refresh-token",
  "access": "access-token"
}
```

### Tokenni ishlatish

Har bir himoyalangan so'rovda quyidagi header yuboriladi:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

### Tokenni yangilash

**POST** `/api/token/refresh/`

Request:

```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```

Access token muddati: 30 daqiqa.

Refresh token muddati: 1 kun.

## 4. Kategoriyalar API

Base URL: `/api/v1/categories/`

| Method | Endpoint | Vazifasi |
|---|---|---|
| GET | `/categories/` | Kategoriyalar ro'yxati |
| POST | `/categories/` | Yangi kategoriya |
| GET | `/categories/{id}/` | Bitta kategoriya |
| PUT | `/categories/{id}/` | Kategoriyani to'liq yangilash |
| PATCH | `/categories/{id}/` | Kategoriyani qisman yangilash |
| DELETE | `/categories/{id}/` | Kategoriyani o'chirish |

Yangi kategoriya yaratish:

```json
{
  "nomi": "Ichimliklar",
  "description": "Ichimlik mahsulotlari"
}
```

Ruxsatlar:
- Rahbar: barcha amallar.
- Omborchi: barcha amallar.
- Boshqa faol kompaniya a'zolari: o'qish.

## 5. Mahsulotlar API

Base URL: `/api/v1/products/`

| Method | Endpoint | Vazifasi |
|---|---|---|
| GET | `/products/` | Mahsulotlar ro'yxati |
| POST | `/products/` | Mahsulot yaratish |
| GET | `/products/{id}/` | Mahsulot tafsilotlari |
| PUT | `/products/{id}/` | Mahsulotni yangilash |
| PATCH | `/products/{id}/` | Qisman yangilash |
| DELETE | `/products/{id}/` | Mahsulotni o'chirish |

Mahsulot yaratish:

```json
{
  "nomi": "Mineral suv",
  "category": 1,
  "xarid_narxi": "3000.00",
  "sotish_narxi": "5000.00",
  "min_qoldiq": 10
}
```

Qo'shimcha qidiruv parametrlari:

| Parametr | Vazifasi |
|---|---|
| `q` | Mahsulot nomi bo'yicha qidirish |
| `category` | Kategoriya ID bo'yicha filtrlash |

Misol:

`/api/v1/products/?q=suv&category=1`

`qoldiq` qiymati API orqali to'g'ridan-to'g'ri o'zgartirilmaydi. U ombor harakatlari orqali yangilanadi.

Ruxsatlar: Rahbar va Omborchi yozish amallarini bajaradi.

## 6. Ombor kirim-chiqim API

Base URL: `/api/v1/movements/`

| Method | Endpoint | Vazifasi |
|---|---|---|
| GET | `/movements/` | Ombor harakatlari ro'yxati |
| POST | `/movements/` | Yangi kirim yoki chiqim |
| GET | `/movements/{id}/` | Harakat tafsilotlari |

Yangi kirim:

```json
{
  "product": 1,
  "movement_type": "IN",
  "nechta": 20,
  "sababi": "Yangi mahsulot keldi"
}
```

Yangi chiqim:

```json
{
  "product": 1,
  "movement_type": "OUT",
  "nechta": 5,
  "sababi": "Ombordan chiqarildi"
}
```

Filtrlash:

| Parametr | Qiymatlar |
|---|---|
| `product` | Mahsulot ID |
| `movement_type` | `IN` yoki `OUT` |

Ruxsatlar:
- Rahbar.
- Omborchi.

Ombor harakati yaratilgandan keyin mahsulot qoldig'i avtomatik yangilanadi.

## 7. Buyurtmalar API

Base URL: `/api/v1/orders/`

| Method | Endpoint | Vazifasi |
|---|---|---|
| GET | `/orders/` | Buyurtmalar ro'yxati |
| POST | `/orders/` | Yangi buyurtma |
| GET | `/orders/{id}/` | Buyurtma tafsilotlari |
| POST | `/orders/{id}/finish/` | Buyurtmani yakunlash |
| POST | `/orders/{id}/cancel/` | Buyurtmani bekor qilish |
| DELETE | `/orders/{id}/` | Kutilayotgan buyurtmani o'chirish |

Buyurtma yaratish:

```json
{
  "items": [
    {
      "product": 1,
      "soni": 2
    },
    {
      "product": 2,
      "soni": 3
    }
  ]
}
```

Mahsulot narxi buyurtma yaratilayotganda mahsulotning amaldagi sotish narxidan olinadi.

Buyurtma holatlari:

| Status | Ma'nosi |
|---|---|
| PENDING | Kutilmoqda |
| COMPLETED | Yakunlangan |
| CANCELLED | Bekor qilingan |

Buyurtmani yakunlash:
- Buyurtma holati tekshiriladi.
- Mahsulotlar ombordan chiqariladi.
- Umumiy summa hisoblanadi.
- Buyurtma yakunlanadi.
- Mijozga email xabarnomasi yuborish vazifasi Celery navbatiga qo'shiladi.

Faqat PENDING holatidagi buyurtmani o'chirish mumkin.

Ruxsatlar:
- Rahbar: buyurtmalarni boshqaradi.
- Sotuvchi: o'z buyurtmalarini boshqaradi.

## 8. Kompaniyalararo xavfsizlik

API foydalanuvchining faol kompaniyasi asosida ishlaydi.

- Foydalanuvchi faqat o'z kompaniyasiga tegishli ma'lumotlarni ko'radi.
- Boshqa kompaniya mahsulotini buyurtmaga qo'shish taqiqlanadi.
- Kategoriya va mahsulotlar kompaniyaga avtomatik biriktiriladi.
- Ruxsatlar `CompanyRolePermission` orqali nazorat qilinadi.

## 9. HTTP javob kodlari

| Kod | Ma'nosi |
|---|---|
| 200 | So'rov muvaffaqiyatli |
| 201 | Yangi obyekt yaratildi |
| 204 | Obyekt muvaffaqiyatli o'chirildi |
| 400 | Ma'lumotlar yoki biznes qoidasi xatosi |
| 401 | Autentifikatsiya talab qilinadi |
| 403 | Ruxsat mavjud emas |
| 404 | Ma'lumot topilmadi |

## 10. API manbalari

- Swagger: `/swagger/`
- ReDoc: `/redoc/`
- API root: `/api/v1/`

---

**SmartOmbor REST API — API Documentation v1**
