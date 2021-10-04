from django.http import JsonResponse
from rest_framework.views import APIView

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from e_shop.permissions import DenyAny, IsShop

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from rest_framework.response import Response
from django.db.models import Q, Sum, F
from ujson import loads as load_json
from django.db import IntegrityError

import yaml
from yaml import Loader

from e_shop.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, Order, OrderItem, Contact
from e_shop.serializers import UserSerializer
from e_shop.signals import new_user_registered, new_order
from e_shop.serializers import (ProductSerializer, ProductInfoSerializer, OrderItemSerializer, OrderSerializer, \
                                OrderItemUpdateSerializer, OrderCreateSerializer)
from e_shop.filters import ProductFilter


class UploadProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsShop()]
        else:
            return [DenyAny()]

    def create(self, request, *args, **kwargs):
        if request.stream:
            stream = request.stream
            data = yaml.load(stream, Loader=Loader)

            shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
            for category in data['categories']:
                category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                category_object.shops.add(shop.id)
                category_object.save()
            ProductInfo.objects.filter(shop_id=shop.id).delete()
            for item in data['goods']:
                product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                product_info = ProductInfo.objects.create(product_id=product.id,
                                                          external_id=item['id'],
                                                          model=item['model'],
                                                          price=item['price'],
                                                          price_rrc=item['price_rrc'],
                                                          quantity=item['quantity'],
                                                          shop_id=shop.id)
                for name, value in item['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(product_info_id=product_info.id,
                                                    parameter_id=parameter_object.id,
                                                    value=value)

            return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class RegisterAccountViewSet(ModelViewSet):
    """
    Для регистрации покупателей
    """

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        else:
            return [DenyAny()]

    def create(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(request.data['password'])
            user.save()
            new_user_registered.send(sender=self.__class__, user_id=user.id)
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class ProductListViewSet(ModelViewSet):
    """
    Класс для вывода списка всех товаров
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [IsAuthenticated()]
        else:
            return [DenyAny()]


class ProductInfoViewSet(ModelViewSet):
    """
    Класс для вывода списка товаров по фильтру
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [IsAuthenticated()]
        else:
            return [DenyAny()]


class BasketViewSet(ModelViewSet):
    """
    Класс для работы с корзиной пользователя
    """

    permission_class = [IsAuthenticated]

    def get_queryset(self):
        if self.action in ['list', 'destroy']:
            return Order.objects.filter(user=self.request.user, state='basket').all()
        elif self.action in ['update', 'partial_update', 'create']:
            return OrderItem.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'destroy']:
            return OrderSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderItemUpdateSerializer
        elif self.action in ['create']:
            return OrderCreateSerializer
        return OrderItemSerializer

    def create(self, request, *args, **kwargs):
        # basket, created = Order.objects.get_or_create(user=request.user, state='basket')
        contact = Contact.objects.filter(user=request.user).all().get().id
        self.request.data['contact'] = contact
        basket = Order.objects.create(user=request.user, state='basket', contact_id=contact)



        serializer = OrderCreateSerializer

        # _mutable = self.request.data._mutable
        # self.request.data._mutable = True
        # self.request.data['order'] = basket.id
        # self.request.data._mutable = _mutable
        # return super().create(request, *args, **kwargs)
        return JsonResponse(serializer(basket).data)

    def partial_update(self, request, pk=None):
        # order_item_id = OrderItem.objects.filter(id=pk).distinct().get().order_id
        basket_id = list(Order.objects.filter(user_id=request.user.id, state='basket').all())
        basket_id = [el.id for el in basket_id]

        serializer = OrderItemUpdateSerializer

        if int(pk) in basket_id:
            order_item_qnty = OrderItem.objects.filter(order_id=pk, product_info_id=self.request.data['product_info']).all().count()

            if order_item_qnty == 0:
                order_item = OrderItem.objects.create(order_id=pk, quantity=self.request.data['quantity'],
                                                                      product_info_id=self.request.data['product_info'])
                return JsonResponse(serializer(order_item).data)
            else:
                order_item = OrderItem.objects.filter(order_id=pk,
                    product_info_id=self.request.data['product_info']).update(quantity=self.request.data['quantity'])
                return JsonResponse({'Status': 'OK'})
        else:

            return JsonResponse({'Status': 'Error', 'message': 'cannot update other basket'})


class OrderViewSet(ModelViewSet):

    # queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ['partial_update', 'list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [DenyAny()]


    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Order.objects.filter(user=self.request.user)
        else:
            return Order.objects.all()



    def partial_update(self, request, pk=None):

        order_id = list(Order.objects.filter(user_id=request.user.id).all())
        order_id = [el.id for el in order_id]


        if int(pk) in order_id:
            order_item = Order.objects.filter(id=pk).update(state=self.request.data['state'])
            return JsonResponse({'Status': 'updated'})
        else:
            return JsonResponse({'Status': 'Error', 'message': 'cannot update other order'})

