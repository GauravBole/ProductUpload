from django.db import models

# Create your models here.

class Product(models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)
    sku = models.CharField(max_length=100,unique=True, null=False, blank=False)
    discription = models.TextField()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Product_detail", kwargs={"pk": self.pk})
