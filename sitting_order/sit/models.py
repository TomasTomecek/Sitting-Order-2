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
    # RGB color displayed on map
    color = models.CharField(max_length=6)
    comment = models.CharField(max_length=255, blank=True)
    parent_team = models.ForeignKey('self', related_name="children",
                                    blank=True, null=True)
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.leader)


class User(AbstractBaseUser):
    # firstname + lastname
    name = models.CharField(max_length=255)
    # translitared firstname + lastname
    name_tl = models.CharField(max_length=255)
    # some users have very common nicknames
    nickname = models.CharField(max_length=128, blank=True, null=True)
    # <kerberos name>@realm
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    team = models.ForeignKey(Team, related_name="members", blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    INTERN = 1
    HALF_TIME = 2
    FULL_TIME = 3
    OTHER = 4
    DEFAULT = 5
    STATUS_CHOICES = (
        (INTERN, 'Intern'),
        (HALF_TIME, 'Half time'),
        (FULL_TIME, 'Full time'),
        (OTHER, 'Other'),
        (DEFAULT, 'Default'),
    )
    employment_type = models.IntegerField(
        choices=STATUS_CHOICES, default=DEFAULT)

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
    image = models.CharField(max_length=255)
    number = models.IntegerField()

    def __unicode__(self):
        return u"%s: floor %d" % (self.building.name, self.number)

class Place(models.Model):
    """place on map"""
    floor = models.ForeignKey(Floor, null=True)
    lon = models.FloatField()
    lat = models.FloatField()
    seat = models.OneToOneField('Seat', null=True)

    def __unicode__(self):
        return u"%d: %s" % (self.floor, self.seat)

    def serialize(self):
        js = self.seat.serialize()

        js.update({
            'lon': self.lon,
            'lat': self.lat,
        })

        return js


class Seat(models.Model):
    """virtual seat where someone is sitting"""
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.number, self.user)

    def serialize(self):
        team = None
        is_leader = False
        if self.user.team:
            team = self.user.team.name
            if self.user.team.leader == self.user:
                is_leader = True
        return {
            'name': self.user.name,
            'team': team,
            'is_leader': is_leader,
        }