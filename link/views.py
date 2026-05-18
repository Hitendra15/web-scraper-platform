from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from .models import Link
from django.http import JsonResponse
from django.core.paginator import Paginator
# Create your views here.
def scrape(request):
    data = []
    if request.method == "POST":
        url = request.POST.get('url')
        page_number = request.POST.get('page', 1)
        if url:
            try:
                page = requests.get(url, timeout=5)
                soup = BeautifulSoup(page.text, 'html.parser')
                for link in soup.find_all('a'):
                    link_address = link.get('href')
                    if not link_address:
                        continue
                    link_text = link.get_text(strip=True)
                    Link.objects.create(
                        address=link_address,
                        name=link_text if link_text else "No Text"
                    )
            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        data = Link.objects.all().order_by('-id')
        paginator = Paginator(data, 10)
        page_obj = paginator.get_page(page_number)
        response_data = []
        for link in page_obj:
            response_data.append({
                'id': link.id,
                'name': link.name,
                'address': link.address
            })
        return JsonResponse({
            'success': True,
            'data': response_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count
        })
    return render(request, 'link/result.html', {'data': data})

def clear(request):
    if request.method == 'POST':
        Link.objects.all().delete()
        return JsonResponse({
            'success': True,
            'data': [],
            'current_page': 1,
            'total_pages': 0,
            'total_items': 0,
            'message': 'Extracted links cleared successfully'
        })
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    })