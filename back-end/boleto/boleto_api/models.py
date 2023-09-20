from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,username,password,**extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username,**extra_fields)
        user.set_password(password)
        user.save()
        return user
   
class User(AbstractBaseUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200,unique=True)
    username = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"

    objects =UserManager()

    def __str__(self):
        return self.username
    
    def has_perm(self,perm,obj=None):
        return self.is_superuser
    
    def has_module_perms(self,app_label):
        return self.is_superuser


class Movie(models.Model):
    title = models.CharField(max_length=255)
    director = models.CharField(max_length=225)
    genre = models.CharField(max_length=225)
    description = models.TextField()
    image = models.TextField()
    language = models.CharField(max_length=225)
    rating = models.FloatField()
    movie_length = models.IntegerField()
    release_date = models.DateTimeField(default=None,null=True)

    def __str__(self):
        return self.title

class Theater(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    movie_timing = models.DateTimeField(default=None,null=True)

    def __str__(self):
        return self.name
    
    
class Seat(models.Model):
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_reserved = models.BooleanField(default=False)
    category = models.CharField(max_length=200)
    price = models.FloatField(default=0.00)

    def __str__(self):
        return f"{self.theater.name} - {self.movie.title} - Seat{self.seat_number}"
    
class Booking(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    movie  = models.ForeignKey(Movie,on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    total_cost = models.FloatField(default=0.00)
    Booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

