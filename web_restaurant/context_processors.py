from reservations.forms import ReservationForm


# Активный пункт меню
def nav_active(request):
    current_url_name = request.resolver_match.url_name if request.resolver_match else None
    current_url_namespace = request.resolver_match.namespace if request.resolver_match else None
    current_full_path = request.get_full_path()

    # Якоря About
    has_anchor = '#' in current_full_path
    current_anchor = current_full_path.split('#')[1] if has_anchor else None
    return {
        'current_url_name': current_url_name,
        'current_url_namespace': current_url_namespace,
        'current_full_path': current_full_path,
        'current_anchor': current_anchor,
    }


def reservation_form_context(request):
    """
    Добавляет форму бронирования с капчей в контекст всех шаблонов
    """
    return {
        'reservation_form': ReservationForm()
    }
