from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework import viewsets
from main.models import Category, Product, ProductImage
from main.serializers import CategorySerializer, ProductSerializer, ProductImageSerializer
from .permissions import IsPostAuthor


# @api_view(['GET'])
# def categories(request):
#     categories = Category.objects.all()
#     serializer = CategorySerializer(categories, many=True)
#     return Response(serializer.data)
#
#
# class ProductListView(APIView):
#     def get(self, request):
#         products = Product.objects.all()
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         product = request.data
#         serializer = ProductSerializer(data=product)
#         if serializer.is_valid(raise_exception=True):
#             product_saved = serializer.save()
#         return Response(serializer.data)

class MyPaginationClass(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        for i in range(self.page_size):
            text = data[i]['text']
            data[i]['text'] = text[:15] + '...'
        return super().get_paginated_response(data)



class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]



# class ProductView(generics.ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#
# class ProductDetailView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#
# class ProductUpdateView(generics.UpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#
# class ProductDeleteView(generics.DestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = MyPaginationClass


    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsPostAuthor, ]
        else:
            permissions = [IsAuthenticated,  ]
        return [permission() for permission in permissions]

    def get_queryset(self):
        queryset = super().get_queryset()
        days_count = int(self.request.query_params('days', 0))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset


    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductImageView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}



