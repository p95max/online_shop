from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from shop.forms import ContactRequestForm
from shop.models import Watch, Brand, Favorite, Comment

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
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:contact_success')
    else:
        form = ContactRequestForm()

    context = {
        'title': 'Contact Us',
        'form': form,
        'all_brands': all_brands,
    }
    return render(request, 'contact.html', context)

def contact_success(request):
    all_brands = Brand.objects.all()
    context = {
        'title': 'Message Sent',
        'message': 'Thank you for contacting us! We’ll get back to you soon.',
        'all_brands': all_brands,
    }
    return render(request, 'contact_success.html', context)
