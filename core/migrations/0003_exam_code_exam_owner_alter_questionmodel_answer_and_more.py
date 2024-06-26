# Generated by Django 4.2.7 on 2024-06-14 22:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_exam_studentprofile_questionmodel_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='code',
            field=models.CharField(max_length=8, unique=True),  # Ensure unique
        ),
        migrations.AddField(
            model_name='exam',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.studentprofile'),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='answer',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='option1',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='option2',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='option3',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='question',
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name='TheoryQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('question', models.TextField()),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.exam')),
            ],
        ),
    ]
