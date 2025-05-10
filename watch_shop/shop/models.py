from django.db.models import F
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
import datetime

class Watch(models.Model):
    model = models.CharField(max_length=100, verbose_name='Model')
    brand = models.ForeignKey(
        'Brand',
        on_delete=models.CASCADE,
        related_name='watches',
        verbose_name='Brand'
    )
    year = models.PositiveIntegerField(
        verbose_name='Product Year',
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.datetime.now().year)
        ]
    )
    description = models.TextField(verbose_name='Description')
    price = models.PositiveIntegerField(verbose_name='Price')
    image = models.ImageField(upload_to='images/',
                              validators=[FileExtensionValidator(['jpg', 'jpeg', 'png',] )],
                              blank=True,
                              null=True,
                              verbose_name='Image',
                              )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Added at')
    in_stock = models.BooleanField(default=True, verbose_name='In stock')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Slug')
    objects = models.Manager()
    favourites_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.model)
            slug = base_slug
            num = 1
            while Watch.objects.exclude(id=self.id).filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def price_with_dollar(self):
        return f"${self.price}"

    def __str__(self):
        return f"{self.model} - {self.brand} - {self.year}"

class WatchUserMananger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(in_stock=True)

    def sorted_by_abc(self):
        return self.get_queryset().all().order_by('model')

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

class Favorite(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='favorites')
    ip_address = models.GenericIPAddressField()

    class Meta:
        unique_together = ('ip_address', 'watch')

    def __str__(self):
        return f"{self.watch.model} - {self.ip_address} - {self.favorites_count}"

class Comment(models.Model):
    article = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.article.model}"

