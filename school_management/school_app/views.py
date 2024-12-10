from django.shortcuts import render

# Create your views here.
def base(request):
    return render(request, 'school_app/base.html')

def dangnhap(request):
    return render(request, 'school_app/dang_nhap.html')