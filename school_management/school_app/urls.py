from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.base),
    path('dang-nhap', views.dangnhap, name='dang-nhap'),
    path('xu-ly-dang-nhap', views.xulydangnhap, name='xu-ly-dang-nhap'),
    path('dang-xuat', views.dang_xuat, name='dang-xuat'),
    path('hoc-sinh/', views.hoc_sinh, name='hoc-sinh'),
    path('them-hoc-sinh', views.them_hoc_sinh, name='them-hoc-sinh'),
    path('cap-nhat-hoc-sinh/<int:hoc_sinh_id>', views.cap_nhat_hoc_sinh, name='cap-nhat-hoc-sinh'),
    path('xoa-hoc-sinh/<int:hoc_sinh_id>', views.xoa_hoc_sinh, name='xoa-hoc-sinh'),
    path('lop-hoc', views.lop_hoc, name='lop-hoc'),
    path('them-lop-hoc', views.them_lop_hoc, name='them-lop-hoc'),
    path('tao-ds-lop', views.tao_danh_sach_lop, name='tao-ds-lop'),
    path('lop-hoc/danh-sach-lop/<int:lop_id>', views.danh_sach_lop, name='danh-sach-lop'),
    path('lop-hoc/danh-sach-lop/<int:lop_id>/xoa-hs/<int:hoc_sinh_id>', views.xoa_hs_khoi_lop, name='xoa-hs-khoi-lop'),
    path('lop-hoc/xoa-lop-hoc/<int:lop_id>', views.xoa_lop_hoc, name='xoa-lop-hoc'),
    path('mon-hoc', views.mon_hoc, name='mon-hoc'),
    path('mon-hoc/them-mon-hoc', views.them_mon_hoc, name='them-mon-hoc'),
    path('mon-hoc/xoa-mon-hoc/<int:mon_hoc_id>', views.xoa_mon_hoc, name='xoa-mon-hoc'),
    path('diem', views.diem, name='diem'),
    path('diem/cap-nhat-diem/<int:diem_id>', views.cap_nhat_diem, name='cap-nhat-diem'),
    path('ds-giao-vien', views.danh_sach_giao_vien, name='ds-giao-vien'),
    path('ds-giao-vien/them-giao-vien', views.them_giao_vien, name='them-giao-vien'),
    path('ds-giao-vien/cap-nhat-gv/<int:giao_vien_id>', views.cap_nhat_giao_vien, name='cap-nhat-gv'),
    path('ds-giao-vien/xoa-gv/<int:giao_vien_id>', views.xoa_giao_vien, name='xoa-gv'),
]
