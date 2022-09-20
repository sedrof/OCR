from django.shortcuts import render, redirect
from .form import PdffileForm
from django.contrib.auth.decorators import user_passes_test, login_required
# Create your views here.

@login_required
def upload(request):
    form = PdffileForm()
    print('here')
    if request.method == 'POST':
        form = PdffileForm(request.POST, request.FILES)
        # if form is not valid then form data will be sent back to view to show error message
        if form.is_valid():
            form.save()
            return redirect('place-portal')
    return render(request, "home.html", {'form': form})