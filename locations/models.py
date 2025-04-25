from django.db import models
from django.utils.text import slugify


class RegionState(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the Region or State (e.g., Yangon Region)")
    slug = models.SlugField(max_length=110, unique=True, blank=True, help_text="URL-friendly version of the name.")

    class Meta:
        verbose_name = "Region/State"
        verbose_name_plural = "Regions & States"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CityDistrict(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the City or District")
    region_state = models.ForeignKey(
        RegionState,
        related_name='districts',
        on_delete=models.PROTECT,
        help_text="The Region or State this district belongs to."
    )
    slug = models.SlugField(max_length=110, blank=True, help_text="URL-friendly version of the name.")

    class Meta:
        verbose_name = "City/District"
        verbose_name_plural = "Cities & Districts"
        ordering = ['region_state', 'name']
        unique_together = [['name', 'region_state']] # Name unique within a region/state

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while CityDistrict.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.region_state.name})"

class Township(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the Township (e.g., Dagon, Bahan)")
    city_district = models.ForeignKey(
        CityDistrict,
        related_name='townships',
        on_delete=models.PROTECT,
        help_text="The City or District this township belongs to."
    )
    slug = models.SlugField(max_length=110, blank=True, help_text="URL-friendly version of the name.")

    class Meta:
        verbose_name = "Township"
        verbose_name_plural = "Townships"
        ordering = ['city_district', 'name']
        unique_together = [['name', 'city_district']] # Name unique within a district

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Township.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.city_district.name})"

