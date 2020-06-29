# Generated by Django 3.0.7 on 2020-06-29 03:50

from django.db import migrations
import jutil.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('jsanctions', '0003_auto_20200626_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='city'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country_description',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='country description'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country_iso2_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=3, verbose_name='country'),
        ),
        migrations.AlterField(
            model_name='address',
            name='place',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='place'),
        ),
        migrations.AlterField(
            model_name='address',
            name='po_box',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='p.o. box'),
        ),
        migrations.AlterField(
            model_name='address',
            name='region',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='region'),
        ),
        migrations.AlterField(
            model_name='address',
            name='regulation_language',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=5, verbose_name='regional language'),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='street'),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='zip code'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='calendar_type',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=32, verbose_name='calendar type'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='city',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='city'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='country_description',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='country description'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='country_iso2_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=3, verbose_name='country'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='place',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='place'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='region',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='region'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='regulation_language',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=5, verbose_name='regional language'),
        ),
        migrations.AlterField(
            model_name='birthdate',
            name='zip_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='zip code'),
        ),
        migrations.AlterField(
            model_name='citizenship',
            name='country_description',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='country description'),
        ),
        migrations.AlterField(
            model_name='citizenship',
            name='country_iso2_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=3, verbose_name='country'),
        ),
        migrations.AlterField(
            model_name='citizenship',
            name='region',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='region'),
        ),
        migrations.AlterField(
            model_name='citizenship',
            name='regulation_language',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=5, verbose_name='regional language'),
        ),
        migrations.AlterField(
            model_name='eucombinedsanctionslist',
            name='global_file_id',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='global file id'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='country_description',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='country description'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='country_iso2_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=3, verbose_name='issued by'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='identification_type_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=32, verbose_name='identification type code'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='identification_type_description',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='identification type code'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='issued_by',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='issued by'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='latin_number',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='latin number'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='name_on_document',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='name on document'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='number',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='number'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='region',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='region'),
        ),
        migrations.AlterField(
            model_name='identification',
            name='regulation_language',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=5, verbose_name='regional language'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='first_name',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='function',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='function'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='last_name',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='middle_name',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='middle name'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='name_language',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=5, verbose_name='name language'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='regulation_language',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=5, verbose_name='regulation language'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='title',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='namealias',
            name='whole_name',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='whole name'),
        ),
        migrations.AlterField(
            model_name='regulation',
            name='number_title',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='number title'),
        ),
        migrations.AlterField(
            model_name='regulation',
            name='organisation_type',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='organization type'),
        ),
        migrations.AlterField(
            model_name='regulation',
            name='programme',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='programmer'),
        ),
        migrations.AlterField(
            model_name='regulation',
            name='regulation_type',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='regulation type'),
        ),
        migrations.AlterField(
            model_name='regulationsummary',
            name='number_title',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='number title'),
        ),
        migrations.AlterField(
            model_name='regulationsummary',
            name='regulation_type',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=32, verbose_name='regulation type'),
        ),
        migrations.AlterField(
            model_name='remark',
            name='text',
            field=jutil.modelfields.SafeTextField(blank=True, verbose_name='text'),
        ),
        migrations.AlterField(
            model_name='sanctionentity',
            name='designation_details',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='designation details'),
        ),
        migrations.AlterField(
            model_name='sanctionentity',
            name='eu_reference_number',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='EU reference number'),
        ),
        migrations.AlterField(
            model_name='sanctionentity',
            name='united_nation_id',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='United Nation identifier'),
        ),
        migrations.AlterField(
            model_name='subjecttype',
            name='classification_code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=32, verbose_name='classification code'),
        ),
        migrations.AlterField(
            model_name='subjecttype',
            name='code',
            field=jutil.modelfields.SafeCharField(blank=True, default='', max_length=512, verbose_name='code'),
        ),
    ]
