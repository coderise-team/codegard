import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_elo_rating_elohistory"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="elohistory",
            options={"ordering": ["-created_at"]},
        ),
        migrations.RenameField(
            model_name="elohistory",
            old_name="new_rating",
            new_name="rating",
        ),
        migrations.RenameField(
            model_name="elohistory",
            old_name="timestamp",
            new_name="created_at",
        ),
        migrations.RemoveField(
            model_name="elohistory",
            name="contest",
        ),
        migrations.RemoveField(
            model_name="elohistory",
            name="opponent",
        ),
        migrations.RemoveField(
            model_name="elohistory",
            name="old_rating",
        ),
        migrations.RemoveField(
            model_name="elohistory",
            name="delta",
        ),
        migrations.AlterField(
            model_name="elohistory",
            name="rating",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="elohistory",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="elohistory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="elo_history",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="elohistory",
            index=models.Index(
                fields=["user", "-created_at"], name="users_elohi_user_id_e6b7f4_idx"
            ),
        ),
    ]
