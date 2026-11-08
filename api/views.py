from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.deletion import ProtectedError
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenRefreshView

from companies.models import CompanyMembership
from companies.utils import get_user_company

from products.models import Category, Product
from inventory.models import OmborMovement
from sales.models import Order
from sales.services import complete_order, cancel_order

from .permissions import CompanyRolePermission

from .serializers import (
    CompanyTokenObtainPairSerializer,
    CategorySerializer,
    ProductSerializer,
    OmborMovementSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)


class CompanyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CompanyTokenObtainPairSerializer

    @swagger_auto_schema(
        tags=["Token"],
        operation_summary="JWT token olish"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CompanyTokenRefreshView(TokenRefreshView):

    @swagger_auto_schema(
        tags=["Token"],
        operation_summary="JWT tokenni yangilash"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def get_company(request):
    company = get_user_company(request.user)

    if not company:
        raise PermissionDenied(
            "Siz faol kompaniyaga biriktirilmagansiz."
        )

    return company


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(tags=["Category"])
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(tags=["Category"])
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(tags=["Category"])
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(tags=["Category"])
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(tags=["Category"])
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(tags=["Category"])
)


class CategoryViewSet(viewsets.ModelViewSet):

    serializer_class = CategorySerializer

    permission_classes = [
        IsAuthenticated,
        CompanyRolePermission
    ]

    role_permissions = {
        "create": ("Rahbar", "Omborchi"),
        "update": ("Rahbar", "Omborchi"),
        "partial_update": ("Rahbar", "Omborchi"),
        "destroy": ("Rahbar", "Omborchi"),
    }

    def get_queryset(self):
        company = get_user_company(self.request.user)

        if not company:
            return Category.objects.none()

        return Category.objects.filter(
            company=company
        ).order_by("nomi")

    def perform_create(self, serializer):
        serializer.save(company=get_company(self.request))

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()

        try:
            category.delete()
        except ProtectedError:
            return Response(
                {"detail": "Bu kategoriya mahsulotlarga biriktirilgan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(tags=["Product"])
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(tags=["Product"])
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(tags=["Product"])
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(tags=["Product"])
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(tags=["Product"])
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(tags=["Product"])
)


class ProductViewSet(viewsets.ModelViewSet):

    serializer_class = ProductSerializer

    permission_classes = [
        IsAuthenticated,
        CompanyRolePermission
    ]

    role_permissions = {
        "create": ("Rahbar", "Omborchi"),
        "update": ("Rahbar", "Omborchi"),
        "partial_update": ("Rahbar", "Omborchi"),
        "destroy": ("Rahbar", "Omborchi"),
    }

    def get_queryset(self):
        company = get_user_company(self.request.user)

        if not company:
            return Product.objects.none()

        queryset = Product.objects.filter(
            company=company
        ).select_related("category")

        qidiruv = self.request.query_params.get("q")

        if qidiruv:
            queryset = queryset.filter(
                nomi__icontains=qidiruv
            )

        category = self.request.query_params.get("category")

        if category and category.isdigit():
            queryset = queryset.filter(
                category_id=int(category)
            )

        return queryset.order_by("nomi")

    def perform_create(self, serializer):
        serializer.save(company=get_company(self.request))

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()

        try:
            product.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Bu mahsulot buyurtma yoki ombor "
                        "harakatlarida ishlatilgan."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(tags=["OmborMovement"])
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(tags=["OmborMovement"])
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(tags=["OmborMovement"])
)


class OmborMovementViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):

    serializer_class = OmborMovementSerializer

    permission_classes = [
        IsAuthenticated,
        CompanyRolePermission
    ]

    role_permissions = {
        "list": ("Rahbar", "Omborchi"),
        "retrieve": ("Rahbar", "Omborchi"),
        "create": ("Rahbar", "Omborchi"),
    }

    def get_queryset(self):
        company = get_user_company(self.request.user)

        if not company:
            return OmborMovement.objects.none()

        queryset = OmborMovement.objects.filter(
            company=company
        ).select_related(
            "product",
            "user"
        )

        product = self.request.query_params.get("product")

        if product and product.isdigit():
            queryset = queryset.filter(
                product_id=int(product)
            )

        movement_type = self.request.query_params.get(
            "movement_type"
        )

        if movement_type in ["IN", "OUT"]:
            queryset = queryset.filter(
                movement_type=movement_type
            )

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        try:
            serializer.save(
                company=get_company(self.request),
                user=self.request.user
            )

        except DjangoValidationError as error:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(error.messages)

@method_decorator(
    name="list",
    decorator=swagger_auto_schema(tags=["Order"])
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(tags=["Order"])
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(tags=["Order"])
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(tags=["Order"])
)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    permission_classes = [
        IsAuthenticated,
        CompanyRolePermission
    ]

    role_permissions = {
        "list": ("Rahbar", "Sotuvchi"),
        "retrieve": ("Rahbar", "Sotuvchi"),
        "create": ("Sotuvchi",),
        "finish": ("Rahbar", "Sotuvchi"),
        "cancel": ("Rahbar", "Sotuvchi"),
        "destroy": ("Rahbar", "Sotuvchi"),
    }

    def get_serializer_class(self):

        if self.action == "create":
            return OrderCreateSerializer

        return OrderSerializer

    def get_queryset(self):
        company = get_user_company(self.request.user)

        if not company:
            return Order.objects.none()

        queryset = Order.objects.filter(
            company=company
        ).select_related(
            "customer",
            "company"
        ).prefetch_related(
            "items__product"
        )

        if not self.request.user.is_superuser:
            membership = CompanyMembership.objects.filter(
                user=self.request.user,
                company=company,
                faol=True,
                company__faol=True
            ).first()

            if not membership or membership.role != "Rahbar":
                queryset = queryset.filter(
                    customer=self.request.user
                )

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        result = OrderSerializer(
            order,
            context=self.get_serializer_context()
        )

        return Response(
            result.data,
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        method="post",
        tags=["Order"],
        operation_summary="Buyurtmani yakunlash",
        operation_description=(
            "Buyurtmani yakunlaydi va mahsulotlarni "
            "ombordan avtomatik chiqaradi."
        ),
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):

        order = self.get_object()

        try:
            complete_order(
                order.id,
                user=request.user
            )

            order.refresh_from_db()

            return Response(
                OrderSerializer(
                    order,
                    context=self.get_serializer_context()
                ).data
            )

        except DjangoValidationError as error:
            return Response(
                {"detail": error.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method="post",
        tags=["Order"],
        operation_summary="Buyurtmani bekor qilish",
        operation_description="Buyurtmani bekor qiladi.",
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):

        order = self.get_object()

        try:
            cancel_order(
                order.id,
                user=request.user
            )

            order.refresh_from_db()

            return Response(
                OrderSerializer(
                    order,
                    context=self.get_serializer_context()
                ).data
            )

        except DjangoValidationError as error:
            return Response(
                {"detail": error.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):

        order = self.get_object()

        if order.status != Order.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Faqat kutilayotgan buyurtmalarni "
                        "o'chirish mumkin."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser:
            company = get_company(request)

            membership = CompanyMembership.objects.filter(
                user=request.user,
                company=company,
                faol=True,
                company__faol=True
            ).first()

            if (
                not membership
                or (
                    membership.role != "Rahbar"
                    and order.customer_id != request.user.id
                )
            ):
                raise PermissionDenied(
                    "Bu buyurtmani o'chirish huquqingiz yo'q."
                )

        order.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

