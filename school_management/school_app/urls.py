from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    # Đường dẫn trang chủ
    path('', views.home, name='home'),

    # Các đường dẫn đăng nhập đăng xuất
    path('dang-nhap', views.dangnhap, name='dang-nhap'),
    path('xu-ly-dang-nhap', views.xulydangnhap, name='xu-ly-dang-nhap'),
    path('dang-xuat', views.dang_xuat, name='dang-xuat'),
    
    # Các đường dẫn liên quan tới trang quản lý học sinh của Quản trị viên
    path('hoc-sinh/', views.hoc_sinh, name='hoc-sinh'),
    path('hoc-sinh/them-hoc-sinh', views.them_hoc_sinh, name='them-hoc-sinh'),
    path('hoc-sinh/cap-nhat-hoc-sinh/<int:hoc_sinh_id>', views.cap_nhat_hoc_sinh, name='cap-nhat-hoc-sinh'),
    path('hoc-sinh/xoa-hoc-sinh/<int:hoc_sinh_id>', views.xoa_hoc_sinh, name='xoa-hoc-sinh'),
    
    # Các đường dẫn liên quan tới trang quản lý lớp học của Quản trị viên
    path('lop-hoc', views.lop_hoc, name='lop-hoc'),
    path('lop-hoc/them-lop-hoc', views.them_lop_hoc, name='them-lop-hoc'),
    path('lop-hoc/tao-ds-lop', views.tao_danh_sach_lop, name='tao-ds-lop'),
    path('lop-hoc/danh-sach-lop/<int:lop_id>', views.danh_sach_lop, name='danh-sach-lop'),
    path('lop-hoc/danh-sach-lop/sua-hanh-kiem/<int:lop_id>/hoc-sinh/<int:hoc_sinh_id>', views.sua_hanh_kiem, name='sua-hanh-kiem'),
    path('lop-hoc/xuat-ds-lop/<int:lop_hoc_id>/', views.xuat_ds_lop, name='xuat-ds-lop'),
    path('lop-hoc/danh-sach-lop/<int:lop_id>/xoa-hs/<int:hoc_sinh_id>', views.xoa_hs_khoi_lop, name='xoa-hs-khoi-lop'),
    path('lop-hoc/xoa-lop-hoc/<int:lop_id>', views.xoa_lop_hoc, name='xoa-lop-hoc'),
    
    # Các đường dẫn liên quan tới trang quản lý môn học của Quản trị viên
    path('mon-hoc', views.mon_hoc, name='mon-hoc'),
    path('mon-hoc/them-mon-hoc', views.them_mon_hoc, name='them-mon-hoc'),
    path('mon-hoc/xoa-mon-hoc/<int:mon_hoc_id>', views.xoa_mon_hoc, name='xoa-mon-hoc'),
    path('mon-hoc/sua-mon-hoc/<int:mon_hoc_id>', views.sua_mon_hoc, name='sua-mon-hoc'),


    # Các đường dẫn liên quan tới trang điểm số 
    path('diem', views.diem, name='diem'),
    path('diem/cap-nhat-diem/<int:diem_id>', views.cap_nhat_diem, name='cap-nhat-diem'),
    path('xuat-diem', views.xuat_diem, name='xuat-diem'),
    
    # Các đường dẫn liên quan tới trang quản lý giáo viên của Quản trị viên
    path('ds-giao-vien', views.danh_sach_giao_vien, name='ds-giao-vien'),
    path('ds-giao-vien/them-giao-vien', views.them_giao_vien, name='them-giao-vien'),
    path('ds-giao-vien/cap-nhat-gv/<int:giao_vien_id>', views.cap_nhat_giao_vien, name='cap-nhat-gv'),
    path('ds-giao-vien/xoa-gv/<int:giao_vien_id>', views.xoa_giao_vien, name='xoa-gv'),
    path('ds-giao-vien/phan-cong-gv/<int:giao_vien_id>', views.phan_cong_giao_vien, name='phan-cong-gv'),
    path('ds-giao-vien/huy-phan-cong/<int:giao_vien_id>/<int:lop_hoc_id>/', views.huy_phan_cong, name='huy-phan-cong'),
    
    # Các đường dẫn liên quan tới trang tổng kết của Quản trị viên
    path('tong-ket/', views.tong_ket, name='tong-ket'),
    path('tong-ket/ds-ket-qua-hoc-sinh/<int:nam_hoc_id>/<str:status>/', views.danh_sach_kq_hoc_sinh, name='ds-ket-qua-hoc-sinh'),
    
    # Đường dẫn kết quả học tập dành cho học sinh
    path('ket-qua-hoc-tap', views.ket_qua_hoc_tap, name='ket-qua-hoc-tap'),
    
    # Đường dẫn trang cá nhân cho tất cả người dùng
    path('trang-ca-nhan', views.trang_ca_nhan, name='trang-ca-nhan'),
    
    # Các đường dẫn liên quan tới trang quản lý điểm, lớp chủ nhiệm của Giáo viên
    path('giao-vien/quan-ly-diem', views.quan_ly_diem, name='quan-ly-diem'),
    path('giao-vien/quan-ly-diem/cap-nhat-diem/<int:diem_id>', views.cap_nhat_diem_gv, name='cap-nhat-diem-gv'),
    path('giao-vien/lop-chu-nhiem/', views.lop_chu_nhiem, name='lop-chu-nhiem'),
    path('giao-vien/xem-ket-qua/<int:lop_id>', views.xem_ket_qua_lop, name='xem-ket-qua-lop'),


]
