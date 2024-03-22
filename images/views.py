from django.shortcuts import render, redirect
from .forms import ImageCreateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_http_methods, require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action 
from .models import image
import redis
from django.conf import settings

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'image added successfully')
            return redirect(new_image.get_absolute_url())
        
    else:
        form = ImageCreateForm(data=request.GET)
    

    return render(request, 'images/image/create.html', {'form': form,
                                                        'section_image':'images',
                                                        'section_dshbrd': 'dshbrd'})


def image_detail(request, id, slug):
    image_view = get_object_or_404(image, id=id, slug=slug)
    # increment image view by 1
    total_views = r.incr(f'image_view:{image_view.id}:views')
    # increment image ranking by 1
    r.zincrby('image_ranking', 1, image_view.id)

    return render(request, 'images/image/detail.html',
                  {'section': 'imagedetail',
                   'image': image_view,
                   'success': True,
                   'total_views': total_views})

@login_required
# @require_http_methods(["POST"])
@require_POST
def image_like(request):
    image_id = request.POST.get("id")
    action = request.POST.get('action')
    if image_id and action:
        try:
            Image = image.objects.get(id=image_id)
            if action == 'like':
                Image.user_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                Image.user_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}) 


@login_required
def image_list(request):
    images = image.objects.all()
    paginator = Paginator(images, 6)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html',{'section': 'images',
                                                                'images': images})
    return render(request, 'images/image/list.html', {'section':'images',
                                                      'images': images})

@login_required
def image_ranking(request):
    image_ranking = r.zrange('image_ranking', 0 , -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]

    most_viewed = list(image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x:image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': "imageRanking",
                                                         'most_viewed': most_viewed})

