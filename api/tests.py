from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from companies.models import Company, CompanyMembership
from products.models import Category, Product
from inventory.models import OmborMovement
from sales.models import Order, OrderItem


User = get_user_model()


class SmartOmborAPITests(APITestCase):

    def setUp(self):

        # Birinchi kompaniya
        self.company = Company.objects.create(
            nomi="Test SmartOmbor",
            manzil="Toshkent",
            telefon="+998901111111",
            email="test1@example.com"
        )

        # Ikkinchi kompaniya
        self.other_company = Company.objects.create(
            nomi="Boshqa kompaniya",
            manzil="Samarqand",
            telefon="+998902222222",
            email="test2@example.com"
        )

        # Foydalanuvchilar
        self.rahbar = User.objects.create_user(
            username="test_rahbar",
            password="Test12345!"
        )

        self.omborchi = User.objects.create_user(
            username="test_omborchi",
            password="Test12345!"
        )

        self.sotuvchi = User.objects.create_user(
            username="test_sotuvchi",
            password="Test12345!"
        )

        self.boshqa_sotuvchi = User.objects.create_user(
            username="boshqa_sotuvchi",
            password="Test12345!"
        )

        # Kompaniya a'zoliklari
        CompanyMembership.objects.create(
            company=self.company,
            user=self.rahbar,
            role="Rahbar"
        )

        CompanyMembership.objects.create(
            company=self.company,
            user=self.omborchi,
            role="Omborchi"
        )

        CompanyMembership.objects.create(
            company=self.company,
            user=self.sotuvchi,
            role="Sotuvchi"
        )

        CompanyMembership.objects.create(
            company=self.company,
            user=self.boshqa_sotuvchi,
            role="Sotuvchi"
        )

        self.other_user = User.objects.create_user(
            username="other_user",
            password="Test12345!"
        )

        CompanyMembership.objects.create(
            company=self.other_company,
            user=self.other_user,
            role="Rahbar"
        )

        # Kategoriyalar
        self.category = Category.objects.create(
            company=self.company,
            nomi="Test kategoriya",
            description="Test uchun"
        )

        self.other_category = Category.objects.create(
            company=self.other_company,
            nomi="Boshqa kategoriya"
        )

        # Mahsulotlar
        self.product = Product.objects.create(
            company=self.company,
            nomi="Test mahsulot",
            category=self.category,
            xarid_narxi=10000,
            sotish_narxi=15000,
            qoldiq=0,
            min_qoldiq=5
        )

        self.other_product = Product.objects.create(
            company=self.other_company,
            nomi="Boshqa mahsulot",
            category=self.other_category,
            xarid_narxi=20000,
            sotish_narxi=25000
        )

        self.categories_url = "/api/v1/categories/"
        self.products_url = "/api/v1/products/"
        self.movements_url = "/api/v1/movements/"
        self.orders_url = "/api/v1/orders/"

    # 1. JWT token olish
    def test_jwt_token_olish(self):

        response = self.client.post(
            "/api/token/",
            {
                "username": "test_rahbar",
                "password": "Test12345!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        token = AccessToken(response.data["access"])

        self.assertEqual(
            token["company_id"],
            self.company.id
        )

        self.assertEqual(
            token["role"],
            "Rahbar"
        )

    # 2. Faqat o'z kompaniyasining kategoriyalarini ko'rish
    def test_category_faqat_oz_kompaniyasini_korsatadi(self):

        self.client.force_authenticate(
            user=self.rahbar
        )

        response = self.client.get(
            self.categories_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ids = [item["id"] for item in response.data]

        self.assertIn(self.category.id, ids)

        self.assertNotIn(
            self.other_category.id,
            ids
        )

    # 3. Rahbar kategoriya yarata oladi
    def test_rahbar_kategoriya_yarata_oladi(self):

        self.client.force_authenticate(
            user=self.rahbar
        )

        response = self.client.post(
            self.categories_url,
            {
                "nomi": "Yangi test kategoriya",
                "description": "API test"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        kategoriya = Category.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            kategoriya.company,
            self.company
        )

    # 4. Sotuvchi kategoriya yarata olmaydi
    def test_sotuvchi_kategoriya_yarata_olmaydi(self):

        self.client.force_authenticate(
            user=self.sotuvchi
        )

        response = self.client.post(
            self.categories_url,
            {
                "nomi": "Ruxsatsiz kategoriya",
                "description": ""
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # 5. Faqat o'z kompaniyasining mahsulotlarini ko'rish
    def test_product_faqat_oz_kompaniyasini_korsatadi(self):

        self.client.force_authenticate(
            user=self.rahbar
        )

        response = self.client.get(
            self.products_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ids = [item["id"] for item in response.data]

        self.assertIn(self.product.id, ids)

        self.assertNotIn(
            self.other_product.id,
            ids
        )

    # 6. Mahsulot yaratish va qoldiqni himoyalash
    def test_product_yaratish(self):

        self.client.force_authenticate(
            user=self.rahbar
        )

        response = self.client.post(
            self.products_url,
            {
                "nomi": "API yangi mahsulot",
                "category": self.category.id,
                "xarid_narxi": "12000.00",
                "sotish_narxi": "18000.00",
                "qoldiq": 100,
                "min_qoldiq": 5
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        product = Product.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            product.company,
            self.company
        )

        # Qoldiq bevosita API orqali o'zgarmasligi kerak
        self.assertEqual(product.qoldiq, 0)

    # 7. Omborga kirim qilish
    def test_omborga_kirim(self):

        self.client.force_authenticate(
            user=self.omborchi
        )

        response = self.client.post(
            self.movements_url,
            {
                "product": self.product.id,
                "movement_type": "IN",
                "nechta": 10,
                "sababi": "API test kirim"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.qoldiq,
            10
        )

        self.assertEqual(
            self.product.company,
            self.company
        )

    # 8. Boshqa kompaniya mahsulotiga kirim qilish mumkin emas
    def test_boshqa_kompaniya_mahsulotiga_kirim_taqiqlanadi(self):

        self.client.force_authenticate(
            user=self.omborchi
        )

        response = self.client.post(
            self.movements_url,
            {
                "product": self.other_product.id,
                "movement_type": "IN",
                "nechta": 5,
                "sababi": "Noto'g'ri test"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # 9. Buyurtma yaratish
    def test_buyurtma_yaratish(self):

        self.client.force_authenticate(
            user=self.sotuvchi
        )

        response = self.client.post(
            self.orders_url,
            {
                "items": [
                    {
                        "product": self.product.id,
                        "soni": 2
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data
        )

        order = Order.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            order.company,
            self.company
        )

        self.assertEqual(
            order.customer,
            self.sotuvchi
        )

        self.assertEqual(
            order.items.count(),
            1
        )

    # 10. Sotuvchi boshqa sotuvchining buyurtmasini ko'ra olmaydi
    def test_sotuvchi_boshqa_buyurtmani_kora_olmaydi(self):

        order = Order.objects.create(
            company=self.company,
            customer=self.boshqa_sotuvchi
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            soni=1,
            narxi=self.product.sotish_narxi
        )

        self.client.force_authenticate(
            user=self.sotuvchi
        )

        response = self.client.get(
            f"{self.orders_url}{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # 11. Buyurtma yakunlash va qoldiqni kamaytirish
    def test_buyurtma_yakunlash(self):

        # Avval omborga 10 dona mahsulot kiritamiz
        OmborMovement.objects.create(
            company=self.company,
            product=self.product,
            user=self.omborchi,
            movement_type="IN",
            nechta=10,
            sababi="Test kirim"
        )

        # Sotuvchi buyurtma yaratadi
        order = Order.objects.create(
            company=self.company,
            customer=self.sotuvchi
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            soni=2,
            narxi=self.product.sotish_narxi
        )

        self.client.force_authenticate(
            user=self.sotuvchi
        )

        response = self.client.post(
            f"{self.orders_url}{order.id}/finish/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.product.refresh_from_db()
        order.refresh_from_db()

        self.assertEqual(
            self.product.qoldiq,
            8
        )

        self.assertEqual(
            order.status,
            Order.Status.COMPLETED
        )

    # 12. Buyurtmani bekor qilish
    def test_buyurtmani_bekor_qilish(self):

        order = Order.objects.create(
            company=self.company,
            customer=self.sotuvchi
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            soni=1,
            narxi=self.product.sotish_narxi
        )

        self.client.force_authenticate(
            user=self.sotuvchi
        )

        response = self.client.post(
            f"{self.orders_url}{order.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED
        )

    # 13. Boshqa kompaniyaning buyurtmasini ko'rish taqiqlanadi
    def test_boshqa_kompaniya_buyurtmasi_yopiq(self):

        order = Order.objects.create(
            company=self.other_company,
            customer=self.other_user
        )

        self.client.force_authenticate(
            user=self.rahbar
        )

        response = self.client.get(
            f"{self.orders_url}{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # 14. Faol bo'lmagan a'zo API'ga kira olmaydi
    def test_faol_bolmagan_azo_api_ga_kira_olmaydi(self):

        membership = CompanyMembership.objects.get(
            company=self.company,
            user=self.omborchi
        )

        membership.faol = False
        membership.save(update_fields=["faol"])

        self.client.force_authenticate(
            user=self.omborchi
        )

        response = self.client.get(
            self.products_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

