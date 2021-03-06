# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-07-03 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('symposion_proposals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TalkProposal',
            fields=[
                ('proposalbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='symposion_proposals.ProposalBase')),
                ('audience_level', models.IntegerField(choices=[(1, b'Principiante'), (3, b'Intermedia'), (2, b'Avanzada')])),
                ('youtube_url', models.URLField(blank=True, default=b'', null=True)),
                ('recording_release', models.BooleanField(default=True, help_text=b'Al enviar tu propuesta, le est\xc3\xa1s dando permiso a los organizadores de la conferencia para grabar, editar y transmitir audio y/o video de tu presentaci\xc3\xb3n. Si no estas de acuerdo con esto, no chequees este recuadro.')),
            ],
            options={
                'verbose_name': 'Propuesta de charla/taller',
                'verbose_name_plural': 'Propuestas de charlas/talleres',
            },
            bases=('symposion_proposals.proposalbase',),
        ),
    ]
