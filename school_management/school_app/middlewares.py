from django.shortcuts import redirect
from django.urls import reverse

class AdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Danh sách các URL chỉ dành cho admin
        admin_only_paths = [
            '/hoc-sinh/', '/them-hoc-sinh', '/cap-nhat-hoc-sinh/', '/xoa-hoc-sinh/',
            '/lop-hoc', '/them-lop-hoc', '/tao-ds-lop', '/mon-hoc', '/diem',
            '/ds-giao-vien', '/tong-ket/'
        ]

        # Nếu user truy cập URL admin mà không phải là admin
        if any(request.path.startswith(path) for path in admin_only_paths):
            if not (request.user.is_authenticated and request.user.vai_tro == '1'):
                return redirect(reverse('dang-nhap'))  # Chuyển hướng đến trang đăng nhập

        return self.get_response(request)
