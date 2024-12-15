from itertools import count
from venv import logger
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import NguoiDung
from django.contrib.auth.decorators import login_required
from .form import CapNhatNguoiDungForm, GiaoVienForm, HocSinhForm, KetQuaForm, LopHocForm, MonHocForm
from .models import *
from django.contrib.messages import get_messages
from django.db.models import Count
from django.db.models import Avg
from django.contrib.auth.decorators import user_passes_test

def check_role(user):
    return user.is_authenticated and user.vai_tro != "Quản trị viên"  # check quyền


# Create your views here.
@login_required(login_url='dang-nhap')
def base(request):
    return render(request, 'school_app/base.html')

def dangnhap(request):
    return render(request, 'school_app/dang_nhap.html')

def xulydangnhap(request):
    """
    Hàm xử lý logic đăng nhập.
    """
    if request.method == "POST":
        # Lấy thông tin từ form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Dùng authenticate để xác thực thông tin
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Nếu thông tin hợp lệ, đăng nhập
            login(request, user)
            messages.success(request, "Đăng nhập thành công!")

            # Dựa vào vai trò, điều hướng người dùng đến trang phù hợp
            if user.vai_tro == '1':
                return redirect('/')
            elif user.vai_tro == '2':
                return redirect('quan-ly-diem')
            elif user.vai_tro == '3':
                return redirect('ket-qua-hoc-tap')
        else:
            # Thêm thông báo lỗi nếu thông tin không hợp lệ
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác!")

    # Render giao diện login
    return render(request, 'school_app/dang_nhap.html')

@login_required(login_url='dang-nhap')
def dang_xuat(request):
    logout(request)
    return redirect("/")

@login_required(login_url='dang-nhap')
def trang_ca_nhan(request):
    return render(request, 'school_app/trang_ca_nhan.html')

@login_required(login_url='dang-nhap')
def them_hoc_sinh(request):
    form = HocSinhForm(request.POST or None)
    context = {
        'form': form,
    }
    storage = get_messages(request)  # Lấy thông báo đã lưu
    for message in storage:  # Tiêu thụ thông báo (không bắt buộc)
        print(f"Message: {message}")
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password')
            ho_ten = form.cleaned_data.get('ho_ten')
            ngay_sinh = form.cleaned_data.get('ngay_sinh')
            gioi_tinh = form.cleaned_data.get('gioi_tinh')
            email = form.cleaned_data.get('email')
            dia_chi = form.cleaned_data.get('dia_chi')

            # Tạo mật khẩu từ ngày sinh (định dạng DDMMYYYY)
            if ngay_sinh:
                # Giả sử ngày sinh có định dạng YYYY-MM-DD
                ngay_sinh_str = ngay_sinh.strftime('%d%m%Y')  # Định dạng ngày sinh thành "DDMMYYYY"
                password = ngay_sinh_str  # Dùng mật khẩu là ngày sinh đã định dạng

            try:
                user = NguoiDung.objects._create_user(
                    username=username, 
                    password=password,  # Dùng mật khẩu đã tạo
                    ho_ten=ho_ten,
                    vai_tro='3',
                    ngay_sinh=ngay_sinh,
                    gioi_tinh=gioi_tinh,
                    email=email,
                    dia_chi=dia_chi
                )

                hoc_sinh = HocSinh(nguoi_dung=user)
                user.save()
                print(hoc_sinh)
                hoc_sinh.save()
                messages.success(request, "Thêm thành công", extra_tags='add_student')
            except Exception as e:
                print(e)
                logger.error(f"Lỗi khi thêm học sinh: {e}")
                messages.error(request, "Không thể thêm", extra_tags='add_student')
        else:
            messages.error(request, "Dữ liệu không phù hợp", extra_tags='add_student')
    
    return render(request, 'school_app/them_hoc_sinh.html', context=context)



@login_required(login_url='dang-nhap')
def hoc_sinh(request):
    # Lấy từ khóa tìm kiếm từ GET (nếu có)
    search_query = request.GET.get('ten_hoc_sinh', '')

    # Lọc danh sách học sinh theo từ khóa tìm kiếm nếu có
    if search_query:
        ds_hoc_sinh = HocSinh.objects.filter(
            nguoi_dung__ho_ten__icontains=search_query
        ).order_by('nguoi_dung__ho_ten')
    else:
        ds_hoc_sinh = HocSinh.objects.all().order_by('nguoi_dung__ho_ten')

    # Truyền danh sách học sinh vào template
    return render(request, 'school_app/hoc_sinh.html', {
        'ds_hoc_sinh': ds_hoc_sinh,
        'search_query': search_query
    })

@login_required(login_url='dang-nhap')
def cap_nhat_hoc_sinh(request, hoc_sinh_id):
    # Lấy đối tượng HocSinh từ cơ sở dữ liệu
    hoc_sinh = get_object_or_404(HocSinh, id=hoc_sinh_id)
    print(hoc_sinh)
    # Nếu là phương thức POST, nghĩa là người dùng đang gửi thông tin
    if request.method == "POST":
        form = CapNhatNguoiDungForm(request.POST, instance=hoc_sinh.nguoi_dung)
        if form.is_valid():
            try:
                # Lưu thông tin cập nhật
                form.save()

                # Thông báo thành công
                messages.success(request, "Cập nhật thành công", extra_tags='update_student')

                # Chuyển hướng về trang danh sách học sinh sau khi cập nhật
                return redirect('cap-nhat-hoc-sinh', hoc_sinh_id = hoc_sinh_id)  # URL danh sách học sinh
            except Exception as e:
                print(e)
                messages.error(request, "Có lỗi khi cập nhật học sinh", extra_tags='update_student')
    else:
        # Nếu là GET, form sẽ được khởi tạo với dữ liệu hiện tại
        form = CapNhatNguoiDungForm(instance=hoc_sinh.nguoi_dung)

    return render(request, 'school_app/cap_nhat_hs.html', {'form': form})

@login_required(login_url='dang-nhap')
def xoa_hoc_sinh(request, hoc_sinh_id):
    hoc_sinh = get_object_or_404(HocSinh, id=hoc_sinh_id)
    nguoi_dung = NguoiDung.objects.filter(username=hoc_sinh.nguoi_dung.username)
    if request.method == 'POST':
        nguoi_dung.delete()  # Xóa học sinh
        messages.success(request, "Xóa học sinh thành công!")
    return redirect('hoc-sinh')


@login_required(login_url='dang-nhap')
def lop_hoc(request):
    # Lấy năm học mới nhất
    # nam_hoc_moi_nhat = NamHoc.objects.order_by('-nam').first()
    lop_hoc_list = LopHoc.objects.all()
    lop_hoc_list = lop_hoc_list.annotate(so_hs=Count('hocsinh'))
    # Lọc theo năm học (nếu có)
    current_nam_hoc = request.GET.get('nam_hoc', None)
    if current_nam_hoc:
        try:
            nam_hoc_obj = NamHoc.objects.get(nam=current_nam_hoc)
            lop_hoc_list = lop_hoc_list.filter(nam_hoc=nam_hoc_obj)
            lop_hoc_list = lop_hoc_list.annotate(so_hs=Count('hocsinh'))
        except NamHoc.DoesNotExist:
            # Nếu không tìm thấy năm học phù hợp, không lọc
            lop_hoc_list = lop_hoc_list.none()

    # Lọc theo tên lớp (nếu có)
    # ten_lop = request.GET.get('ten_lop', '')
    # if ten_lop:
    #     lop_hoc_list = lop_hoc_list.filter(ma_lop=ten_lop)

    # Lấy danh sách các năm học để hiển thị trong form lọc
    nam_hoc_options = NamHoc.objects.all()

    # Lấy danh sách các mã lớp để hiển thị trong dropdown tên lớp
    ten_lop_options = LopHoc.objects.values_list('ma_lop', flat=True).distinct()

    return render(request, 'school_app/lop_hoc.html', {
        'lop_hoc_list': lop_hoc_list,
        'nam_hoc_options': nam_hoc_options,
        'ten_lop_options': ten_lop_options,  # Thêm danh sách lớp vào context
        'current_nam_hoc': current_nam_hoc,
        # 'current_ten_lop': ten_lop,
    })

@login_required(login_url='dang-nhap')
def them_lop_hoc(request):
    if request.method == 'POST':
        form = LopHocForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm lớp học thành công!")
            return redirect('lop-hoc')  # Chuyển hướng về trang danh sách lớp học
    else:
        form = LopHocForm()
    
    return render(request, 'school_app/them_lop_hoc.html', {'form': form})


@login_required(login_url='dang-nhap')
def tao_danh_sach_lop(request):
    # Lấy các lớp học và năm học cho việc lọc
    nam_hoc_options = NamHoc.objects.all()
    ten_lop_options = LopHoc.objects.all()

    # Lấy giá trị lọc từ GET
    selected_nam_hoc = request.GET.get('nam_hoc')
    selected_ten_lop = request.GET.get('ten_lop')

    # Khởi tạo QuerySet lớp học trong năm học đã chọn
    lop_hoc_nam_hoc = LopHoc.objects.all()
    hoc_sinh_chua_co_lop = HocSinh.objects.all()
    # Lọc các lớp học theo năm học nếu có
    if selected_nam_hoc:
        try:
            nam_hoc = NamHoc.objects.get(nam=selected_nam_hoc)
            ten_lop_options = ten_lop_options.filter(nam_hoc=nam_hoc)
            lop_hoc_nam_hoc = lop_hoc_nam_hoc.filter(nam_hoc=nam_hoc)
            # Lọc học sinh chưa có lớp trong năm học đó
            hoc_sinh_chua_co_lop = HocSinh.objects.exclude(lop_hoc__in=lop_hoc_nam_hoc)  # Loại trừ học sinh thuộc bất kỳ lớp nào của năm học này
        
        except NamHoc.DoesNotExist:
            nam_hoc = None  # Nếu không có năm học, xử lý lỗi hoặc để trống

    # Lọc theo lớp học nếu có
    if selected_ten_lop:
        hoc_sinh_chua_co_lop = hoc_sinh_chua_co_lop.exclude(lop_hoc__ma_lop=selected_ten_lop)

    # Kiểm tra xem có POST request để cập nhật học sinh vào lớp
    if request.method == 'POST':
        # Lấy danh sách các sinh viên đã chọn từ form
        hoc_sinh_ids = request.POST.getlist('hoc_sinh_ids')
        if hoc_sinh_ids:
            # Lấy lớp học được chọn
            try:
                lop_hoc = LopHoc.objects.get(ma_lop=selected_ten_lop)
                nam_hoc = lop_hoc.nam_hoc.nam
                # Lưu các sinh viên vào lớp học
                list(map(lambda hoc_sinh_id: HocSinh.objects.get(id=hoc_sinh_id).lop_hoc.add(lop_hoc), hoc_sinh_ids))

                # Redirect đến trang danh sách lớp sau khi lưu thành công
                return redirect(f'/lop-hoc?nam_hoc={nam_hoc}')  # Sửa 'lop-hoc' bằng tên URL thực tế của bạn
            except LopHoc.DoesNotExist:
                pass  # Nếu không có lớp học, có thể xử lý thông báo lỗi ở đây

    # Render template với các dữ liệu cần thiết
    return render(request, 'school_app/tao_ds_lop.html', {
        'nam_hoc_options': nam_hoc_options,
        'ten_lop_options': ten_lop_options,
        'selected_nam_hoc': selected_nam_hoc,
        'selected_ten_lop': selected_ten_lop,
        'hoc_sinh_chua_co_lop': hoc_sinh_chua_co_lop,
    })


@login_required(login_url='dang-nhap')
def danh_sach_lop(request, lop_id):
    lop_hoc = get_object_or_404(LopHoc, id=lop_id)
    ds_hoc_sinh = HocSinh.objects.filter(lop_hoc = lop_hoc)

    return render(request, 'school_app/ds_lop.html',{
        'lop_hoc': lop_hoc,
        'ds_hoc_sinh': ds_hoc_sinh
    })


@login_required(login_url='dang-nhap')
def xoa_hs_khoi_lop(request, lop_id, hoc_sinh_id):
    if request.method == 'POST':
        hoc_sinh = get_object_or_404(HocSinh, id = hoc_sinh_id)
        lop_hoc = get_object_or_404(LopHoc, id = lop_id)
        hoc_sinh.lop_hoc.remove(lop_hoc)
        messages.success(request, f"Học sinh {hoc_sinh.nguoi_dung.ho_ten} đã được xóa khỏi lớp thành công.",  extra_tags='delete_hs_lop')

    return redirect('danh-sach-lop', lop_id=lop_id)


@login_required(login_url='dang-nhap')
def xoa_lop_hoc(request, lop_id):
    lop_hoc = get_object_or_404(LopHoc, id = lop_id)
    nam_hoc = lop_hoc.nam_hoc.nam
    if request.method == 'POST':
        lop_hoc.delete()
    return redirect(f'/lop-hoc?nam_hoc={nam_hoc}')


@login_required(login_url='dang-nhap')
def mon_hoc(request):
    nam_hoc_options = NamHoc.objects.all()
    selected_nam_hoc = request.GET.get('nam_hoc', None)
    if selected_nam_hoc:
        ds_mon_hoc = MonHoc.objects.filter(nam_hoc__nam=selected_nam_hoc)
    else:
        ds_mon_hoc = MonHoc.objects.all()

    context = {
        'nam_hoc_options': nam_hoc_options,
        'selected_nam_hoc': selected_nam_hoc,
        'ds_mon_hoc': ds_mon_hoc,
    }
    return render(request, 'school_app/mon_hoc.html', context)

@login_required(login_url='dang-nhap')
def them_mon_hoc(request):
    if request.method == 'POST':
        form = MonHocForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm môn học thành công!", extra_tags='add_subj')
            return redirect('mon-hoc')  
    else:
        form = MonHocForm()

    return render(request, 'school_app/them_mon_hoc.html', {'form': form})

@login_required(login_url='dang-nhap')  # Đảm bảo chỉ người dùng đã đăng nhập mới có quyền xóa
def xoa_mon_hoc(request, mon_hoc_id):
    mon_hoc = get_object_or_404(MonHoc, id=mon_hoc_id)
    nam_hoc = mon_hoc.nam_hoc.nam
    if request.method == 'POST':
        try:
            mon_hoc.delete()
            messages.success(request, "Môn học đã được xóa thành công.")
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi xóa môn học: {e}")
    return redirect(f'/mon-hoc?nam_hoc={nam_hoc}')  


@login_required(login_url='dang-nhap')
def diem(request):
    # Lấy các tham số từ request.GET để lọc
    selected_nam_hoc = request.GET.get('nam_hoc', '')
    selected_lop_hoc = request.GET.get('lop_hoc', '')
    selected_mon_hoc = request.GET.get('mon_hoc', '')
    selected_hoc_ki = request.GET.get('hoc_ki', '')
    search_name = request.GET.get('search_name', '')  # Lấy tên học sinh từ tham số tìm kiếm

    # Lấy danh sách tất cả các kết quả
    ket_qua_list = KetQua.objects.all()

    # Lọc theo năm học từ lớp học
    if selected_nam_hoc:
        ket_qua_list = ket_qua_list.filter(nam_hoc__nam=selected_nam_hoc)

    # Lọc theo lớp học
    if selected_lop_hoc:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__lop_hoc__ma_lop=selected_lop_hoc)

    # Lọc theo môn học
    if selected_mon_hoc:
        ket_qua_list = ket_qua_list.filter(mon_hoc__ten_mon=selected_mon_hoc)

    # Lọc theo học kỳ
    if selected_hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=selected_hoc_ki)

    # Lọc theo tên học sinh nếu có tham số tìm kiếm
    if search_name:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__nguoi_dung__ho_ten__icontains=search_name)

    # Sắp xếp theo tên học sinh (hoặc trường tương tự trong mô hình HocSinh)
    ket_qua_list = ket_qua_list.order_by('hoc_sinh__nguoi_dung__ho_ten')  # Sắp xếp theo trường ho_ten của học sinh

    # Lấy tất cả các dữ liệu cần thiết cho dropdown
    nam_hoc_list = NamHoc.objects.all()
    lop_hoc_list = LopHoc.objects.filter(nam_hoc__nam = selected_nam_hoc)
    mon_hoc_list = MonHoc.objects.all()

    context = {
        'ket_qua_list': ket_qua_list,
        'nam_hoc_list': nam_hoc_list,
        'lop_hoc_list': lop_hoc_list,
        'mon_hoc_list': mon_hoc_list,
        'selected_nam_hoc': selected_nam_hoc,
        'selected_lop_hoc': selected_lop_hoc,
        'selected_mon_hoc': selected_mon_hoc,
        'selected_hoc_ki': selected_hoc_ki,
        'search_name': search_name,  # Truyền giá trị tìm kiếm lại cho form
    }

    return render(request, 'school_app/diem.html', context)

import openpyxl
from django.http import HttpResponse
def xuat_diem(request):
    # Lấy thông tin năm học, lớp học, học kỳ và môn học từ request
    nam_hoc = request.GET.get('nam_hoc', '2024-2025')  # Ví dụ lấy năm học từ GET request
    ma_lop = request.GET.get('lop_hoc')  # Mã lớp học (có thể lấy từ GET request)
    hoc_ki = request.GET.get('hoc_ki')  # Học kỳ (có thể lấy từ GET request, '1' hoặc '2')
    mon_hoc = request.GET.get('mon_hoc')  # Mã môn học (có thể lấy từ GET request)

    # Lấy lớp học theo mã lớp
    lop_hoc = LopHoc.objects.filter(ma_lop=ma_lop).first()

    # Kiểm tra nếu lop_hoc không tồn tại
    if lop_hoc is None:
        return HttpResponse("Lớp học không tồn tại", status=404)

    # Lấy tất cả học sinh thuộc lớp học này
    hocsinh_list = HocSinh.objects.filter(lop_hoc=lop_hoc)

    # Lọc kết quả theo học kỳ và môn học nếu có tham số hoc_ki và mon_hoc
    ket_qua_list = KetQua.objects.filter(hoc_sinh__in=hocsinh_list, nam_hoc=lop_hoc.nam_hoc)
    
    # Lọc theo học kỳ nếu có
    if hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=hoc_ki)

    # Lọc theo môn học nếu có
    if mon_hoc:
        ket_qua_list = ket_qua_list.filter(mon_hoc__ten_mon=mon_hoc)

    # Tạo workbook và worksheet mới
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Bảng điểm {lop_hoc}"

    # Đặt tiêu đề cho các cột
    ws.append([
        "Tên Học Sinh",
        "Học Kỳ",
        "Điểm 15 Phút",
        "Điểm 1 Tiết",
        "Điểm Giữa Kỳ",
        "Điểm Cuối Kỳ",
        "Điểm Tổng"
    ])

    # Thêm dữ liệu điểm của từng học sinh vào bảng Excel
    for ket_qua in ket_qua_list:
        ws.append([
            ket_qua.hoc_sinh.nguoi_dung.ho_ten,
            "Học kỳ 1" if ket_qua.hoc_ki == '1' else "Học kỳ 2",
            ket_qua.diem_15phut,
            ket_qua.diem_1tiet,
            ket_qua.diem_gk,
            ket_qua.diem_ck,
            ket_qua.diem_tong
        ])

    # Tạo response với MIME type của Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Bang_diem_{lop_hoc.ma_lop}_{nam_hoc}.xlsx'

    # Ghi dữ liệu vào file Excel và trả về phản hồi
    wb.save(response)
    return response





@login_required(login_url='dang-nhap')
def cap_nhat_diem(request, diem_id):
    ket_qua = get_object_or_404(KetQua, id=diem_id)
    lop_hoc = ket_qua.hoc_sinh.lop_hoc.first()
    if lop_hoc:
        ma_lop = lop_hoc.ma_lop
        print(ma_lop)
    nam_hoc = ket_qua.nam_hoc.nam
    mon_hoc = ket_qua.mon_hoc.ten_mon   
    hoc_ki = ket_qua.hoc_ki
    if request.method == 'POST':
        # Xử lý form chỉnh sửa điểm
        form = KetQuaForm(request.POST, instance=ket_qua)
        if form.is_valid():
            form.save()  # Lưu lại điểm đã chỉnh sửa
            return redirect(f'/diem?nam_hoc={nam_hoc}&lop_hoc={ma_lop}&mon_hoc={mon_hoc}&hoc_ki={hoc_ki}')  # Redirect lại trang danh sách điểm
    else:
        form = KetQuaForm(instance=ket_qua)  # Hiển thị form với dữ liệu hiện tại

    return render(request, 'school_app/cap_nhat_diem.html', {'form': form, 'ket_qua': ket_qua})


@login_required(login_url='dang-nhap')
def danh_sach_giao_vien(request):
    giao_vien_list = GiaoVien.objects.all()
    return render(request, 'school_app/ds_giao_vien.html', {'giao_vien_list': giao_vien_list})

# Thêm giáo viên
@login_required(login_url='dang-nhap')
def them_giao_vien(request):
    form = GiaoVienForm(request.POST or None)
    context = {
        'form': form,
    }
    storage = get_messages(request)  # Lấy thông báo đã lưu
    for message in storage:  # Tiêu thụ thông báo (không bắt buộc)
        print(f"Message: {message}")
    
    if request.method == 'POST':
        if form.is_valid():
            # Lấy dữ liệu từ form
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            ho_ten = form.cleaned_data.get('ho_ten')
            ngay_sinh = form.cleaned_data.get('ngay_sinh')
            gioi_tinh = form.cleaned_data.get('gioi_tinh')
            email = form.cleaned_data.get('email')
            dia_chi = form.cleaned_data.get('dia_chi')
            mon_day = form.cleaned_data.get('mon_day')  # Lấy môn dạy từ form

            # Kiểm tra xem username hoặc email đã tồn tại chưa
            if NguoiDung.objects.filter(username=username).exists():
                messages.error(request, "Tên đăng nhập đã được sử dụng.", extra_tags='add_teacher')
            elif NguoiDung.objects.filter(email=email).exists():
                messages.error(request, "Email đã được sử dụng.", extra_tags='add_teacher')
            else:
                try:
                    # Tạo người dùng (User)
                    user = NguoiDung.objects._create_user(
                        username=username, 
                        password=password, 
                        ho_ten=ho_ten,
                        vai_tro='2',  # Vai trò giáo viên
                        ngay_sinh=ngay_sinh,
                        gioi_tinh=gioi_tinh,
                        email=email,
                        dia_chi=dia_chi,
                    )
                    
                    # Tạo đối tượng GiaoVien và liên kết với người dùng
                    giao_vien = GiaoVien(nguoi_dung=user, mon_day=mon_day)  # Gắn môn dạy vào giáo viên
                    user.save()  # Lưu người dùng
                    giao_vien.save()  # Lưu giáo viên

                    # Thêm thông báo thành công
                    messages.success(request, "Thêm giáo viên thành công", extra_tags='add_teacher')
                except Exception as e:
                    # Xử lý lỗi và ghi log
                    logger.error(f"Lỗi khi thêm giáo viên: {e}")
                    messages.error(request, "Không thể thêm giáo viên", extra_tags='add_teacher')
        else:
            messages.error(request, "Dữ liệu không hợp lệ", extra_tags='add_teacher')
    
    return render(request, 'school_app/them_giao_vien.html', context=context)


# Sửa thông tin giáo viên
@login_required(login_url='dang-nhap')
def cap_nhat_giao_vien(request, giao_vien_id):
    giao_vien = get_object_or_404(GiaoVien, id=giao_vien_id)
    nguoi_dung = giao_vien.nguoi_dung  # Lấy đối tượng NguoiDung liên kết với GiaoVien

    if request.method == 'POST':
        form = CapNhatNguoiDungForm(request.POST, instance=nguoi_dung)  # Khởi tạo form với instance của NguoiDung
        if form.is_valid():
            # Lưu các thay đổi cho NguoiDung
            nguoi_dung = form.save()
            messages.success(request, 'Cập nhật giáo viên thành công!')
            return redirect('ds-giao-vien')  # Chuyển hướng đến danh sách giáo viên
    else:
        form = CapNhatNguoiDungForm(instance=nguoi_dung)  # Khởi tạo form với instance của NguoiDung

    return render(request, 'school_app/cap_nhat_gv.html', {'form': form, 'giao_vien': giao_vien})

# Xóa giáo viên
@login_required(login_url='dang-nhap')
def xoa_giao_vien(request, giao_vien_id):
    giao_vien = get_object_or_404(GiaoVien, id=giao_vien_id)
    nguoi_dung = giao_vien.nguoi_dung
    if request.method == 'POST':
        nguoi_dung.delete()  # Xóa giáo viên
        messages.success(request, 'Xóa giáo viên thành công!')
        return redirect('ds-giao-vien')
    return render(request, 'school_app/xoa_giao_vien.html', {'giao_vien': giao_vien})

# Phân công giáo viên dạy lớp
@login_required(login_url='dang-nhap')
def phan_cong_giao_vien(request, giao_vien_id):
    giao_vien = GiaoVien.objects.get(id=giao_vien_id)

    # Lấy danh sách môn học và năm học
    mon_hoc_list = MonHoc.objects.all()
    nam_hoc_list = NamHoc.objects.all()

    # Lọc lớp học theo năm học nếu có
    current_nam_hoc = request.GET.get('nam_hoc')  # Lấy năm học từ query parameters
    lop_hoc_list = LopHoc.objects.exclude(id__in=giao_vien.lop_day.values('id'))
    
    # Lọc lớp học đã có giáo viên khác dạy môn học
    if giao_vien.mon_day:
        lop_hoc_list = lop_hoc_list.exclude(
            id__in=LopHoc.objects.filter(
                giaovien__mon_day=giao_vien.mon_day  # Sử dụng 'giaovien' thay vì 'giao_vien'
            ).values('id')
        )

    if current_nam_hoc:  # Nếu có chọn năm học
        try:
            nam_hoc_obj = NamHoc.objects.get(nam=current_nam_hoc)
            lop_hoc_list = lop_hoc_list.filter(nam_hoc=nam_hoc_obj)
        except NamHoc.DoesNotExist:
            lop_hoc_list = []  # Nếu không tìm thấy năm học, trả về danh sách rỗng

    # Xử lý POST request
    if request.method == 'POST':
        selected_lop_hoc = request.POST.getlist('lop_hoc')  # Lớp học được chọn
        # Lưu thông tin
        giao_vien.lop_day.set(LopHoc.objects.filter(id__in=selected_lop_hoc))
        giao_vien.save()

        # Thông báo thành công
        messages.success(request, 'Phân công giáo viên thành công!')
        return redirect('ds-giao-vien')

    return render(request, 'school_app/phan_cong_gv.html', {
        'giao_vien': giao_vien,
        'lop_hoc_list': lop_hoc_list,
        'mon_hoc_list': mon_hoc_list,
        'nam_hoc_list': nam_hoc_list,
        'current_nam_hoc': current_nam_hoc,  # Gửi năm học hiện tại
    })



@login_required(login_url='dang-nhap')
def tong_ket(request):
    # Lấy danh sách các năm học và môn học
    nam_hocs = NamHoc.objects.all()
    mon_hocs = MonHoc.objects.all()

    # Lấy năm học và môn học từ yêu cầu GET
    nam_hoc_id = request.GET.get('nam_hoc_id')
    mon_hoc_id = request.GET.get('mon_hoc_id')

    # Nếu không chọn năm học, không hiển thị gì
    if not nam_hoc_id:
        return render(request, 'school_app/tong_ket.html', {
            'nam_hocs': nam_hocs,
            'mon_hocs': mon_hocs,
            'lop_data': [],
            'labels': [],
            'data_points': [],
            'selected_nam_hoc': None,
            'selected_mon_hoc': None,
        })

    # Lọc lớp học theo năm học được chọn
    lop_hocs = LopHoc.objects.filter(nam_hoc_id=nam_hoc_id)

    # Chuẩn bị dữ liệu điểm trung bình cho từng lớp theo môn học
    lop_data = []
    for lop in lop_hocs:
        # Tính điểm trung bình của lớp theo môn học nếu được chọn
        if mon_hoc_id:
            diem_tb = KetQuaMonHoc.objects.filter(
                hoc_sinh__lop_hoc=lop,
                nam_hoc_id=nam_hoc_id,
                mon_hoc_id=mon_hoc_id
            ).aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']
        else:
            # Tính điểm trung bình tổng hợp (không phân biệt môn)
            diem_tb = KetQuaMonHoc.objects.filter(
                hoc_sinh__lop_hoc=lop,
                nam_hoc_id=nam_hoc_id
            ).aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']

        # Thêm vào danh sách dữ liệu lớp
        lop_data.append({
            'ma_lop': lop.ma_lop,
            'diem_tb': round(diem_tb, 2) if diem_tb else 0
        })

    # Sắp xếp danh sách lớp theo mã lớp
    lop_data = sorted(lop_data, key=lambda x: x['ma_lop'])

    # Tách labels (tên lớp) và data points (điểm trung bình)
    labels = [lop['ma_lop'] for lop in lop_data]
    data_points = [lop['diem_tb'] for lop in lop_data]

    context = {
        'nam_hocs': nam_hocs,
        'mon_hocs': mon_hocs,
        'lop_data': lop_data,
        'labels': labels,  # Truyền labels cho template
        'data_points': data_points,  # Truyền data points cho template
        'selected_nam_hoc': int(nam_hoc_id) if nam_hoc_id else None,
        'selected_mon_hoc': int(mon_hoc_id) if mon_hoc_id else None,
    }

    return render(request, 'school_app/tong_ket.html', context)


@login_required(login_url='dang-nhap')
def ket_qua_hoc_tap(request):
    # Lấy học sinh hiện tại
    try:
        hoc_sinh = HocSinh.objects.get(nguoi_dung=request.user)
    except HocSinh.DoesNotExist:
        return render(request, 'school_app/404.html', {'message': 'Học sinh không tồn tại'})

    # Lấy năm học và học kỳ đã chọn từ GET
    selected_nam_hoc = request.GET.get('nam_hoc', None)
    selected_hoc_ki = request.GET.get('hoc_ki', None)

    if selected_nam_hoc:
        try:
            nam_hoc = NamHoc.objects.get(nam=selected_nam_hoc)
        except NamHoc.DoesNotExist:
            nam_hoc = None
    else:
        nam_hoc = None

    # Lấy lớp học của học sinh trong năm học đã chọn
    lop_hoc = None
    if nam_hoc:
        lop_hoc = hoc_sinh.lop_hoc.filter(nam_hoc=nam_hoc).first()  # Lấy lớp học đầu tiên trong năm học này

    # Lấy kết quả học tập
    ket_qua_hoc_ky = None
    ket_qua_mon_hoc = None
    ket_qua_nam_hoc = None

    if nam_hoc:
        if selected_hoc_ki:  # Nếu người dùng chọn học kỳ
            # Kết quả học kỳ (Học kỳ 1 hoặc Học kỳ 2)
            ket_qua_hoc_ky = KetQua.objects.filter(
                hoc_sinh=hoc_sinh,
                nam_hoc=nam_hoc,
                hoc_ki=selected_hoc_ki
            )
        else:
            # Kết quả môn học cả năm
            ket_qua_mon_hoc = KetQuaMonHoc.objects.filter(
                hoc_sinh=hoc_sinh,
                nam_hoc=nam_hoc
            )

            # Kết quả tổng kết năm học
            try:
                ket_qua_nam_hoc = KetQuaNamHoc.objects.get(
                    hoc_sinh=hoc_sinh,
                    nam_hoc=nam_hoc
                )
            except KetQuaNamHoc.DoesNotExist:
                ket_qua_nam_hoc = None

    # Danh sách tất cả các năm học
    danh_sach_nam_hoc = hoc_sinh.lop_hoc.values_list('nam_hoc__nam', flat=True).distinct()

    # Tạo context để gửi dữ liệu sang template
    context = {
        'lop_hoc': lop_hoc, 
        'danh_sach_nam_hoc': danh_sach_nam_hoc,  
        'selected_nam_hoc': selected_nam_hoc,  
        'selected_hoc_ki': selected_hoc_ki,  
        'ket_qua_hoc_ky': ket_qua_hoc_ky,  
        'ket_qua_mon_hoc': ket_qua_mon_hoc,  
        'ket_qua_nam_hoc': ket_qua_nam_hoc,  
    }

    return render(request, 'school_app/ket_qua_hoc_tap.html', context)



from django.http import HttpResponseForbidden

@login_required(login_url='dang-nhap')
def quan_ly_diem(request):
    try:
        # Lấy thông tin giáo viên đang đăng nhập
        giao_vien = GiaoVien.objects.get(nguoi_dung=request.user)
    except GiaoVien.DoesNotExist:
        # Nếu giáo viên không tồn tại, trả về thông báo lỗi
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    # Lấy tham số lọc từ GET
    selected_nam_hoc = request.GET.get('nam_hoc', None)
    selected_hoc_ki = request.GET.get('hoc_ki', None)
    selected_lop_hoc = request.GET.get('lop_hoc', None)

    # Lấy danh sách lớp học mà giáo viên dạy
    lop_hoc_list = LopHoc.objects.filter(giaovien=giao_vien, nam_hoc__nam = selected_nam_hoc)

    # Lấy danh sách năm học
    nam_hoc_list = NamHoc.objects.all()

    # Lọc danh sách kết quả học tập
    ket_qua_list = KetQua.objects.filter(
        hoc_sinh__lop_hoc__in=lop_hoc_list,  # Lọc kết quả học sinh chỉ thuộc lớp mà giáo viên được phân công
        mon_hoc__giaovien=giao_vien  # Chỉ môn học mà giáo viên dạy
    )

    # Áp dụng các bộ lọc từ tham số GET
    if selected_nam_hoc:
        ket_qua_list = ket_qua_list.filter(nam_hoc__nam=selected_nam_hoc)
    if selected_hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=selected_hoc_ki)
    if selected_lop_hoc:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__lop_hoc__ma_lop=selected_lop_hoc)

    mon_hoc = MonHoc.objects.filter(giaovien=giao_vien).first()
    context = {
        'nam_hoc_list': nam_hoc_list,
        'lop_hoc_list': lop_hoc_list,
        'ket_qua_list': ket_qua_list,
        'selected_nam_hoc': selected_nam_hoc,
        'selected_hoc_ki': selected_hoc_ki,
        'selected_lop_hoc': selected_lop_hoc,
        'mon_hoc': mon_hoc
    }

    return render(request, 'school_app/home_giao_vien.html', context) 


@login_required(login_url='dang-nhap')
def cap_nhat_diem_gv(request, diem_id):
    ket_qua = get_object_or_404(KetQua, id=diem_id)
    lop_hoc = ket_qua.hoc_sinh.lop_hoc.first()
    if lop_hoc:
        ma_lop = lop_hoc.ma_lop
        print(ma_lop)
    nam_hoc = ket_qua.nam_hoc.nam 
    hoc_ki = ket_qua.hoc_ki
    if request.method == 'POST':
        # Xử lý form chỉnh sửa điểm
        form = KetQuaForm(request.POST, instance=ket_qua)
        if form.is_valid():
            form.save()  # Lưu lại điểm đã chỉnh sửa
            return redirect(f'/quan-ly-diem?nam_hoc={nam_hoc}&lop_hoc={ma_lop}&hoc_ki={hoc_ki}')  # Redirect lại trang danh sách điểm
    else:
        form = KetQuaForm(instance=ket_qua)  # Hiển thị form với dữ liệu hiện tại

    return render(request, 'school_app/cap_nhat_diem_gv.html', {'form': form, 'ket_qua': ket_qua})


