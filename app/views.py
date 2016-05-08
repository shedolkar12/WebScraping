from django.shortcuts import render
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from lxml import html
import requests
from app.models import *
# Create your views here. 

cache = {'q':'', 'data': []}

def index(request):
    if request.method=='POST':
        q = request.POST.get('q', '')
        #checking for same request and displaying cache data
        if q==cache['q']:
            return render(request, 'search.html', {'data': cache['data'], 'is_data': True} )
        page = requests.get('https://play.google.com/store/search?q='+q+'&c=apps&hl=en')
        tree = html.fromstring(page.content)
        app_links = tree.xpath('//a[@class="title"]/@href')
        #app_data will contains app search result
        app_data = []
        n=10 if len(app_links)>10 else len(app_links)
        for link in app_links[0:n]:
            app_data.append(get_data(link))
        #storing data after every new search      
        cache['q']=q
        cache['data'] = app_data
            
        return render(request, 'search.html', {'data': app_data, 'is_data': True})
    else:
        # with every back link attaching back keyword which will retuen cache data
        if 'back' in request.GET.dict():
            data = {'data': cache['data'], 'is_data': True }
        else:
            data = {'is_data' : False}     
        return render(request, 'search.html', data)

def get_data(link):
    
    #data will be returned in the following format
    data = {"app_id": '', "app_name": '',}
    #link contain id extracting id from link
    app_id = link.split("id=")[1].strip()
    
    try:
        #checking app in the database
        query = app_details.objects.get(app_id=app_id)
        data['app_id']=query.app_id
        data['app_name'] = query.app_name
        
    except app_details.DoesNotExist:
        page = requests.get( 'https://play.google.com' + link)
        tree = html.fromstring(page.content)
        # parsing and storing app details in the database
        app_name = tree.xpath('//div[@class="id-app-title"]/text()')
        developer = tree.xpath('//span[@itemprop="name"]/text()')
        icon_url =  tree.xpath('//img[@class="cover-image"]/@src')
        developer_email = tree.xpath('//a[@class="dev-link"]/text()')
        app = app_details(app_id=app_id, app_name=app_name[0], developer=developer[0], developer_email=get_email(developer_email), icon_url=icon_url[0])
        app.save()
        data['app_id']=app_id
        data['app_name']=app_name

    return data

def get_email(links):
    for link in links:
        if 'Email' in link.split():
            return link.split()[1]

def details(request):
    app_id = request.GET.get('app_id')
    app = app_details.objects.get(app_id=app_id)
    data = {'app_id': app.app_id, 
            'app_name': app.app_name,
            'developer': app.developer,
            'developer_email': app.developer_email,
            'icon_url': app.icon_url,
    }
    return render(request, 'details.html', data)    
