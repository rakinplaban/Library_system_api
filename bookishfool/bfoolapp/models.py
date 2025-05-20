from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    penalty_point = models.IntegerField(default=0)  # spelling corrected

    def __str__(self):
        return f"{self.user.username}'s profile"

# Automatically create or update UserProfile on User creation/update
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class Category(models.Model):  # use singular 'Category' as model name
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):  # use singular 'Author' as model name
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Book(models.Model):  # use singular 'Book' as model name
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author, related_name='books_has_authors')  # fixed reverse relationship
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    borrows = models.ManyToManyField(User, related_name='borrowed_books', through='Borrow', blank=True)

    def __str__(self):
        return self.title


class Borrow(models.Model):  # use singular 'Borrow'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrow_date or (timezone.now().date()) + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
