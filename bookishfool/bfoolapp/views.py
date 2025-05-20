from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta
from .serializers import *
from .models import *
# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class BookListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permission() for permission in [AllowAny]]  # Anyone can view
        elif self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser]]  # Only admin can create
        return super().get_permissions()

    def get(self, request):
        queryset = Book.objects.all()

        author_id = request.query_params.get('author')
        category_id = request.query_params.get('category')

        if author_id:
            queryset = queryset.filter(authors__id=author_id)
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        serializer = BookSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            print("Validated Data:", serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Book, pk=pk)
    

    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        book = self.get_object(pk)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthorListCreateAPIView(APIView):
    def get(self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Author, pk=pk)

    def put(self, request, pk):
        author = self.get_object(pk)
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        author = self.get_object(pk)
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BorrowBookAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        active_borrows = Borrow.objects.filter(user=user, return_date__isnull=True)
        serializer = BorrowSerializer(active_borrows, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({'error': 'book_id is required.'}, status=400)

        book = get_object_or_404(Book, id=book_id)

        active_borrows = Borrow.objects.filter(user=user, return_date__isnull=True).count()
        if active_borrows >= 3:
            return Response({'error': 'You can only borrow up to 3 books at a time.'}, status=400)

        if book.available_copies < 1:
            return Response({'error': 'No available copies to borrow.'}, status=400)

        book.available_copies -= 1
        book.save()

        borrow = Borrow.objects.create(
            user=user,
            book=book,
            borrow_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )

        return Response({'message': f'You have borrowed "{book.title}". Return by {borrow.due_date}.'}, status=201)


class ReturnBookAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        user = request.user
        borrow_id = request.data.get('borrow_id')
        borrow = get_object_or_404(Borrow, id=borrow_id, user=user)

        if borrow.return_date:
            return Response({'error': 'Book already returned.'}, status=400)

        borrow.return_date = timezone.now().date()
        borrow.save()

        book = borrow.book
        book.available_copies += 1
        book.save()

        if borrow.return_date > borrow.due_date:
            late_days = (borrow.return_date - borrow.due_date).days
            user_profile = user.userprofile
            user_profile.penalty_point += late_days
            user_profile.save()
            return Response({'message': f'Book returned. {late_days} penalty point(s) added for late return.'})

        return Response({'message': 'Book returned successfully.'})


class UserPenaltyView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id):
        user = get_object_or_404(User, id=id)

        if request.user != user and not request.user.is_staff:
            raise PermissionDenied('Not authorized to view this user\'s penalties.')

        return Response({'username': user.username, 'penalty_points': user.userprofile.penalty_point})


