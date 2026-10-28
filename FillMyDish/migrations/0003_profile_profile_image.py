from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FillMyDish', '0002_connection'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, upload_to='profile_images/'),
        ),
    ]
