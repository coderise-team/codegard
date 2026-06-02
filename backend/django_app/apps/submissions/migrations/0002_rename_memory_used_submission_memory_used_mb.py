from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("submissions", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="memory_used",
            new_name="memory_used_mb",
        ),
    ]
