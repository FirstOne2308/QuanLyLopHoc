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
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# def check_role(user):
#     return user.is_authenticated and user.vai_tro != "Quản trị viên"  # check quyền


# Create your views here.
#Trang chủ 
@login_required(login_url='dang-nhap')
def home(request):
    """
        Home: giao diện trang chủ của tất cả người dùng

        Input: request

        Trả về: giao diện trang chủ 
    """
    return render(request, 'school_app/home.html')

#Đăng nhập 
def dangnhap(request):
    """
        Trang đăng nhập

        Input: request

        Trả về: giao diện trang đăng nhập
    """
    return render(request, 'school_app/dang_nhap.html')

#Xử lý đăng nhập
def xulydangnhap(request):
    """
    Hàm xử lý logic đăng nhập.

    Input: request, username, password

    Trả về:
        - Nếu đăng nhập sai, trả về thông báo lỗi "Tên đăng nhập hoặc mật khẩu không chính xác!"
        - Nếu đăng nhập đúng, chuyển người dùng tới giao diện trang chủ
    """
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.vai_tro == '1':
                return redirect('/')
            elif user.vai_tro == '2':
                return redirect('/')
            elif user.vai_tro == '3':
                return redirect('/')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác!")

    return render(request, 'school_app/dang_nhap.html')


#Đăng xuất
@login_required(login_url='dang-nhap')
def dang_xuat(request):
    """
    Hàm xử lý đăng xuất:

    Input: request

    Trả về: chuyển hướng đến giao diện đăng nhập
    """
    logout(request)
    return redirect("/")


#Trang cá nhân
@login_required(login_url='dang-nhap')
def trang_ca_nhan(request):
    """
    Trang cá nhân

    Input: request

    Trả về: chuyển hướng đến giao diện trang cá nhân gồm các thông tin cá nhân của người dùng
    """
    return render(request, 'school_app/trang_ca_nhan.html')


#Thêm học sinh
@login_required(login_url='dang-nhap')
def them_hoc_sinh(request):
    """
    Trang thêm mới học sinh

    Input: request, thông tin của học sinh như username, ho_ten, ngay_sinh,...

    Trả vè: 
        - Nếu thêm học sinh thành công: trả về thông báo Thêm thành công
        - Nếu thêm học sinh thất bại: trả về thông báo Không thể thêm 
            (Vì lý do tên đăng nhập hoặc email đã có)
    """
    form = HocSinhForm(request.POST or None)
    context = {
        'form': form,
    }
    storage = get_messages(request)  
    for message in storage:  
        print(f"Message: {message}")
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            ho_ten = form.cleaned_data.get('ho_ten')
            ngay_sinh = form.cleaned_data.get('ngay_sinh')
            gioi_tinh = form.cleaned_data.get('gioi_tinh')
            email = form.cleaned_data.get('email')
            dia_chi = form.cleaned_data.get('dia_chi')
            if ngay_sinh:
                ngay_sinh_str = ngay_sinh.strftime('%d%m%Y')  
                password = ngay_sinh_str  

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
                print(e)
                logger.error(f"Lỗi khi thêm học sinh: {e}")
                messages.error(request, "Không thể thêm do tên đăng nhập hoặc email đã tồn tại", extra_tags='add_student')
        else:
            messages.error(request, "Dữ liệu không phù hợp", extra_tags='add_student')
    
    return render(request, 'school_app/them_hoc_sinh.html', context=context)


#Lấy danh sách tất cả học sinh
@login_required(login_url='dang-nhap')
def hoc_sinh(request):
    """
    Trang danh sách học sinh

    Input: request, query(tên học sinh)

    Trả về: Danh sách học sinh sắp xếp theo tên và được phân trang
    """
    search_query = request.GET.get('ten_hoc_sinh', '')
    if search_query:
        ds_hoc_sinh = HocSinh.objects.filter(
            nguoi_dung__ho_ten__icontains=search_query)
        ds_hoc_sinh = sorted(ds_hoc_sinh, key=lambda hocsinh: hocsinh.nguoi_dung.ho_ten.split()[-1].lower())
    else:
        ds_hoc_sinh = HocSinh.objects.all()
        ds_hoc_sinh = sorted(ds_hoc_sinh, key=lambda hocsinh: hocsinh.nguoi_dung.ho_ten.split()[-1].lower())

    # Phân trang
    paginator = Paginator(ds_hoc_sinh, 10)  # Mỗi trang hiển thị 10 học sinh
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'school_app/hoc_sinh.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


# Cập nhật thông tin học sinh
@login_required(login_url='dang-nhap')
def cap_nhat_hoc_sinh(request, hoc_sinh_id):
    """
    Trang cập nhật học sinh

    Input: request, thông tin cần cập nhật như username, ho_ten,...

    Trả về: 
        - Nếu cập nhật thành công, thông báo thành công 
        - Nếu cập nhật thất bại, thông báo không thể cập nhật
    """
    hoc_sinh = get_object_or_404(HocSinh, id=hoc_sinh_id)
    print(hoc_sinh)
    if request.method == "POST":
        form = CapNhatNguoiDungForm(request.POST, instance=hoc_sinh.nguoi_dung)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật thành công", extra_tags='update_student')
                return redirect('cap-nhat-hoc-sinh', hoc_sinh_id = hoc_sinh_id) 
            except Exception as e:
                print(e)
                messages.error(request, "Có lỗi khi cập nhật học sinh", extra_tags='update_student')
    else:
        form = CapNhatNguoiDungForm(instance=hoc_sinh.nguoi_dung)

    return render(request, 'school_app/cap_nhat_hs.html', {'form': form})


# Xóa học sinh
@login_required(login_url='dang-nhap')
def xoa_hoc_sinh(request, hoc_sinh_id):
    """
    Xóa học sinh

    Input: request, hoc_sinh_id

    Trả về: Thông báo xóa thành công, chuyển hướng về lại trang danh sách học sinh
    """
    hoc_sinh = get_object_or_404(HocSinh, id=hoc_sinh_id)
    nguoi_dung = NguoiDung.objects.filter(username=hoc_sinh.nguoi_dung.username)
    if request.method == 'POST':
        nguoi_dung.delete()  
        messages.success(request, "Xóa học sinh thành công!")
    return redirect('hoc-sinh')

# Danh sách tất cả lớp học
@login_required(login_url='dang-nhap')
def lop_hoc(request):
    """
    Danh sách lớp học

    Input: request

    Trả về: Chuyển hướng người dùng tới trang danh sách các lớp học
    """
    lop_hoc_list = LopHoc.objects.all()
    lop_hoc_list = lop_hoc_list.annotate(so_hs=Count('hocsinh'))
    current_nam_hoc = request.GET.get('nam_hoc', None)
    if current_nam_hoc:
        try:
            nam_hoc_obj = NamHoc.objects.get(nam=current_nam_hoc)
            lop_hoc_list = lop_hoc_list.filter(nam_hoc=nam_hoc_obj)
            lop_hoc_list = lop_hoc_list.annotate(so_hs=Count('hocsinh'))
        except NamHoc.DoesNotExist:
            lop_hoc_list = lop_hoc_list.none()

    nam_hoc_options = NamHoc.objects.all()
    ten_lop_options = LopHoc.objects.values_list('ma_lop', flat=True).distinct()

    return render(request, 'school_app/lop_hoc.html', {
        'lop_hoc_list': lop_hoc_list,
        'nam_hoc_options': nam_hoc_options,
        'ten_lop_options': ten_lop_options,  
        'current_nam_hoc': current_nam_hoc,
    })


# Thêm lớp học mới
@login_required(login_url='dang-nhap')
def them_lop_hoc(request):
    """
    Trang thêm lớp học

    Input: request, thông tin lớp học như: ma_lop, so_hoc_sinh, nam_hoc

    Trả về: Chuyển hướng người dùng tới trang thêm lớp học, form tạo lớp học
    """
    if request.method == 'POST':
        form = LopHocForm(request.POST)
        
        if form.is_valid():
            nam_hoc = form.cleaned_data['nam_hoc']
            giao_vien_chu_nhiem = form.cleaned_data['giao_vien_chu_nhiem']
            if LopHoc.objects.filter(nam_hoc=nam_hoc, giao_vien_chu_nhiem=giao_vien_chu_nhiem).exists():
                messages.error(request, "Giáo viên đã làm chủ nhiệm lớp trong năm học này!")
                return render(request, 'school_app/them_lop_hoc.html', {'form': form})
            lop_hoc = form.save()
            messages.success(request, "Thêm lớp học thành công!")
            return redirect('lop-hoc')  
    
    else:
        form = LopHocForm()

    return render(request, 'school_app/them_lop_hoc.html', {'form': form})


#Tạo danh sách lớp(Thêm học sinh vào lớp)
@login_required(login_url='dang-nhap')
def tao_danh_sach_lop(request):
    nam_hoc_options = NamHoc.objects.all()
    ten_lop_options = LopHoc.objects.all()

    selected_nam_hoc = request.GET.get('nam_hoc')
    selected_ten_lop = request.GET.get('ten_lop')  # Đây sẽ là `id` của lớp học

    lop_hoc_nam_hoc = LopHoc.objects.all()
    hoc_sinh_chua_co_lop = HocSinh.objects.all()

    # Lọc danh sách lớp và học sinh theo năm học
    if selected_nam_hoc:
        try:
            nam_hoc = NamHoc.objects.get(nam=selected_nam_hoc)
            ten_lop_options = ten_lop_options.filter(nam_hoc=nam_hoc)
            lop_hoc_nam_hoc = lop_hoc_nam_hoc.filter(nam_hoc=nam_hoc)
            hoc_sinh_chua_co_lop = HocSinh.objects.exclude(lop_hoc__in=lop_hoc_nam_hoc)
        except NamHoc.DoesNotExist:
            nam_hoc = None  

    # Lọc danh sách học sinh chưa có lớp nếu lớp được chọn
    if selected_ten_lop:
        hoc_sinh_chua_co_lop = hoc_sinh_chua_co_lop.exclude(lop_hoc__id=selected_ten_lop)

    # Xử lý thêm học sinh vào lớp
    if request.method == 'POST':
        hoc_sinh_ids = request.POST.getlist('hoc_sinh_ids')
        lop_id = request.POST.get('lop_id')  # Nhận id lớp từ POST

        if lop_id:
            try:
                lop_hoc = LopHoc.objects.get(id=lop_id)
                so_hien_tai = lop_hoc.hocsinh_set.count()

                if so_hien_tai + len(hoc_sinh_ids)>= lop_hoc.so_hoc_sinh:
                    messages.error(
                        request,
                        f"Lớp {lop_hoc.ma_lop} đã đủ học sinh ({so_hien_tai}/{lop_hoc.so_hoc_sinh}). Không thể thêm học sinh mới.",
                        extra_tags='full_class'
                    )
                else:
                    for hoc_sinh_id in hoc_sinh_ids:
                        hoc_sinh = HocSinh.objects.get(id=hoc_sinh_id)
                        hoc_sinh.lop_hoc.add(lop_hoc)

                    messages.success(
                        request,
                        f"Học sinh đã được thêm vào lớp {lop_hoc.ma_lop}.",
                        extra_tags='add_hs_lop'
                    )
                    return redirect(f'/lop-hoc?nam_hoc={lop_hoc.nam_hoc.nam}')  
            except LopHoc.DoesNotExist:
                messages.error(request, "Lớp học không tồn tại.", extra_tags="invalid_lop_hoc")

    return render(request, 'school_app/tao_ds_lop.html', {
        'nam_hoc_options': nam_hoc_options,
        'ten_lop_options': ten_lop_options,
        'selected_nam_hoc': selected_nam_hoc,
        'selected_ten_lop': selected_ten_lop,
        'hoc_sinh_chua_co_lop': hoc_sinh_chua_co_lop,
    })



# Xem danh sách lớp
@login_required(login_url='dang-nhap')

def danh_sach_lop(request, lop_id):
    """
    Trang danh sách lớp 

    Input: request, lop_id

    Trả về: Chuyển hướng người dùng tới trang danh sách các học sinh của lớp học đó
    """
    lop_hoc = get_object_or_404(LopHoc, id=lop_id)
    ds_hoc_sinh = HocSinh.objects.filter(lop_hoc=lop_hoc)
    ds_hoc_sinh = sorted(ds_hoc_sinh, key=lambda hocsinh: hocsinh.nguoi_dung.ho_ten.split()[-1].lower())
    for hocsinh in ds_hoc_sinh:
        ket_qua_nam_hoc = KetQuaNamHoc.objects.filter(
            hoc_sinh=hocsinh,
            nam_hoc=lop_hoc.nam_hoc
        ).first()
        if ket_qua_nam_hoc:
            hocsinh.hanh_kiem = ket_qua_nam_hoc.hanh_kiem
        else:
            hocsinh.hanh_kiem = None

    return render(request, 'school_app/ds_lop.html',{
        'lop_hoc': lop_hoc,
        'ds_hoc_sinh': ds_hoc_sinh
    })


# Sửa hạnh kiểm cho từng học sinh
@csrf_exempt
def sua_hanh_kiem(request, lop_id, hoc_sinh_id):
    """
    Sửa hạnh kiểm

    Input: request, lop_id, hoc_sinh_id

    Ghi chú: chỉ có admin hoặc giáo viên chủ nhiệm mới có quyền chỉnh sửa hạnh kiểm 

    Trả về: Trả về trang danh sách học sinh lớp học đó có hạnh kiểm đã được cập nhật
    """
    if request.method == "POST":
        hanh_kiem = request.POST.get('hanh_kiem')
        lop_hoc = get_object_or_404(LopHoc, id=lop_id)
        hoc_sinh = get_object_or_404(HocSinh, id=hoc_sinh_id)
        nam_hoc = lop_hoc.nam_hoc
        ket_qua_nam_hoc = KetQuaNamHoc.objects.filter(
            hoc_sinh=hoc_sinh, nam_hoc=nam_hoc
        ).first()
        if ket_qua_nam_hoc:
            ket_qua_nam_hoc.hanh_kiem = hanh_kiem
            ket_qua_nam_hoc.save()
        return redirect(request.META.get('HTTP_REFERER'))
    

# Xuất danh sách lớp
@login_required(login_url='dang-nhap')
def xuat_ds_lop(request, lop_hoc_id):
    """
    Xuất danh sách lớp

    Input: request, lop_id

    Ghi chú: chỉ có admin hoặc giáo viên chủ nhiệm mới có quyền xuất danh sách lớp

    Trả về: file excel chứa thông tin học sinh của lớp đó
    """
    lop_hoc = LopHoc.objects.get(id=lop_hoc_id)
    ds_hoc_sinh = HocSinh.objects.filter(lop_hoc=lop_hoc)
    ds_hoc_sinh = sorted(ds_hoc_sinh, key=lambda hocsinh: hocsinh.nguoi_dung.ho_ten.split()[-1].lower())
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Danh sách lớp {lop_hoc.ma_lop}"
    headers = ["STT", "Họ và tên", "Ngày sinh", "Giới tính", "Email", "Địa chỉ"]
    ws.append(headers)
    for index, hocsinh in enumerate(ds_hoc_sinh, start=1):
        row = [
            index,
            hocsinh.nguoi_dung.ho_ten,
            hocsinh.nguoi_dung.ngay_sinh.strftime('%d/%m/%Y'),
            'Nam' if hocsinh.nguoi_dung.gioi_tinh == '1' else 'Nữ',
            hocsinh.nguoi_dung.email,
            hocsinh.nguoi_dung.dia_chi
        ]
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="danh_sach_lop_{lop_hoc.ma_lop}.xlsx"'
    wb.save(response)
    return response


# Xóa học sinh khỏi lớp 
@login_required(login_url='dang-nhap')
def xoa_hs_khoi_lop(request, lop_id, hoc_sinh_id):
    """
    Xóa học sinh khỏi lớp

    Input: request, lop_id, hoc_sinh_id

    Ghi chú: chỉ có quản trị viên mới có quyền xóa học sinh ra khỏi lớp

    Trả về: trang danh sách lớp đó sau khi xóa và thông báo đã xóa học sinh khỏi lớp thành công
    """
    if request.method == 'POST':
        hoc_sinh = get_object_or_404(HocSinh, id = hoc_sinh_id)
        lop_hoc = get_object_or_404(LopHoc, id = lop_id)
        hoc_sinh.lop_hoc.remove(lop_hoc)
        messages.success(request, f"Học sinh {hoc_sinh.nguoi_dung.ho_ten} đã được xóa khỏi lớp thành công.",  extra_tags='delete_hs_lop')

    return redirect('danh-sach-lop', lop_id=lop_id)


@login_required(login_url='dang-nhap')
def xoa_lop_hoc(request, lop_id):
    """
    Xóa lớp học 

    Input: request, lop_id

    Ghi chú: chỉ có quản trị viên mới có quyền xóa lớp học

    Trả về: Danh sách các lớp học sau khi xóa
    """
    lop_hoc = get_object_or_404(LopHoc, id = lop_id)
    nam_hoc = lop_hoc.nam_hoc.nam
    if request.method == 'POST':
        lop_hoc.delete()
    return redirect(f'/lop-hoc?nam_hoc={nam_hoc}')


@login_required(login_url='dang-nhap')
def mon_hoc(request):
    """
    Danh sách môn học   

    Input: request

    Trả về: chuyển hướng tới trang danh sách môn học gồm các thông tin của môn học đó
    """
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
    """
    Thêm môn học

    Input: request

    Ghi chú: chỉ có quản trị viên mới có quyền thêm môn học

    Trả về: Danh sách các môn học sau khi thêm
    """
    if request.method == 'POST':
        form = MonHocForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm môn học thành công!", extra_tags='add_subj')
            return redirect('mon-hoc')  
    else:
        form = MonHocForm()

    return render(request, 'school_app/them_mon_hoc.html', {'form': form})


@login_required(login_url='dang-nhap')
def sua_mon_hoc(request, mon_hoc_id):
    """
    Sửa môn học

    Input: request

    Ghi chú: chỉ có quản trị viên mới có quyền thêm môn học

    Trả về: Danh sách các môn học sau khi thêm, form thông tin môn học
    """
    mon_hoc = get_object_or_404(MonHoc, id=mon_hoc_id)
    print(mon_hoc)
    if request.method == 'POST':
        form = MonHocForm(request.POST, instance=mon_hoc)
        if form.is_valid():
            form.save()
            messages.success(request, "Sửa môn học thành công!", extra_tags='upd_subj')
            return redirect('mon-hoc')  
    else:
        # Truyền instance để hiển thị thông tin hiện tại của môn học
        form = MonHocForm(instance=mon_hoc_id)
    print(form)
    return render(request, 'school_app/sua_mon_hoc.html', {'form': form})

@login_required(login_url='dang-nhap')  
def xoa_mon_hoc(request, mon_hoc_id):
    """
    Xóa môn học

    Input: request, mon_hoc_id

    Ghi chú: chỉ có quản trị viên mới có quyền xóa môn học

    Trả về: Danh sách các môn học sau khi xóa
    """
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
    """
    Danh sách điểm: trang danh sách điểm của từng học sinh, có thể lọc theo năm học, môn học, học kỳ, hoặc tra cứu bằng tên

    Input: request

    Trả về: Danh sách điểm của học sinh
    """
    selected_nam_hoc = request.GET.get('nam_hoc', '')
    selected_lop_hoc = request.GET.get('lop_hoc', '')
    selected_mon_hoc = request.GET.get('mon_hoc', '')
    selected_hoc_ki = request.GET.get('hoc_ki', '')
    search_name = request.GET.get('search_name', '')  
    ket_qua_list = KetQua.objects.all()

    if selected_nam_hoc:
        ket_qua_list = ket_qua_list.filter(nam_hoc__nam=selected_nam_hoc)

    if selected_lop_hoc:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__lop_hoc__ma_lop=selected_lop_hoc)

    if selected_mon_hoc:
        ket_qua_list = ket_qua_list.filter(mon_hoc__ten_mon=selected_mon_hoc)

    if selected_hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=selected_hoc_ki)

    if search_name:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__nguoi_dung__ho_ten__icontains=search_name)

    ket_qua_list = ket_qua_list.order_by('hoc_sinh__nguoi_dung__ho_ten')  

    paginator = Paginator(ket_qua_list, 10)
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    nam_hoc_list = NamHoc.objects.all()
    lop_hoc_list = LopHoc.objects.filter(nam_hoc__nam=selected_nam_hoc)
    mon_hoc_list = MonHoc.objects.all()

    context = {
        'ket_qua_list': page_obj,  
        'nam_hoc_list': nam_hoc_list,
        'lop_hoc_list': lop_hoc_list,
        'mon_hoc_list': mon_hoc_list,
        'selected_nam_hoc': selected_nam_hoc,
        'selected_lop_hoc': selected_lop_hoc,
        'selected_mon_hoc': selected_mon_hoc,
        'selected_hoc_ki': selected_hoc_ki,
        'search_name': search_name,  
    }

    return render(request, 'school_app/diem.html', context)


import openpyxl
from django.http import HttpResponse, HttpResponseForbidden
def xuat_diem(request):
    """
        Xuất điểm học sinh theo năm học, môn học, học kỳ

        Input: request

        Trả về: file excel chứa danh sách điểm của học sinh
    """
    nam_hoc = request.GET.get('nam_hoc', '2024-2025')  
    ma_lop = request.GET.get('lop_hoc')  
    hoc_ki = request.GET.get('hoc_ki')  
    mon_hoc = request.GET.get('mon_hoc')  
    lop_hoc = LopHoc.objects.filter(ma_lop=ma_lop).first()
    if lop_hoc is None:
        return HttpResponse("Lớp học không tồn tại", status=404)
    hocsinh_list = HocSinh.objects.filter(lop_hoc=lop_hoc)
    ket_qua_list = KetQua.objects.filter(hoc_sinh__in=hocsinh_list, nam_hoc=lop_hoc.nam_hoc)
    if hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=hoc_ki)
    if mon_hoc:
        ket_qua_list = ket_qua_list.filter(mon_hoc__ten_mon=mon_hoc)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Bảng điểm {lop_hoc}"
    ws.append([
        "Tên Học Sinh",
        "Học Kỳ",
        "Điểm 15 Phút",
        "Điểm 1 Tiết",
        "Điểm Giữa Kỳ",
        "Điểm Cuối Kỳ",
        "Điểm Tổng"
    ])
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

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Bang_diem_{lop_hoc.ma_lop}_{nam_hoc}.xlsx'

    wb.save(response)
    return response





@login_required(login_url='dang-nhap')
def cap_nhat_diem(request, diem_id):
    """
    Cập nhật điểm

    Input: request, diem_id

    Ghi chú: chỉ có quản trị viên hoặc giáo viên dạy đúng bộ môn đó và lớp đó mới có quyền sửa điểm

    Trả về: Thông báo cập nhật điểm thành công, danh sách điểm sau khi cập nhật
    """
    ket_qua = get_object_or_404(KetQua, id=diem_id)

    if request.method == 'POST':
        form = KetQuaForm(request.POST, instance=ket_qua)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Cập nhật điểm thành công!')
            return redirect(request.META.get('HTTP_REFERER'))  # Redirect lại trang danh sách điểm
    else:
        form = KetQuaForm(instance=ket_qua) 

    return render(request, 'school_app/cap_nhat_diem.html', {'form': form, 'ket_qua': ket_qua})


@login_required(login_url='dang-nhap')
def danh_sach_giao_vien(request):
    """
    Danh sách giáo viên

    Input: request

    Ghi chú: chỉ có quản trị viên mới có quyền xem danh sách giáo viên

    Trả về: Chuyển hướng tới trang danh sách giáo viên
    """
    giao_vien_list = GiaoVien.objects.all()
    giao_vien_list = sorted(giao_vien_list, key=lambda gv: gv.nguoi_dung.ho_ten.split()[-1].lower())
    return render(request, 'school_app/ds_giao_vien.html', {'giao_vien_list': giao_vien_list})


@login_required(login_url='dang-nhap')
def them_giao_vien(request):
    """
    Thêm giáo viên

    Input: request, thông tin của giáo viên cần thêm: username, ho_ten, email,...

    Ghi chú: chỉ có quản trị viên mới có quyền thêm giáo viên

    Trả về: 
        - form thông tin giáo viên
        - Nếu thêm giáo viên thành công, thông báo thêm giáo viên thành công
        - Nếu thêm giáo viên thất bại, thông báo thêm giáo viên thất bại
    """
    form = GiaoVienForm(request.POST or None)
    context = {
        'form': form,
    }
    storage = get_messages(request)  
    for message in storage:  
        print(f"Message: {message}")
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            ho_ten = form.cleaned_data.get('ho_ten')
            ngay_sinh = form.cleaned_data.get('ngay_sinh')
            gioi_tinh = form.cleaned_data.get('gioi_tinh')
            email = form.cleaned_data.get('email')
            so_dien_thoai = form.cleaned_data.get('so_dien_thoai')
            dia_chi = form.cleaned_data.get('dia_chi')
            mon_day = form.cleaned_data.get('mon_day')  

            if NguoiDung.objects.filter(username=username).exists():
                messages.error(request, "Tên đăng nhập đã được sử dụng.", extra_tags='add_teacher')
            elif NguoiDung.objects.filter(email=email).exists():
                messages.error(request, "Email đã được sử dụng.", extra_tags='add_teacher')
            else:
                try:
                    user = NguoiDung.objects._create_user(
                        username=username, 
                        password=password, 
                        ho_ten=ho_ten,
                        vai_tro='2',  
                        ngay_sinh=ngay_sinh,
                        gioi_tinh=gioi_tinh,
                        email=email,
                        so_dien_thoai=so_dien_thoai,
                        dia_chi=dia_chi,
                    )
                    
                    giao_vien = GiaoVien(nguoi_dung=user, mon_day=mon_day)  
                    user.save()  
                    giao_vien.save()  
                    messages.success(request, "Thêm giáo viên thành công", extra_tags='add_teacher')
                except Exception as e:
                    logger.error(f"Lỗi khi thêm giáo viên: {e}")
                    messages.error(request, "Không thể thêm giáo viên", extra_tags='add_teacher')
        else:
            messages.error(request, "Dữ liệu không hợp lệ", extra_tags='add_teacher')
    
    return render(request, 'school_app/them_giao_vien.html', context=context)


@login_required(login_url='dang-nhap')
def cap_nhat_giao_vien(request, giao_vien_id):
    """
    Cập nhật giáo viên

    Input: request, giao_vien_id, thông tin của giáo viên cần cập nhật: username, ho_ten, email,...

    Ghi chú: chỉ có quản trị viên mới có quyền cập nhật giáo viên

    Trả về: 
        - form thông tin giáo viên
        - Nếu cập nhật giáo viên thành công, thông báo thêm giáo viên thành công
    """
    giao_vien = get_object_or_404(GiaoVien, id=giao_vien_id)
    nguoi_dung = giao_vien.nguoi_dung  

    if request.method == 'POST':
        form = CapNhatNguoiDungForm(request.POST, instance=nguoi_dung)  
        if form.is_valid():
            nguoi_dung = form.save()
            messages.success(request, 'Cập nhật giáo viên thành công!')
            return redirect('ds-giao-vien')  
    else:
        form = CapNhatNguoiDungForm(instance=nguoi_dung)  

    return render(request, 'school_app/cap_nhat_gv.html', {'form': form, 'giao_vien': giao_vien})

# Xóa giáo viên
@login_required(login_url='dang-nhap')
def xoa_giao_vien(request, giao_vien_id):
    """
    Xóa giáo viên

    Input: request, giao_vien_id

    Ghi chú: chỉ có quản trị viên mới có quyền xóa giáo viên

    Trả về: Thông báo xóa giáo viên thành công và trả về danh sách giáo viên sau khi xóa
    """
    giao_vien = get_object_or_404(GiaoVien, id=giao_vien_id)
    nguoi_dung = giao_vien.nguoi_dung
    if request.method == 'POST':
        nguoi_dung.delete()  # Xóa giáo viên
        messages.success(request, 'Xóa giáo viên thành công!')
        return redirect('ds-giao-vien')
    return render(request, 'school_app/xoa_giao_vien.html', {'giao_vien': giao_vien})


# Phân công giáo viên dạy
@login_required(login_url='dang-nhap')
def phan_cong_giao_vien(request, giao_vien_id):
    """
    Phân công giáo viên dạy 

    Input: request, giao_vien_id

    Ghi chú: chỉ có quản trị viên mới có quyền phân công giáo viên

    Trả về: 
        - Danh sách lớp học năm học đó chưa được phân công dạy môn đó
        - Danh sách lớp học đã được phân công và tên giáo viên đã được phân công
        - Nếu phân công giáo viên thành công thì trả về trang phân công cho giáo viên đó
    """
    giao_vien = GiaoVien.objects.get(id=giao_vien_id)
    mon_hoc = giao_vien.mon_day
    mon_hoc_list = MonHoc.objects.all()
    nam_hoc_list = NamHoc.objects.all()
    current_nam_hoc = request.GET.get('nam_hoc')
    lop_hoc_list = LopHoc.objects.exclude(id__in=giao_vien.lop_day.values('id'))
    if current_nam_hoc:
        try:
            nam_hoc_obj = NamHoc.objects.get(nam=current_nam_hoc)
            lop_hoc_list = lop_hoc_list.filter(nam_hoc=nam_hoc_obj)
        except NamHoc.DoesNotExist:
            lop_hoc_list = []

    lop_da_phan_cong_giao_vien_khac = []
    if giao_vien.mon_day:
        lop_da_phan_cong_giao_vien_khac = lop_hoc_list.filter(
            giaovien__mon_day=giao_vien.mon_day
        ).distinct()

        lop_hoc_list = lop_hoc_list.exclude(id__in=lop_da_phan_cong_giao_vien_khac.values('id'))

    lop_da_phan_cong_giao_vien_hien_tai = giao_vien.lop_day.all()
    if current_nam_hoc:
        lop_da_phan_cong_giao_vien_hien_tai = lop_da_phan_cong_giao_vien_hien_tai.filter(nam_hoc__nam=current_nam_hoc)

    if request.method == 'POST':
        selected_lop_hoc = request.POST.getlist('lop_hoc')  
        if selected_lop_hoc:
            giao_vien.lop_day.add(*LopHoc.objects.filter(id__in=selected_lop_hoc))  
            messages.success(request, 'Thêm lớp học vào phân công thành công!')
        else:
            messages.warning(request, 'Bạn chưa chọn lớp học nào để phân công.')

        return redirect('phan-cong-gv', giao_vien_id=giao_vien.id)

    return render(request, 'school_app/phan_cong_gv.html', {
        'giao_vien': giao_vien,
        'lop_hoc_list': lop_hoc_list,
        'lop_da_phan_cong_giao_vien_khac': lop_da_phan_cong_giao_vien_khac,
        'lop_da_phan_cong_giao_vien_hien_tai': lop_da_phan_cong_giao_vien_hien_tai,
        'mon_hoc_list': mon_hoc_list,
        'nam_hoc_list': nam_hoc_list,
        'current_nam_hoc': current_nam_hoc,
        'mon_hoc': mon_hoc
    })


# Hủy phân công giáo viên dạy
@login_required(login_url='dang-nhap')
def huy_phan_cong(request, giao_vien_id, lop_hoc_id):
    """
    Cập nhật giáo viên

    Input: request, giao_vien_id, lop_hoc_id

    Ghi chú: chỉ có quản trị viên mới có quyền hủy phân công giáo viên dạy

    Trả về: 
        - Danh sách lớp học năm học đó chưa được phân công dạy môn đó
        - Danh sách lớp học đã được phân công và tên giáo viên đã được phân công
        - Danh sách lớp học giáo viên đó đã được phân công sau khi hủy
    """
    giao_vien = get_object_or_404(GiaoVien, id=giao_vien_id)
    lop_hoc = get_object_or_404(LopHoc, id=lop_hoc_id)

    giao_vien.lop_day.remove(lop_hoc)
    
    messages.success(request, f'Đã hủy phân công lớp {lop_hoc.ma_lop} cho giáo viên {giao_vien.nguoi_dung.ho_ten}.')

    return redirect('phan-cong-gv', giao_vien_id=giao_vien.id)



@login_required(login_url='dang-nhap')
def tong_ket(request):
    """
    Trang tổng kết: trang thể hiện những kết quả của từng năm học, 
    bao gồm biểu đồ so sánh điểm trung bình tổng các lớp cả năm hoặc theo từng môn

    Input: request

    Trả về: Trang tổng kết, cùng các dữ liệu lable và data_point để vẽ biểu đồ
    """
    nam_hocs = NamHoc.objects.all()
    mon_hocs = MonHoc.objects.all()

    nam_hoc_id = request.GET.get('nam_hoc_id')
    mon_hoc_id = request.GET.get('mon_hoc_id')

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

    lop_hocs = LopHoc.objects.filter(nam_hoc_id=nam_hoc_id)

    lop_data = []
    for lop in lop_hocs:
        if mon_hoc_id:
            diem_tb = KetQuaMonHoc.objects.filter(
                hoc_sinh__lop_hoc=lop,
                nam_hoc_id=nam_hoc_id,
                mon_hoc_id=mon_hoc_id
            ).aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']
        else:
            diem_tb = KetQuaMonHoc.objects.filter(
                hoc_sinh__lop_hoc=lop,
                nam_hoc_id=nam_hoc_id
            ).aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']

        lop_data.append({
            'ma_lop': lop.ma_lop,
            'diem_tb': round(diem_tb, 2) if diem_tb else 0
        })

    lop_data = sorted(lop_data, key=lambda x: x['ma_lop'])

    labels = [lop['ma_lop'] for lop in lop_data]
    data_points = [lop['diem_tb'] for lop in lop_data]

    context = {
        'nam_hocs': nam_hocs,
        'mon_hocs': mon_hocs,
        'lop_data': lop_data,
        'labels': labels,  
        'data_points': data_points,  
        'selected_nam_hoc': int(nam_hoc_id) if nam_hoc_id else None,
        'selected_mon_hoc': int(mon_hoc_id) if mon_hoc_id else None,
    }

    return render(request, 'school_app/tong_ket.html', context)



@login_required(login_url='dang-nhap')
def danh_sach_kq_hoc_sinh(request, nam_hoc_id, status):
    """
        Trang danh sách kết quả học sinh

        Input: request, nam_hoc_id, status

        Trả về: Danh sách học sinh theo học lực
    """
    ket_qua = KetQuaNamHoc.objects.filter(nam_hoc_id=nam_hoc_id)
    print(ket_qua)
    if status == 'gioi':
        ket_qua = ket_qua.filter(diem_tong_ket__gte=8.0, hanh_kiem='Tot')  

    elif status == 'kha':
        ket_qua = ket_qua.filter(
            diem_tong_ket__gte=7.0, diem_tong_ket__lt=8.0, hanh_kiem__in=['Tot', 'Kha']
        )

    elif status == 'trung_binh':
        ket_qua = ket_qua.filter(
            diem_tong_ket__gte=5.0, diem_tong_ket__lt=7.0, hanh_kiem__in=['Tot', 'Kha']
        )

    elif status == 'khong_dat':
        ket_qua = ket_qua.filter(
            Q(diem_tong_ket__lt=5.0) | Q(hanh_kiem='Yeu')
        )

    else:
        ket_qua = KetQuaNamHoc.objects.none()
        
    hoc_sinh_list = []
    for kq in ket_qua:
        hoc_sinh = kq.hoc_sinh
        lop_hoc = hoc_sinh.lop_hoc.filter(nam_hoc_id=nam_hoc_id).first()
        ma_lop = lop_hoc.ma_lop if lop_hoc else None
        hoc_sinh_list.append({
            'ho_ten': hoc_sinh.nguoi_dung.ho_ten,
            'ma_lop': ma_lop,
            'nam_hoc': kq.nam_hoc.nam,
            'diem_tong_ket': kq.diem_tong_ket,
            'ket_qua': kq.ket_qua,
            'hanh_kiem': kq.hanh_kiem
        })

    return render(request, 'school_app/ds_kq_hoc_sinh.html', {
        'hoc_sinh_list': hoc_sinh_list,
        'status': status,
        'nam_hoc_id': nam_hoc_id,
    })




@login_required(login_url='dang-nhap')
def ket_qua_hoc_tap(request):
    """
        Kết quả học sinh 

        Input: request

        Trả về: Chuyển hướng tới trang kết quả học sinh được lọc theo năm học, học kỳ
    """
    try:
        hoc_sinh = HocSinh.objects.get(nguoi_dung=request.user)
    except HocSinh.DoesNotExist:
        return render(request, 'school_app/404.html', {'message': 'Học sinh không tồn tại'})

    selected_nam_hoc = request.GET.get('nam_hoc', None)
    selected_hoc_ki = request.GET.get('hoc_ki', None)

    if selected_nam_hoc:
        try:
            nam_hoc = NamHoc.objects.get(nam=selected_nam_hoc)
        except NamHoc.DoesNotExist:
            nam_hoc = None
    else:
        nam_hoc = None
    lop_hoc = None

    if nam_hoc:
        lop_hoc = hoc_sinh.lop_hoc.filter(nam_hoc=nam_hoc).first()  

    ket_qua_hoc_ky = None
    ket_qua_mon_hoc = None
    ket_qua_nam_hoc = None

    if nam_hoc:
        if selected_hoc_ki:  
            ket_qua_hoc_ky = KetQua.objects.filter(
                hoc_sinh=hoc_sinh,
                nam_hoc=nam_hoc,
                hoc_ki=selected_hoc_ki
            )
        else:
            ket_qua_mon_hoc = KetQuaMonHoc.objects.filter(
                hoc_sinh=hoc_sinh,
                nam_hoc=nam_hoc
            )

            try:
                ket_qua_nam_hoc = KetQuaNamHoc.objects.get(
                    hoc_sinh=hoc_sinh,
                    nam_hoc=nam_hoc
                )
            except KetQuaNamHoc.DoesNotExist:
                ket_qua_nam_hoc = None

    danh_sach_nam_hoc = hoc_sinh.lop_hoc.values_list('nam_hoc__nam', flat=True).distinct()

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





@login_required(login_url='dang-nhap')
def quan_ly_diem(request):
    """
        Trang quản lý điểm dành cho giáo viên bộ môn

        Input: request

        Trả về: Danh sách điểm lọc theo năm học, lớp học, học kỳ

        Ghi chú: Danh sách chỉ hiện điểm môn mà giáo viên đó dạy, lớp giáo viên đó dạy
    """
    try:
        giao_vien = GiaoVien.objects.get(nguoi_dung=request.user)
    except GiaoVien.DoesNotExist:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")

    selected_nam_hoc = request.GET.get('nam_hoc', None)
    selected_hoc_ki = request.GET.get('hoc_ki', None)
    selected_lop_hoc = request.GET.get('lop_hoc', None)

    nam_hoc_list = NamHoc.objects.all()
    mon_hoc_list = MonHoc.objects.filter(giaovien=giao_vien)
    lop_hoc_list = giao_vien.lop_day.all()
    ket_qua_list = KetQua.objects.none()
    if selected_nam_hoc:
        lop_hoc_list = lop_hoc_list.filter(nam_hoc__nam=selected_nam_hoc)

        ket_qua_list = KetQua.objects.filter(
            mon_hoc__in=mon_hoc_list, 
            hoc_sinh__lop_hoc__in=lop_hoc_list 
        )

    if selected_nam_hoc:
        ket_qua_list = ket_qua_list.filter(nam_hoc__nam=selected_nam_hoc)
    if selected_hoc_ki:
        ket_qua_list = ket_qua_list.filter(hoc_ki=selected_hoc_ki)
    if selected_lop_hoc:
        ket_qua_list = ket_qua_list.filter(hoc_sinh__lop_hoc__ma_lop=selected_lop_hoc)

    context = {
        'nam_hoc_list': nam_hoc_list,
        'lop_hoc_list': lop_hoc_list,
        'ket_qua_list': ket_qua_list,
        'selected_nam_hoc': selected_nam_hoc,
        'selected_hoc_ki': selected_hoc_ki,
        'selected_lop_hoc': selected_lop_hoc,
        'mon_hoc_list': mon_hoc_list,
        'mon_hoc': giao_vien.mon_day.ten_mon
    }

    return render(request, 'school_app/diem_giao_vien.html', context)


@login_required(login_url='dang-nhap')
def cap_nhat_diem_gv(request, diem_id):
    """
        Cập nhật điểm dành cho giáo viên bộ môn

        Input: request, diem_id

        Trả về: Danh sách điểm sau khi cập nhật

        Ghi chú: Danh sách chỉ hiện điểm môn mà giáo viên đó dạy, lớp giáo viên đó dạy
    """
    ket_qua = get_object_or_404(KetQua, id=diem_id)
    lop_hoc = ket_qua.hoc_sinh.lop_hoc.first()
    if lop_hoc:
        ma_lop = lop_hoc.ma_lop
        print(ma_lop)
    nam_hoc = ket_qua.nam_hoc.nam 
    hoc_ki = ket_qua.hoc_ki
    if request.method == 'POST':
        form = KetQuaForm(request.POST, instance=ket_qua)
        if form.is_valid():
            form.save()  
            return redirect(f'/quan-ly-diem?nam_hoc={nam_hoc}&lop_hoc={ma_lop}&hoc_ki={hoc_ki}')  
    else:
        form = KetQuaForm(instance=ket_qua)  

    return render(request, 'school_app/cap_nhat_diem_gv.html', {'form': form, 'ket_qua': ket_qua})


@login_required(login_url='dang-nhap')
def lop_chu_nhiem(request):
    """
        Trang lớp chủ nhiệm hiển thị danh sách học sinh lớp mà giáo viên đó chủ nhiệm

        Input: request

        Trả về: Danh sách các lớp mà giáo viên đó chủ nhiệm qua các năm
    """
    giao_vien = get_object_or_404(GiaoVien, nguoi_dung=request.user)

    nam_hoc_list = NamHoc.objects.all()

    nam_hoc_id = request.GET.get('nam_hoc')
    print(nam_hoc_id)
    lop_chu_nhiem = LopHoc.objects.filter(giao_vien_chu_nhiem=giao_vien)
    nam_hoc = lop_chu_nhiem.first().nam_hoc
    if nam_hoc_id:
        lop_chu_nhiem = lop_chu_nhiem.filter(nam_hoc_id=nam_hoc_id)

    if lop_chu_nhiem.exists():
        hoc_sinh_list = HocSinh.objects.filter(lop_hoc__in=lop_chu_nhiem).distinct()
        print(hoc_sinh_list)
        for hs in hoc_sinh_list:
            ket_qua = KetQuaNamHoc.objects.filter(hoc_sinh=hs, nam_hoc=nam_hoc).first()
            hs.hanh_kiem = ket_qua.hanh_kiem if ket_qua else None
    else:
        hoc_sinh_list = []

    return render(request, 'school_app/lop_chu_nhiem.html', {
        'nam_hoc_list': nam_hoc_list,
        'hoc_sinh_list': hoc_sinh_list,
        'lop': lop_chu_nhiem.first() if lop_chu_nhiem.exists() else None
    })

@login_required(login_url='dang-nhap')
def xem_ket_qua_lop(request, lop_id):
    """
        Xem kết quả học tập của lớp mà giáo viên đó chủ nhiệm

        Input: request, lop_id

        Trả về: Danh sách điểm của các học sinh lọc theo từng môn
    """
    # Lấy tham số lọc từ query string (mặc định để trống)
    hoc_ky = request.GET.get('hoc_ky', '1')  # Học kỳ mặc định là '1'
    mon_hoc_id = request.GET.get('mon_hoc', None)  # Mặc định không chọn môn học

    # Truy xuất thông tin lớp học
    lop_hoc = LopHoc.objects.get(id=lop_id)
    hoc_sinh_list = HocSinh.objects.filter(lop_hoc=lop_hoc)

    # Truy xuất danh sách môn học và năm học
    danh_sach_mon_hoc = MonHoc.objects.all()
    nam_hoc = lop_hoc.nam_hoc

    # Kết quả lớp học
    ket_qua_lop = []
    if mon_hoc_id:  # Chỉ lọc khi có chọn môn học
        mon_hoc = MonHoc.objects.get(id=mon_hoc_id)
        for hoc_sinh in hoc_sinh_list:
            ket_qua = KetQua.objects.filter(
                hoc_sinh=hoc_sinh, 
                nam_hoc=nam_hoc, 
                hoc_ki=hoc_ky,
                mon_hoc=mon_hoc
            ).first()
            ket_qua_lop.append({
                'ho_ten': hoc_sinh.nguoi_dung.ho_ten,
                'diem_15phut': ket_qua.diem_15phut if ket_qua else None,
                'diem_1tiet': ket_qua.diem_1tiet if ket_qua else None,
                'diem_gk': ket_qua.diem_gk if ket_qua else None,
                'diem_ck': ket_qua.diem_ck if ket_qua else None,
                'diem_tong': ket_qua.diem_tong if ket_qua else None,
            })

    context = {
        'lop_hoc': lop_hoc,
        'ket_qua_lop': ket_qua_lop,
        'hoc_ky': hoc_ky,
        'danh_sach_mon_hoc': danh_sach_mon_hoc,
        'mon_hoc_id': int(mon_hoc_id) if mon_hoc_id else None,
    }
    return render(request, 'school_app/ket_qua_lop.html', context)