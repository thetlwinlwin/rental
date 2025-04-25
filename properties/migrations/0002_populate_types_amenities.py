


from django.db import migrations
from django.utils.text import slugify



INITIAL_PROPERTY_TYPES = [
    "Apartment",
    "Condominium",
    "Landed House",
    "Townhouse",
    "Room for Rent",
    "Shophouse",
    "Office Space",
]

INITIAL_AMENITIES = [
    "Air Conditioning",
    "Parking Available",
    "Backup Generator",
    "Swimming Pool",
    "Gym",
    "Furnished", 
    "Hot Water",
    "Security",
    "Elevator",
    "Balcony",
    "Wifi Included",
    "Pet Friendly",
    "Washing Machine",
    "Refrigerator",
    "Kitchen Appliances",
]



def populate_data(apps, schema_editor):
    """Populates PropertyType and Amenity models with initial data."""
    PropertyType = apps.get_model('properties', 'PropertyType')
    Amenity = apps.get_model('properties', 'Amenity')
    db_alias = schema_editor.connection.alias

    print("\nPopulating initial Property Types...")
    for name in INITIAL_PROPERTY_TYPES:
        slug = slugify(name)
        obj, created = PropertyType.objects.using(db_alias).update_or_create(
            name=name,
            defaults={'slug': slug}
        )
        if created:
            print(f'  Created PropertyType: {name}')
        
            

    print("Populating initial Amenities...")
    for name in INITIAL_AMENITIES:
        slug = slugify(name)
        obj, created = Amenity.objects.using(db_alias).update_or_create(
            name=name,
            defaults={'slug': slug}
        )
        if created:
            print(f'  Created Amenity: {name}')
        
            

def delete_data(apps, schema_editor):
    """Deletes the initial data if the migration is reversed (optional)."""
    PropertyType = apps.get_model('properties', 'PropertyType')
    Amenity = apps.get_model('properties', 'Amenity')
    db_alias = schema_editor.connection.alias

    print("\nDeleting initial Property Types...")
    PropertyType.objects.using(db_alias).filter(name__in=INITIAL_PROPERTY_TYPES).delete()

    print("Deleting initial Amenities...")
    Amenity.objects.using(db_alias).filter(name__in=INITIAL_AMENITIES).delete()




class Migration(migrations.Migration):

    dependencies = [
        
        
        
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_data, reverse_code=delete_data),
    ]