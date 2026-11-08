from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from companies.models import CompanyMembership
from companies.utils import get_user_company

from products.models import Category, Product
from inventory.models import OmborMovement
from sales.models import Order, OrderItem


class CompanyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        company = get_user_company(user)

        if company:
            token["company_id"] = company.id
            token["company_nomi"] = company.nomi

            membership = CompanyMembership.objects.filter(
                user=user,
                company=company,
                faol=True,
                company__faol=True
            ).first()

            if membership:
                token["role"] = membership.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        company = get_user_company(self.user)

        if not company:
            raise AuthenticationFailed(
                "Sizda faol kompaniya mavjud emas."
            )

        if not self.user.is_superuser:
            membership = CompanyMembership.objects.filter(
                user=self.user,
                company=company,
                faol=True,
                company__faol=True
            ).exists()

            if not membership:
                raise AuthenticationFailed(
                    "Faol kompaniya a'zoligi topilmadi."
                )

        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "nomi",
            "description",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class ProductSerializer(serializers.ModelSerializer):

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none()
    )

    category_nomi = serializers.CharField(
        source="category.nomi",
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "nomi",
            "category",
            "category_nomi",
            "xarid_narxi",
            "sotish_narxi",
            "qoldiq",
            "min_qoldiq",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "qoldiq",
            "created_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            company = get_user_company(request.user)

            self.fields["category"].queryset = (
                Category.objects.filter(company=company)
                if company else Category.objects.none()
            )


class OmborMovementSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.none()
    )

    product_nomi = serializers.CharField(
        source="product.nomi",
        read_only=True
    )

    user_login = serializers.CharField(
        source="user.username",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = OmborMovement

        fields = [
            "id",
            "product",
            "product_nomi",
            "movement_type",
            "nechta",
            "sababi",
            "user_login",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user_login",
            "created_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            company = get_user_company(request.user)

            self.fields["product"].queryset = (
                Product.objects.filter(company=company)
                if company else Product.objects.none()
            )


class OrderItemReadSerializer(serializers.ModelSerializer):

    product_nomi = serializers.CharField(
        source="product.nomi",
        read_only=True
    )

    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_nomi",
            "soni",
            "narxi",
            "subtotal",
        ]


class OrderSerializer(serializers.ModelSerializer):

    customer_login = serializers.CharField(
        source="customer.username",
        read_only=True
    )

    company_nomi = serializers.CharField(
        source="company.nomi",
        read_only=True
    )

    items = OrderItemReadSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "buyurtma_raqami",
            "customer_login",
            "company_nomi",
            "status",
            "total_price",
            "created_at",
            "items",
        ]

        read_only_fields = fields



class OrderItemCreateSerializer(serializers.Serializer):

    product = serializers.IntegerField()
    soni = serializers.IntegerField(min_value=1)

    def validate_product(self, value):
        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError(
                "Foydalanuvchi ma'lumotlari topilmadi."
            )

        company = get_user_company(request.user)

        if not company:
            raise serializers.ValidationError(
                "Faol kompaniya topilmadi."
            )

        try:
            product = Product.objects.get(
                pk=value,
                company=company
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Mahsulot topilmadi yoki sizning kompaniyangizga tegishli emas."
            )

        return product



class OrderCreateSerializer(serializers.ModelSerializer):

    items = OrderItemCreateSerializer(
        many=True,
        allow_empty=False
    )

    class Meta:
        model = Order

        fields = [
            "items",
        ]

    def create(self, validated_data):

        request = self.context["request"]
        company = get_user_company(request.user)

        if not company:
            raise PermissionDenied(
                "Faol kompaniya topilmadi."
            )

        items_data = validated_data.pop("items")

        try:
            with transaction.atomic():

                order = Order.objects.create(
                    company=company,
                    customer=request.user
                )

                for item in items_data:

                    product = item["product"]
                    soni = item["soni"]

                    if product.company_id != company.id:
                        raise DjangoValidationError(
                            "Mahsulot boshqa kompaniyaga tegishli!"
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        soni=soni,
                        narxi=product.sotish_narxi
                    )

                return order

        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
