from urllib import request
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import *

class AdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_only_paths = [
            '/hoc-sinh/', '/them-hoc-sinh', '/cap-nhat-hoc-sinh/', '/xoa-hoc-sinh/',
            '/mon-hoc', '/diem', '/ds-giao-vien', '/tong-ket/'
        ]

        if any(request.path.startswith(path) for path in admin_only_paths):
            if not (request.user.is_authenticated and request.user.vai_tro == '1'):
                return redirect(reverse('dang-nhap')) 
            
        if request.path.startswith('lop-hoc/danh-sach-lop/sua-hanh-kiem'):
            if request.resolver_match:
                lop_id = request.resolver_match.kwargs.get('lop_id')
                hoc_sinh_id = request.resolver_match.kwargs.get('hoc_sinh_id')

                if lop_id and hoc_sinh_id:
                    giao_vien = get_object_or_404(GiaoVien, nguoi_dung=request.user)
                    lop_hoc = get_object_or_404(LopHoc, id=lop_id)

                    if giao_vien not in lop_hoc.giao_vien.all():
                        return redirect(reverse('dang-nhap'))  
        
        # Cho phép sửa điểm nếu giáo viên được phân công dạy lớp và môn học
        if request.path.startswith('/diem/cap-nhat-diem/'):
            if request.resolver_match:
                diem_id = request.resolver_match.kwargs.get('diem_id')
                if diem_id:
                    # Lấy thông tin điểm từ KetQua
                    ket_qua = get_object_or_404(KetQua, id=diem_id)
                    giao_vien = get_object_or_404(GiaoVien, nguoi_dung=request.user)

                    # Kiểm tra giáo viên có dạy lớp và môn học tương ứng không
                    if (
                        ket_qua.mon_hoc != giao_vien.mon_day or
                        ket_qua.hoc_sinh.lop_hoc.filter(id__in=giao_vien.lop_day.all()).count() == 0
                    ):
                        return redirect(reverse('dang-nhap'))  # Chuyển hướng nếu không có quyền
        
        return self.get_response(request)

