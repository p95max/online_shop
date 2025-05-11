from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from shop.models import Watch, Brand, Favorite, Comment


def catalog(request):
    sort_by = request.GET.get('sort', 'date')
    sort_options = {
        'date': '-added_at',
        'views': '-views',
        'favourites': '-favourites_count',
    }
    sort_field = sort_options.get(sort_by, sort_options['date'])

    watches_count = Watch.objects.count()
    all_brands = Brand.objects.all()
    favourites_count = Favorite.objects.count()

    news_list = Watch.objects.filter(in_stock=True).order_by(sort_field)
    paginator = Paginator(news_list, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "watches_count": watches_count,
        "all_brands": all_brands,
        "page_obj": page_obj,
        "favourites_count": favourites_count,
        "sort": sort_by,
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


def toggle_favorite(request, slug):
    watch = get_object_or_404(Watch, slug=slug)
    ip_address = request.META.get('REMOTE_ADDR')

    existing_like = Favorite.objects.filter(watch=watch, ip_address=ip_address).first()

    if existing_like:
        existing_like.delete()
        watch.favourites_count = max(0, watch.favourites_count - 1)
        liked = False
    else:
        Favorite.objects.create(watch=watch, ip_address=ip_address)
        watch.favourites_count += 1
        liked = True

    watch.save()

    return JsonResponse({
        "likes_count": watch.favourites_count,
        "liked": liked
    })