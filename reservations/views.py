from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ReservationForm
from .models import Reservation


@require_POST
@csrf_exempt
def create_reservation(request):
    form = ReservationForm(request.POST)

    if form.is_valid():
        reservation = Reservation(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data['phone'],
            guests=form.cleaned_data['guests'],
            visit_date=form.cleaned_data['visit_date'],
            visit_time=form.cleaned_data['visit_time'],
            special_request=form.cleaned_data['special_request']
        )
        reservation.save()

        return JsonResponse({
            'success': True,
            'message': 'Thank you! The administrator will contact you to confirm your reservation!'
        })
    else:
        errors = {}
        for field in form.errors:
            errors[field] = form.errors[field]
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Please correct the errors in the form:'
        })
