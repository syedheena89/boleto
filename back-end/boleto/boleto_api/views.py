import queue
from tokenize import TokenError
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.paginator import Paginator
from rest_framework import status
from .serializers import *
from django.db.models import Q
from django.db.models import Sum

# Create your views here.


class UserAPI(APIView):
    # For the signup new user
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Äccount created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # To get the particular user detail

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user).data
            return Response(serializer, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # # To update the particular user detail

    def put(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        update_serializer = UserUpdateSerializer(user, data=request.data)

        if update_serializer.is_valid():
            # Validate and save the updated data
            update_serializer.save()
            return Response(
                {"message": "User details updated successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # To Remove the particular User
    def delete(self, request, username):
        try:
            user = User.objects.get(username=username)
            user.delete()  # Delete the user
            return Response(
                {"message": "User deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AuthenticationAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data
            token = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "login done",
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # #To logout particular user


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            # Getting the Refresh Token
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            if hasattr(token, "blacklist"):
                token.blacklist()
            else:
                # version of rest_framework_simplejwt does not support blacklist(),
                # you can manually revoke the token by invalidating it.
                token["jti"] = "revoked"
                token["exp"] = 0
                token["token_type"] = "refresh"

            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )

        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging

            logging.error(f"Error during logout: {str(e)}")
            return Response(
                {"error": "Unable to logout. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MoviesViewAPI(APIView):
    #  get the movie list display according to the filters
    def get(self, request, id=None):
        # To get the details of the specific movie
        if id:
            try:
                movie = Movie.objects.get(id=id)
                serializer = MovieSerializer(movie).data
                return Response(serializer, status=status.HTTP_200_OK)
            except Movie.DoesNotExist:
                return Response(
                    {"message", "Movie doesnt exists."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        query = request.GET.get("query", None)
        rating = request.GET.get("rating", None)
        genre = request.GET.get("genre", None)
        language = request.GET.get("language", None)
        page_no = request.GET.get("page", None)
        allMovies = Movie.objects.all().order_by("-id")

        if query:
            allMovies = allMovies.filter(
                Q(title__icontains=query | queue(description__icontains=query))
            )

        if rating:
            allMovies = allMovies.filter(rating__gte=int(rating))

        if genre:
            allMovies = allMovies.filter(genre__icontains=genre)

        if language:
            allMovies = allMovies.filter(
                Q (language__in=language.split("|")) | Q (language__icontains=language)
            )
        paginate = Paginator(allMovies, 8)
        page = paginate.get_page(page_no)
        page_data = page.object_list
        serializer = MovieSerializer(page_data, many=True).data

        return Response(
            {
                "count": allMovies.count(),
                "total_page": paginate.num_pages,
                "next": page.has_next(),
                "previous": page.has_previous(),
                "data": serializer,
            },
            status=status.HTTP_200_OK,
        )


class MoviesAdminAPI(APIView):
    permission_classes = [IsAdminUser]

    # POST (admin only: add movie)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT (admin only: update movie),

    def put(self, request, id):
        try:
            movie = Movie.objects.get(id=id)
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateMovieSerializer(instance=movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Movie details updated successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #  DELETE (admin only: delete movie)

    def delete(self, request, id):
        try:
            movie = Movie.objects.get(id=id)
            movie.delete()  # Delete the movie
            return Response(
                {"message": "Movie deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Movie.DoesNotExist:
            return Response(
                {"error": "Movie not Found"}, status=status.HTTP_404_NOT_FOUND
            )


class TheaterAdminAPI(APIView):
    permission_classes = [IsAdminUser]

    # To add the theater

    def post(self, request):
        data = request.data
        print(data)
        serializer = TheaterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # To Update the theater

    def put(self, request, id=None):
        try:
            theater = Theater.objects.get(id=id)
        except Theater.DoesNotExist:
            return Response(
                {"error": "Theater not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TheaterSerializer(theater, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        try:
            theater = Theater.objects.get(id=id)
            theater.delete()
            return Response(
                {"message": "Theater has been removed"}, status=status.HTTP_200_OK
            )
        except Theater.DoesNotExist:
            return Response(
                {"error": "Theater not found"}, status=status.HTTP_404_NOT_FOUND
            )
        


class TheaterMovieApi(APIView):
    # To get all the theaters for the particular movie

    def get(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            print(movie)
            serializer = MovieSerializer(movie).data
            theaters = Theater.objects.filter(movie=movie_id).values()
            serializer["theaters"] = list(theaters)
            return Response(serializer, status=status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response(
                {"message": "Theater not found"}, status=status.HTTP_404_NOT_FOUND
            )


class SeatsView(APIView):
    # To add the seat in the theater

    def post(self, request):
        serializer = SeatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update the seat in the theater

    def put(self, request, id=None):
        try:
            seat = Seat.objects.get(id=id)
        except Seat.DoesNotExist:
            return Response(
                {"message": "Seat not Found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = SeatSerializer(seat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Seat updated successfully"}, status=status.HTTP_200_OK
            )

        # Delete the particular seat in the theater

    def delete(self, request, id=None):
        try:
            print("Hi i am in the delete")
            seat = Seat.objects.get(id=id)
            seat.delete()
            return Response(
                {"message": "Seat deleted successfully"}, status=status.HTTP_200_OK
            )
        except Seat.DoesNotExist:
            return Response(
                {"message": "seat not found"}, status=status.HTTP_404_NOT_FOUND
            )



class TheaterSeats(APIView):
    # Get the seats for the particular theater

    def get(self, request, id):
        try:
            theater = Theater.objects.get(id=id)
            serializer = TheaterSerializer(theater).data
            seats = (
                Seat.objects.filter(theater=id)
                .order_by(
                    "id",
                )
                .values("id", "seat_number", "is_reserved", "category", "price")
            )
            serializer["seats"] = list(seats)
            return Response(serializer, status=status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response(
                {"message": "Theater not found"}, status=status.HTTP_404_NOT_FOUND
            )


class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    # to get the detail of the booking

    def get(self, request, id=None):
        if id:
            try:
                booking = Booking.objects.get(user=request.user.id, id=id)
                serializer = BookingSerializer(booking).data
                return Response(serializer, status=status.HTTP_200_OK)
            except Booking.DoesNotExist:
                return Response(
                    {"message": "Booking not Found"}, status=status.HTTP_404_NOT_FOUND
                )
        bookings = Booking.objects.select_related("movie").filter(user=request.user.id)
        serializer = BookingSerializer(bookings, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request):
        seats = request.data.get("seats", [])
        allSeats = Seat.objects.filter(id__in=seats)
        is_reserved = allSeats.filter(is_reserved__in=[True]).exists()
        if is_reserved:
            return Response(
                {"error": "Some seats are reserved"}, status=status.HTTP_400_BAD_REQUEST
            )
        data = request.data
        data["user"] = request.user.id
        total_price = allSeats.aggregate(sum=Sum("price"))
        data["total_cost"] = total_price["sum"]
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            Seat.objects.filter(id__in=seats).update(is_reserved=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            booking = Booking.objects.get(id=id, user=request.user.id)
            unreserved = booking.seats.values_list("id", flat=True)
            Seat.objects.filter(id__in=list(unreserved)).update(is_reserved=False)

            booking.delete()
            return Response(
                {"message": "Booking has been cancelled"}, status=status.HTTP_200_OK
            )
        except Booking.DoesNotExist:
            return Response(
                {"message": "Booking doesn't exists"}, status=status.HTTP_404_NOT_FOUND
            )


class BookingRemoveSeatAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, seat_id):
        try:
            try:
                booking = Booking.objects.get(user=request.user.id, pk=id)
            except Booking.DoesNotExist:
                return Response(
                    {"message": "Bookinf doesnt exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                seat = Seat.objects.get(pk=seat_id)
                booking.seats.remove(seat)
                booking.total_cost -= seat.price
                seat.is_reserved = False
            except Seat.DoesNotExist:
                return Response(
                    {"messsage": "Seat not found"}, status=status.HTTP_404_NOT_FOUND
                )
            booking.save()
            seat.save()
            if booking.seats.count() < 1:
                booking.delete()
            return Response(
                {"Message": "Seat has been cancelled"}, status=status.HTTP_200_OK
            )
        except Booking.DoesNotExist:
            return Response(
                {"message": "Bookinf doesnt exists"}, status=status.HTTP_404_NOT_FOUND
            )
