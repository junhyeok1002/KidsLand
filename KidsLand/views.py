from django.shortcuts import render

def splash_view(request):
    # Render the splash.html template with the provided context
    return render(request, 'KidsLand/splash.html')
