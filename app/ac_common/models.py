# coding: utf-8
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from djcelery.models import PeriodicTask, IntervalSchedule


class TaskScheduler(models.Model):
    periodic_task = models.ForeignKey(PeriodicTask)

    @staticmethod
    def schedule(task_path, minutes=0, task_name="", kwargs=None):
        if minutes < 1:
            raise Exception("Nope")

        intervals = IntervalSchedule.objects.filter(period='minutes', every=minutes)

        if intervals:
            interval = intervals[0]
        else:
            interval = IntervalSchedule.objects.create(period='minutes', every=minutes)

        task = PeriodicTask(name=task_name, task=task_path, interval=interval)
        task.kwargs = kwargs if kwargs else '{}'
        task.save()

        return TaskScheduler.objects.create(periodic_task=task)

    def terminate(self):
        task = self.periodic_task
        task.enabled = False
        task.save(force_update=True)  # so that celery-beat sees the change (post-save signal)

        self.delete()
        task.delete()

    @staticmethod
    def terminate_by_task_name(task_name):
        task = TaskScheduler.objects.get(periodic_task__name=task_name)
        task.terminate()


class Category(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    name = models.TextField()
    parent_id = models.IntegerField(blank=True)  # Without self-FK. I'm leaving it for potential future use
    parent_name = models.TextField(blank=True)
    provider = models.IntegerField(choices=settings.PROVIDERS, default=settings.PROVIDER_ALLEGRO)

    def __repr__(self):
        if self.parent_name:
            return "Category: %s > %s" % (self.parent_name, self.name)
        else:
            return "Category: %s" % self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_admin, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_admin=is_admin,
            is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    AUTH_LOCAL = 0
    AUTH_FACEBOOK = 1

    AUTH_TYPES = (
        (AUTH_LOCAL, 'Local'),
        (AUTH_FACEBOOK, 'Facebook'),
    )

    email = models.CharField(max_length=80, unique=True)
    auth_type = models.PositiveSmallIntegerField(choices=AUTH_TYPES, default=0)

    auth_token = models.CharField(max_length=128, blank=True)
    auth_expiry_date = models.DateTimeField(blank=True, null=True)

    reset_token = models.CharField(max_length=128, blank=True, null=True)
    reset_token_expiry_date = models.DateTimeField(blank=True, null=True)

    allegro_user_id = models.CharField(max_length=60, blank=True)
    allegro_user_name = models.CharField(max_length=60, blank=True)

    ebay_user_id = models.CharField(max_length=60, blank=True)
    ebay_user_name = models.CharField(max_length=60, blank=True)

    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return "[{}] Allegro: '{}', Ebay: '{}'".format(
            self.email, self.allegro_user_name, self.ebay_user_name
        )
