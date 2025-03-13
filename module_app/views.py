from django.shortcuts import render


def page_not_found(request, exception):
    return render(
        request,
        'module_app/errors/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'module_app/errors/500.html', status=500)


def bad_request(request, exception):
    return render(
        request,
        'module_app/errors/400.html',
        {'path': request.path}, status=400
    )
