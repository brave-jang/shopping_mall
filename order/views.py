from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import *


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        # 입력 받은 정보를 후처리
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.get_discount_total()
                order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], qauntity=item['quantity'])
            cart.clear()
            return render(request, 'order/created.html', {'order':order})
    else:
        # 주문자 정보를 입력 받는 페이지
        form = OrderCreateForm()
    return render(request, 'order/create.html', {'cart':cart, 'form':form})

# JS가 동작하지 않는 환경에서도 주문은 가능해야 함.
def order_complete(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/created.html', {'order':order})


from django.views.generic.base import View
from django.http import JsonResponse

class OrderCreateAjaxView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)
        
        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.get_discount_total()
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], qauntity=item['quantity'])
            cart.clear()
            data = {
                "order_id" : order.id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=404)


class OrderCheckoutAjaxView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        amount = request.POST.get('amount')

        try:
            merchant_order_id = OrderTransaction.objects.create_new(
                order=order,
                amount=amount,
            )
        except:
            merchant_order_id = None
        
        if merchant_order_id is not None:
            data = {
                'works':True,
                'merchant_id':merchant_order_id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)


# 결제 완료 된 후 후처리
class OrderImpAjaxView(View):
    def post (self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)

        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            trans = OrderTransaction.objects.get(
                order = order,
                merchant_order_id = merchant_id,
                amount = amount,
            )
        except:
            trans = None
        
        if trans is not None:
            trans.transation_id = imp_id
            trans.save()
            order.paid = True
            order.save()

            data = {
                "works":True
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)
