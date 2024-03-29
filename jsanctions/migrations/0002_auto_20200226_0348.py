# Generated by Django 2.2.5 on 2020-02-26 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jsanctions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="city",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="city"),
        ),
        migrations.AlterField(
            model_name="address",
            name="country_description",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="country description"),
        ),
        migrations.AlterField(
            model_name="address",
            name="place",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="place"),
        ),
        migrations.AlterField(
            model_name="address",
            name="po_box",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="p.o. box"),
        ),
        migrations.AlterField(
            model_name="address",
            name="region",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="region"),
        ),
        migrations.AlterField(
            model_name="address",
            name="street",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="street"),
        ),
        migrations.AlterField(
            model_name="address",
            name="zip_code",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="zip code"),
        ),
        migrations.AlterField(
            model_name="birthdate",
            name="city",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="city"),
        ),
        migrations.AlterField(
            model_name="birthdate",
            name="country_description",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="country description"),
        ),
        migrations.AlterField(
            model_name="birthdate",
            name="place",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="place"),
        ),
        migrations.AlterField(
            model_name="birthdate",
            name="region",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="region"),
        ),
        migrations.AlterField(
            model_name="birthdate",
            name="zip_code",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="zip code"),
        ),
        migrations.AlterField(
            model_name="citizenship",
            name="country_description",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="country description"),
        ),
        migrations.AlterField(
            model_name="citizenship",
            name="region",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="region"),
        ),
        migrations.AlterField(
            model_name="eucombinedsanctionslist",
            name="global_file_id",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="global file id"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="country_description",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="country description"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="identification_type_description",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="identification type code"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="issued_by",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="issued by"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="latin_number",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="latin number"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="name_on_document",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="name on document"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="number",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="number"),
        ),
        migrations.AlterField(
            model_name="identification",
            name="region",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="region"),
        ),
        migrations.AlterField(
            model_name="namealias",
            name="first_name",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="first name"),
        ),
        migrations.AlterField(
            model_name="namealias",
            name="function",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="function"),
        ),
        migrations.AlterField(
            model_name="namealias",
            name="last_name",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="last name"),
        ),
        migrations.AlterField(
            model_name="namealias",
            name="middle_name",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="middle name"),
        ),
        migrations.AlterField(
            model_name="namealias",
            name="title",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="namealias",
            name="whole_name",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="whole name"),
        ),
        migrations.AlterField(
            model_name="regulation",
            name="number_title",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="number title"),
        ),
        migrations.AlterField(
            model_name="regulation",
            name="organisation_type",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="organization type"),
        ),
        migrations.AlterField(
            model_name="regulation",
            name="programme",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="programmer"),
        ),
        migrations.AlterField(
            model_name="regulation",
            name="regulation_type",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="regulation type"),
        ),
        migrations.AlterField(
            model_name="regulationsummary",
            name="number_title",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="number title"),
        ),
        migrations.AlterField(
            model_name="sanctionentity",
            name="designation_details",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="designation details"),
        ),
        migrations.AlterField(
            model_name="sanctionentity",
            name="eu_reference_number",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="EU reference number"),
        ),
        migrations.AlterField(
            model_name="sanctionentity",
            name="united_nation_id",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="United Nation identifier"),
        ),
        migrations.AlterField(
            model_name="subjecttype",
            name="code",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="code"),
        ),
    ]
