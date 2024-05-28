from typing import cast

from django.apps import apps
from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from subscribers.models import Subscriber
from rest_framework.authtoken.models import Token


class TokenStackedInline(admin.StackedInline):
    model = Token
    extra = 1


inlines = (TokenStackedInline,)


if apps.is_installed("calls"):

    class OperatorStackedInline(admin.StackedInline):
        model = cast(models.ManyToManyField, getattr(Subscriber, "operators")).through
        extra = 1

    inlines += (OperatorStackedInline,)


class SubscriberAdmin(UserAdmin):
    search_fields = ("full_name__startswith",)

    list_per_page = 25
    list_display = ("full_name", "birth_date", "passport")
    list_display_links = ("full_name",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "email",
                    "passport",
                    "birth_date",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "passport", "birth_date")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    inlines = inlines
