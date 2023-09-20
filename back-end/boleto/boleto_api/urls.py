from django.urls import path
from .views import *
urlpatterns = [
    path("users",UserAPI.as_view(),name='sign-up'),
    path("users/<str:username>",UserAPI.as_view(),name='user-info'),
    path("auth",AuthenticationAPI.as_view(),name='sign-in'),
    path("auth/logout",LogoutAPI.as_view(), name='user-logout'),
    path("movies",MoviesAdminAPI.as_view(),name='movies-api'),
    path("movies/update/<int:id>",MoviesAdminAPI.as_view(),name="update-movie"),
    path("movies/all",MoviesViewAPI.as_view(),name='all-movies'),
    path("movies/<int:id>", MoviesViewAPI.as_view(), name="specific-movie"),
    path("theaters",TheaterAdminAPI.as_view(),name="all-theaters"),
    path("theaters/<int:id>",TheaterAdminAPI.as_view(),name="all-theaters"),
    path("theaters/movie/<int:movie_id>",TheaterMovieApi.as_view(),name='theater-api'),
    path("seats",SeatsView.as_view(),name='seats-api'),
    path("seats/delete/<int:id>",SeatsView.as_view(),name='seats-api'),
    path("seats/all/<int:id>",TheaterSeats.as_view(),name='seats-intheater'),
    path("booking",BookingView.as_view(),name='bookingsummary-api'),
    path("booking/<int:id>",BookingView.as_view(),name='delete-booking-summary-api'),
    path("booking/<int:id>/seats/<int:seat_id>",BookingRemoveSeatAPI.as_view(),name='delete-booked-seat')
    
]
