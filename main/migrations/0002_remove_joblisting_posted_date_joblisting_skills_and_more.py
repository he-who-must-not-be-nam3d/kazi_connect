# Generated by Django 5.1.4 on 2024-12-08 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='joblisting',
            name='posted_date',
        ),
        migrations.AddField(
            model_name='joblisting',
            name='skills',
            field=models.TextField(default='web developer', help_text='Comma-separated list of skills (e.g., Python, Django, SQL)'),
        ),
        migrations.AlterField(
            model_name='joblisting',
            name='employment_type',
            field=models.CharField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time')], max_length=50),
        ),
    ]