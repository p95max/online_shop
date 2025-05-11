from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

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
