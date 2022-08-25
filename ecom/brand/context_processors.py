from .models import brand

def menu_links(request):
    link = brand.objects.all()
    return dict(link = link)