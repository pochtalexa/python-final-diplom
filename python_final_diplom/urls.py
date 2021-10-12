"""python_final_diplom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import routers
from django.urls import path, include
from django.contrib import admin
from e_shop import views
from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()
router.register('partner/update', views.UploadProductViewSet, basename='partner_update')
router.register('partner/state', views.OrderStateViewSet, basename='partner_state')
router.register('user/register', views.RegisterAccountViewSet, basename='user-register')
router.register('products/list', views.ProductListViewSet, basename='products-list')
router.register('products', views.ProductInfoViewSet, basename='products-info')
router.register('basket', views.BasketViewSet, basename='basket')
router.register('order', views.OrderViewSet, basename='order')

urlpatterns = [
    # загрузка товаров из yaml
    # регистрация
    # список товаров
    # карточка товара (поиск товаров)
    path('api/v1/', include(router.urls)),
    # вход
    path('api/v1/user/login', obtain_auth_token, name='login'),


    # корзина
    # path('api/v1/basket', views.BasketView.as_view(), name='basket'),


    # path('partner/state', PartnerState.as_view(), name='partner-state'),

    # заказы
    # path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),

    # path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    # path('user/details', AccountDetails.as_view(), name='user-details'),
    # path('user/contact', ContactView.as_view(), name='user-contact'),
    # path('user/password_reset', reset_password_request_token, name='password-reset'),
    # path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),

    # path('categories', CategoryView.as_view(), name='categories'),

    # path('shops', ShopView.as_view(), name='shops'),





    # заказ
    # path('order', OrderView.as_view(), name='order'),


    # Список товаров
    # Подтверждение заказа
    # Спасибо за заказ


    path('admin/', admin.site.urls),
]
