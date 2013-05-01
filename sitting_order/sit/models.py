# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User must have an email address and team.')

        user = self.model(
            email=UserManager.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Team(models.Model):
    name = models.CharField(max_length=128)
    # related is useless
    leader = models.OneToOneField("User", related_name="team_related")

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.leader)


class User(AbstractBaseUser):
    # <kerberos name>@realm
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    team = models.ForeignKey(Team, related_name="members", blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

class Building(models.Model):
    name = models.CharField(max_length=32)

class Floor(models.Model):
    building = models.ForeignKey(Building)

class Place(models.Model):
    floor = models.ForeignKey(Floor)
    lon = models.FloatField()
    lat = models.FloatField()

class Seat(models.Model):
    OCCUPIED = 1
    RESERVED = 2
    BLANK = 3
    STATUS_CHOICES = (
        (OCCUPIED, 'Occupied'),
        (RESERVED, 'Reserved'),
        (BLANK, 'Blank'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=BLANK)
    number = models.CharField(max_length=16)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
