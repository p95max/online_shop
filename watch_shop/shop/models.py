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
    views = models.PositiveIntegerField(default=0)

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

class WatchImage(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='watches/', null=True, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.watch.model}"

class WatchUserMananger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(in_stock=True)

    def sorted_by_abc(self):
        return self.get_queryset().all().order_by('model')

class Brand(models.Model):
    name = models.CharField(max_length=100,)
    slug = models.SlugField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
        return f"{self.watch.model} - {self.ip_address}"

class Comment(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.watch.model}"

class ContactRequest(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Contact from {self.name} ({self.email})"

class CartItem(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.watch.model}"

    @property
    def total_price(self):
        return self.quantity * self.watch.price if self.watch.price else 0

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.first_name} {self.last_name}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.watch.model} in Order {self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.price

