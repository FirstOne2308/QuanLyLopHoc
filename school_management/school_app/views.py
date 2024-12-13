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
                return redirect('/')
            elif user.vai_tro == '3':
                return redirect('/')
        else:
            # Thêm thông báo lỗi nếu thông tin không hợp lệ
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác!")

    # Render giao diện login
    return render(request, 'school_app/dang_nhap.html')


def dang_xuat(request):
    logout(request)
    return redirect("/")

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
            password = form.cleaned_data.get('password')
            ho_ten = form.cleaned_data.get('ho_ten')
            ngay_sinh = form.cleaned_data.get('ngay_sinh')
            gioi_tinh = form.cleaned_data.get('gioi_tinh')
            email = form.cleaned_data.get('email')
            dia_chi = form.cleaned_data.get('dia_chi')
            try:
                user = NguoiDung.objects._create_user(
                    username=username, 
                    password=password, 
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
                logger.error(f"Lỗi khi thêm học sinh: {e}")
                messages.error(request, "Không thể thêm",extra_tags='add_student')
        else:
            messages.error(request, "Dữ liệu không phù hợp",extra_tags='add_student')
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
            messages.success(request, "Thêm môn học thành công!")
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


@login_required(login_url='dang-nhap')  # Đảm bảo chỉ người dùng đã đăng nhập mới có quyền xóa
def diem(request):
    # Lấy các tham số từ request.GET để lọc
    selected_nam_hoc = request.GET.get('nam_hoc', '')
    selected_lop_hoc = request.GET.get('lop_hoc', '')
    selected_mon_hoc = request.GET.get('mon_hoc', '')
    selected_hoc_ki = request.GET.get('hoc_ki', '')

    # Lấy danh sách tất cả các kết quả
    ket_qua_list = KetQua.objects.all()

    # Lọc theo năm học từ lớp học
    if selected_nam_hoc:
        ket_qua_list = ket_qua_list.filter(
            nam_hoc__nam=selected_nam_hoc)

    # Lọc theo lớp học
    if selected_lop_hoc:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__lop_hoc__ma_lop=selected_lop_hoc)

    # Lọc theo môn học
    if selected_mon_hoc:
        ket_qua_list = ket_qua_list.filter(mon_hoc__ten_mon=selected_mon_hoc)

    # Lọc theo học kỳ
    if selected_hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=selected_hoc_ki)

    # Lấy tất cả các dữ liệu cần thiết cho dropdown
    nam_hoc_list = NamHoc.objects.all()
    lop_hoc_list = LopHoc.objects.all()
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
    }

    return render(request, 'school_app/diem.html', context)


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



def danh_sach_giao_vien(request):
    giao_vien_list = GiaoVien.objects.all()
    return render(request, 'school_app/ds_giao_vien.html', {'giao_vien_list': giao_vien_list})

# Thêm giáo viên
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
def xoa_giao_vien(request, giao_vien_id):
    giao_vien = get_object_or_404(GiaoVien, id=giao_vien_id)
    if request.method == 'POST':
        giao_vien.delete()  # Xóa giáo viên
        messages.success(request, 'Xóa giáo viên thành công!')
        return redirect('ds-giao-vien')
    return render(request, 'school_app/xoa_giao_vien.html', {'giao_vien': giao_vien})

# Phân công giáo viên dạy lớp
# def phan_cong_giao_vien(request, pk):
#     giao_vien = get_object_or_404(GiaoVien, pk=pk)
#     if request.method == 'POST':
#         form = GiaoVienForm(request.POST, instance=giao_vien)
#         if form.is_valid():
#             form.save()  # Lưu phân công giáo viên
#             messages.success(request, 'Phân công giáo viên thành công!')
#             return redirect('danh_sach_giao_vien')
#     else:
#         form = GiaoVienForm(instance=giao_vien)
#     return render(request, 'school_app/phan_cong_giao_vien.html', {'form': form, 'giao_vien': giao_vien})