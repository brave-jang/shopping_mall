from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Coupon
from .forms import AddCouponForm


@require_POST
def add_coupon(request):
    now = timezone.now()
    form = AddCouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']

        try:
            coupon = Coupon.objects.get(code__iexact=code, use_form__lte=now, use_to__gte=now, active=True) # iexcat : 대,소문자 가리지 않고 일치하는 문자
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None

    return redirect('cart:detail')