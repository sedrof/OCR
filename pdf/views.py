from django.shortcuts import render, redirect
from .form import PdffileForm

# Create your views here.
def upload(request):

    form = PdffileForm()

    if request.method == 'POST':
        form = PdffileForm(request.POST, request.FILES)
        # if form is not valid then form data will be sent back to view to show error message
        if form.is_valid():
            form.save()
            return redirect('place-portal')

    return render(request, "upload.html", {'form': form})