from django.shortcuts import render
from .models import Event


def events_list(request):
    events = Event.objects.filter(is_active=True)
    context = {'events': events}
    return render(request, 'events/list.html', context)


def event_detail(request, event_id):
    ...
    return render(request, 'events/detail.html')
