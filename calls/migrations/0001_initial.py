# Generated by Django 5.0.3 on 2024-04-23 20:35

import calls.models.mixins.created_mixin
import calls.models.mixins.updated_mixin
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL("create schema if not exists communications;"),
        migrations.CreateModel(
            name="Operator",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        db_index=True, max_length=100, unique=True, verbose_name="title"
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, default="", max_length=2500, verbose_name="description"
                    ),
                ),
                ("foundation_date", models.DateField(verbose_name="foundation date")),
            ],
            options={
                "verbose_name": "mobile operator",
                "verbose_name_plural": "mobile operators",
                "db_table": '"communications"."operator"',
                "ordering": ("title", "foundation_date"),
            },
            bases=(
                calls.models.mixins.created_mixin.CreatedMixin,
                calls.models.mixins.updated_mixin.UpdatedMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="OperatorSubscriber",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "operator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="calls.operator",
                        verbose_name="operator",
                    ),
                ),
            ],
            options={
                "verbose_name": "relation of operator and subscriber",
                "verbose_name_plural": "relations of operator and subscriber",
                "db_table": '"communications"."operator_subscriber"',
            },
        ),
        migrations.CreateModel(
            name="Subscriber",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("birth_date", models.DateField(verbose_name="birth day")),
                (
                    "passport",
                    models.CharField(
                        help_text='Passport number has a format like "0000-000000"',
                        max_length=11,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{4}-\\d{6}$",
                                'incorrect passport number format (example: "0000-000000")',
                            )
                        ],
                        verbose_name="passport number",
                    ),
                ),
                (
                    "operators",
                    models.ManyToManyField(
                        blank=True,
                        related_name="+",
                        through="calls.OperatorSubscriber",
                        to="calls.operator",
                        verbose_name="operators",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriber",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "subscriber",
                "verbose_name_plural": "subscribers",
                "db_table": '"communications"."subscriber"',
            },
            bases=(
                calls.models.mixins.created_mixin.CreatedMixin,
                calls.models.mixins.updated_mixin.UpdatedMixin,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="operatorsubscriber",
            name="subscriber",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="calls.subscriber",
                verbose_name="subscriber",
            ),
        ),
        migrations.AddField(
            model_name="operator",
            name="subscribers",
            field=models.ManyToManyField(
                blank=True,
                related_name="+",
                through="calls.OperatorSubscriber",
                to="calls.subscriber",
                verbose_name="subscribers",
            ),
        ),
        migrations.CreateModel(
            name="SubscriberCall",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        blank=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("start", models.DateTimeField(verbose_name="start time")),
                ("duration", models.DurationField(verbose_name="duration")),
                (
                    "caller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="made_calls",
                        to="calls.subscriber",
                        verbose_name="caller",
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_calls",
                        to="calls.subscriber",
                        verbose_name="call receiver",
                    ),
                ),
            ],
            options={
                "verbose_name": "subscriber call",
                "verbose_name_plural": "subscribers calls",
                "db_table": '"communications"."subscriber_call"',
            },
            bases=(
                calls.models.mixins.created_mixin.CreatedMixin,
                calls.models.mixins.updated_mixin.UpdatedMixin,
                models.Model,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="operatorsubscriber",
            unique_together={("operator", "subscriber")},
        ),
        migrations.AddConstraint(
            model_name="subscribercall",
            constraint=models.CheckConstraint(
                check=models.Q(("caller_id", models.F("receiver_id")), _negated=True),
                name="check_not_equal_caller_and_receiver",
            ),
        ),
    ]
