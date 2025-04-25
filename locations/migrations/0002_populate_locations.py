


from django.db import migrations
from django.utils.text import slugify

def populate_yangon_mandalay(apps, schema_editor):
    """
    Populates Region/State, City/District, and Township data for Yangon & Mandalay.
    NOTE: Township lists should be verified against current official sources.
    """
    
    RegionState = apps.get_model('locations', 'RegionState')
    CityDistrict = apps.get_model('locations', 'CityDistrict')
    Township = apps.get_model('locations', 'Township')
    db_alias = schema_editor.connection.alias

    
    yangon_region, _ = RegionState.objects.using(db_alias).update_or_create(
        name="Yangon Region", defaults={'slug': slugify("Yangon Region")}
    )

    
    yangon_east, _ = CityDistrict.objects.using(db_alias).update_or_create(
        name="Yangon Eastern District", region_state=yangon_region,
        defaults={'slug': slugify("Yangon Eastern District")}
    )
    yangon_west, _ = CityDistrict.objects.using(db_alias).update_or_create(
        name="Yangon Western District", region_state=yangon_region,
        defaults={'slug': slugify("Yangon Western District")}
    )
    yangon_south, _ = CityDistrict.objects.using(db_alias).update_or_create(
        name="Yangon Southern District", region_state=yangon_region,
        defaults={'slug': slugify("Yangon Southern District")}
    )
    yangon_north, _ = CityDistrict.objects.using(db_alias).update_or_create(
        name="Yangon Northern District", region_state=yangon_region,
        defaults={'slug': slugify("Yangon Northern District")}
    )

    
    yangon_townships = {
        yangon_east: [
            "Botataung", "Dagon Seikkan", "Dawbon","Mingala Taungnyunt", "East Dagon", 
            "North Dagon","South Dagon", "North Okkalapa", "Pazundaung",  "South Okkalapa",
            "Thaketa", "Thingangyun","Tamwe","Yankin",
        ],
        yangon_west: [
            "Ahlon", "Bahan", "Dagon", "Hlaing", "Kamayut", "Kyauktada",
            "Kyimyindaing","Lanmadaw","Mayangon",
            "Latha", "Pabedan", "Sanchaung",
        ],
        yangon_south: [
            "Dala","Seikkyi Kanaungto"
        ],
        yangon_north: [
            "Insein","Hlaingthya","Mingaladon","Shwepyitha"
        ]
    }

    for district, townships in yangon_townships.items():
        for township_name in townships:
            Township.objects.using(db_alias).update_or_create(
                name=township_name,
                city_district=district,
                defaults={'slug': slugify(township_name.replace('(','').replace(')',''))} 
            )

    
    mandalay_region, _ = RegionState.objects.using(db_alias).update_or_create(
        name="Mandalay Region", defaults={'slug': slugify("Mandalay Region")}
    )

    
    mandalay_district, _ = CityDistrict.objects.using(db_alias).update_or_create(
        name="Mandalay District", region_state=mandalay_region,
        defaults={'slug': slugify("Mandalay District")}
    )

    
    mandalay_townships = [
        "Aungmyaythazan", "Chanayethazan", "Chanmyathazi", "Maha Aungmyay", "Pyigyidagun",
        "Amarapura", "Patheingyi"
    ]

    for township_name in mandalay_townships:
        Township.objects.using(db_alias).update_or_create(
            name=township_name,
            city_district=mandalay_district,
            defaults={'slug': slugify(township_name)}
        )


def remove_populated_locations(apps, schema_editor):
    """ Reverses the population (optional). """
    
    
    pass


class Migration(migrations.Migration):

    dependencies = [
        
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_yangon_mandalay, remove_populated_locations),
    ]