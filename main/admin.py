from django.contrib import admin

# Register your models here.
from main.models import Product, Category, ProductImage, Comment, Like


class ProductImageInLine(admin.TabularInline):
    model = ProductImage
    max_num = 5
    min_num = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInLine, ]

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Like)
