from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from shop.forms import ContactRequestForm, OrderForm
from shop.models import Watch, Brand, Favorite, Comment, CartItem, OrderItem


def catalog(request):

    watches = Watch.objects.exclude(slug__isnull=True).exclude(slug='')


    sort_by = request.GET.get('sort', 'date')
    filter_param = request.GET.get('filter', '')

    sort_options = {
        'date': '-added_at',
        'views': '-views',
    }
    sort_field = sort_options.get(sort_by, sort_options['date'])

    if filter_param:
        watches = watches.filter(brand__name__icontains=filter_param)

    watches_count = watches.count()
    all_brands = Brand.objects.all()

    news_list = watches.filter(in_stock=True).order_by(sort_field, 'id')
    paginator = Paginator(news_list, 6)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'watches': page_obj,
        'watches_count': watches_count,
        'all_brands': all_brands,
        'page_obj': page_obj,
        'sort': sort_by,
        'filter': filter_param,
    }

    return render(request, 'catalog.html', context)

def item_detail(request, slug):
    watch = get_object_or_404(Watch, slug=slug)
    all_brands = Brand.objects.all()

    ip_address = request.META.get('REMOTE_ADDR')
    is_favourite = Favorite.objects.filter(watch=watch, ip_address=ip_address).exists()

    watch.views += 1
    watch.save()

    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")
        if name and message:
            try:
                Comment.objects.create(
                    watch=watch,
                    name=name,
                    message=message
                )
            except Exception as e:
                print(f"Error saving comment: {e}")
            return redirect(request.path)

    context = {
        "watch": watch,
        "all_brands": all_brands,
        "favourite_ips": watch.favourites_count,
        "is_favourite": is_favourite,
        "comments": watch.comments.all(),
    }

    return render(request, 'item_detail.html', context)

def sort_by_brand(request, slug):

    brand = get_object_or_404(Brand, slug=slug)
    watches = Watch.objects.filter(brand=brand, in_stock=True)
    all_brands = Brand.objects.all()

    context = {
        'watches': watches,
        'filter': f"Brand: {brand.name}",
        'all_brands': all_brands,
    }

    return render(request, 'sort_by_brand.html', context)

def about(request):
    all_brands = Brand.objects.all()
    context = {
        'title': 'About Us',
        'description': (
            'Watch Shop is your gateway to the world of exquisite timepieces. '
            'We’re passionate about blending precision with style, curating a collection of luxury watches from iconic brands. '
            'Our mission is to make your journey to the perfect watch seamless and inspiring. '
            'With a sleek, user-friendly catalog and intuitive design, we bring elegance to every click. '
            'Whether it’s a timeless classic for the boardroom or a bold statement piece, Watch Shop offers watches that reflect your unique story. '
            'We value your trust and strive for excellence, delivering not just timepieces, but the moments they capture. '
            'Join us and discover time redefined!'
        ),
        'contacts': {
            'email': 'info@watchshop.com',
            'phone': '+49 (30) 1234-5678',
            'address': 'Berlin, Hauptstrasse 10',
        },
        'latitude': 52.5200,
        'longitude': 13.4050,
        'company_name': 'Watch Shop',
        'all_brands': all_brands,
    }
    return render(request, 'about.html', context=context)

def contact_us(request):
    all_brands = Brand.objects.all()
    success = False

    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            form.save()
            success = True  # Устанавливаем флаг успеха
            form = ContactRequestForm()  # Очищаем форму после отправки
        else:
            success = False
    else:
        form = ContactRequestForm()

    context = {
        'form': form,
        'all_brands': all_brands,
        'success': success,
    }
    return render(request, 'contact.html', context)

def cart_add(request, slug):
    watch = get_object_or_404(Watch, slug=slug)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_item, created = CartItem.objects.get_or_create(
        watch=watch, session_key=session_key, defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('shop:cart_detail')

def cart_remove(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, session_key=request.session.session_key)
    cart_item.delete()
    return redirect('shop:cart_detail')

def cart_detail(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = CartItem.objects.filter(session_key=session_key)
    total_price = sum(item.total_price for item in cart_items)
    all_brands = Brand.objects.all()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'all_brands': all_brands,
    }
    return render(request, 'cart_detail.html', context)

def order_create(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = CartItem.objects.filter(session_key=session_key)
    if not cart_items:
        return redirect('shop:catalog')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.session_key = session_key
            order.save()
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    watch=item.watch,
                    quantity=item.quantity,
                    price=item.watch.price
                )
            cart_items.delete()
            return redirect('shop:order_success')
    else:
        form = OrderForm()

    total_price = sum(item.total_price for item in cart_items)
    all_brands = Brand.objects.all()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'all_brands': all_brands,
    }
    return render(request, 'order_create.html', context)

def order_success(request):
    all_brands = Brand.objects.all()
    context = {
        'title': 'Order Successful',
        'message': 'Thank you for your order! We will contact you soon.',
        'all_brands': all_brands,
    }
    return render(request, 'order_success.html', context)
