# -*- coding: utf-8 -*-
import datetime
import json

from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template import Context, loader
from symposion.schedule.models import Slot, Day

from .forms import BecasForm

def becas(request):
    form_class = BecasForm

    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get(
                'nombre_completo')
            contact_email = request.POST.get(
                'email')
            form_content = request.POST.get('que_necesitas')

            # Email the profile with the
            # contact information
            template = loader.get_template('becas_email.txt')
            context = Context({
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            })
            content = template.render(context)

            email = EmailMessage(
                "[BECAS]Nueva beca requerida",
                content,
                "no-reply@python.org.ar",
                ['pyconar@listas.bitson.com.ar'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            messages.add_message(request, messages.INFO, u"""¡Gracias por tu solicitud!, nos pondremos en contacto a la brevedad para
 informarte de los pasos a seguir""")

            return redirect('becas')
        else:
            messages.add_message(request, messages.ERROR, u"""Por favor completa los campos correctamente""")

    return render(request, 'becas.html', {
        'form': form_class,
    })

AUDIENCE_LEVEL = {
    1: 'Inicial',
    2: 'Intermedio',
    3: 'Avanzado'
}

def schedule_json(request):
    slots = Slot.objects.filter(
        day__schedule__published=True,
        day__schedule__hidden=False
    ).order_by("start")

    protocol = request.META.get('HTTP_X_FORWARDED_PROTO', 'http')

    full_data = {}

    def create_day(slots, day):
        data = []

        for slot in slots.filter(day=day):
            slot_data = {
                "room": ", ".join(room["name"] for room in slot.rooms.values()),
                "rooms": [room["name"] for room in slot.rooms.values()],
                "day": day.date.strftime('%Y-%m-%d'),
                "start": slot.start_datetime.isoformat(),
                "end": slot.end_datetime.isoformat(),
                "duration": slot.length_in_minutes,
                "kind": slot.kind.label,
                "section": slot.day.schedule.section.slug,
                "conf_key": slot.pk,
                # TODO: models should be changed.
                # these are model features from other conferences that have forked symposion
                # these have been used almost everywhere and are good candidates for
                # base proposals
                #"license": "CC BY",
                "tags": "",
                #"released": True,
                "contact": [],


            }
            if hasattr(slot.content, "proposal"):
                import pdb;pdb.set_trace()
                slot_data.update({
                    "name": slot.content.title,
                    "audience_level": AUDIENCE_LEVEL[slot.content.proposal.audience_level],
                    "authors": [s.name for s in slot.content.speakers()],
                    "contact": [
                        s.email for s in slot.content.speakers()
                    ] if request.user.is_staff else ["redacted"],
                    "abstract": slot.content.abstract,
                    "description": slot.content.description,
                    "conf_url": "%s://%s%s" % (
                        protocol,
                        Site.objects.get_current().domain,
                        reverse("schedule_presentation_detail", args=[slot.content.pk])
                    ),
                    "cancelled": slot.content.cancelled,
                })
            else:
                slot_data.update({
                    "name": slot.content_override if slot.content_override else "Slot",
                })

            data.append(slot_data)

        return data

    for day in Day.objects.all():
        day_key = day.date.strftime('%Y-%m-%d')
        full_data[day_key] = create_day(slots, day)


    return HttpResponse(
        json.dumps({"schedule": full_data}),
        content_type="application/json"
    )
