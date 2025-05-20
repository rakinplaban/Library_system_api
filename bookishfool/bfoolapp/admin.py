from django.contrib import admin
from .models import UserProfile, Category, Author, Book, Borrow

# -------------------------
# UserProfile Admin
# -------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'penalty_point']
    search_fields = ['user__username']


# -------------------------
# Category Admin
# -------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    search_fields = ['name']


# -------------------------
# Author Admin
# -------------------------
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']


# -------------------------
# Book Admin
# -------------------------
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'total_copies', 'available_copies']
    list_filter = ['category', 'authors']
    search_fields = ['title', 'description']
    filter_horizontal = ['authors']  # To choose multiple authors more easily


# -------------------------
# Borrow Admin
# -------------------------
@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'due_date', 'return_date']
    list_filter = ['borrow_date', 'due_date', 'return_date']
    search_fields = ['user__username', 'book__title']

