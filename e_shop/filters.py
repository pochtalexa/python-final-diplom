from django_filters import rest_framework as filters
from e_shop.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, Order, OrderItem


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    category = filters.CharFilter(field_name="category__name", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('name', 'category')
