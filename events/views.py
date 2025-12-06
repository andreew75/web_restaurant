from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from .models import Event


def events_list(request):
    events = Event.objects.filter(is_active=True).order_by('-date')

    paginator = Paginator(events, 3)
    page = request.GET.get('page')

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    context = {'events': events, 'paginator': paginator}

    return render(request, 'events/list.html', context)

