# Generated by Django 4.2.9 on 2024-03-19 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_notification_periodicallynotification_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminTelegramUsers",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.CharField()),
                ("name", models.CharField(max_length=100)),
            ],
        ),
    ]