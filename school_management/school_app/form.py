from django import forms
from .models import GiaoVien, KetQua, MonHoc, NamHoc, NguoiDung, HocSinh, LopHoc


class NguoiDungForm(forms.ModelForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'id': "username_user",
            'class': "form-control",
            'placeholder': 'Username...'
        })
    )

    ho_ten = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'id': "name_user",
            'class': "form-control",
            'placeholder': 'Họ tên...'
        })
    )

    password = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={
            'id': "password",
            'class': "form-control",
            'placeholder': 'Mật khẩu...'
        })
    )

    ngay_sinh = forms.DateField(
        label="",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'id': "datepicker",
            'class': 'form-control'
        })
    )

    gioi_tinh = forms.ChoiceField(
        label="",
        choices=NguoiDung.GIOI_TINH,  # GIOI_TINH là tuple chứa các lựa chọn giới tính
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'sex_user'
        })
    )

    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'id': 'email_user',
            'class': 'form-control',
            'placeholder': 'Email...'
        })
    )

    dia_chi = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            'class': 'form-control',
            'id': 'address_user',
            'placeholder': "Địa chỉ"
        })
    )

    class Meta:
        model = NguoiDung
        fields = ['username', 'password', 'ho_ten', 'ngay_sinh', 'gioi_tinh', 'email', 'dia_chi']


class CapNhatNguoiDungForm(forms.ModelForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'id': "username_user",
            'class': "form-control",
        })
    )

    ho_ten = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'id': "name_user",
            'class': "form-control",
        })
    )

    ngay_sinh = forms.DateField(
        label="",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'id': "datepicker",
            'class': 'form-control'
        })
    )

    gioi_tinh = forms.ChoiceField(
        label="",
        choices=NguoiDung.GIOI_TINH,  # GIOI_TINH là tuple chứa các lựa chọn giới tính
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'sex_user'
        })
    )

    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'id': 'email_user',
            'class': 'form-control',
        })
    )

    dia_chi = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            'class': 'form-control',
            'id': 'address_user',
        })
    )

    class Meta:
        model = NguoiDung
        fields = ['username', 'ho_ten', 'ngay_sinh', 'gioi_tinh', 'email', 'dia_chi']


class HocSinhForm(NguoiDungForm):  # Kế thừa từ NguoiDungForm
    lop_hoc = forms.ModelMultipleChoiceField(
        queryset=LopHoc.objects.all(),  # Giả sử LopHoc là model chứa danh sách các lớp học
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False  # Không bắt buộc
    )

    class Meta:
        model = HocSinh
        fields = NguoiDungForm.Meta.fields + ['lop_hoc']

    def __init__(self, *args, **kwargs):
        super(HocSinhForm, self).__init__(*args, **kwargs)
        # if self.instance and self.instance.nguoi_dung:
        #     self.fields.pop('password')  # Loại bỏ trường password
        self.fields['lop_hoc'].required = False  # Đảm bảo trường 'lop_hoc' không bắt buộc

    def save(self, commit=True):
        # Lưu đối tượng NguoiDung trước
        nguoi_dung = super().save(commit=False)
        if commit:
            nguoi_dung.save()

        # Tạo hoặc lấy đối tượng HocSinh dựa trên NguoiDung
        hoc_sinh, created = HocSinh.objects.get_or_create(nguoi_dung=nguoi_dung)

        # Gán danh sách lớp học cho học sinh nếu có
        if self.cleaned_data.get('lop_hoc'):
            hoc_sinh.lop_hoc.set(self.cleaned_data['lop_hoc'])

        if commit:
            hoc_sinh.save()

        return hoc_sinh



# class LopHocForm(forms.ModelForm):
#     class Meta:
#         model = LopHoc
#         fields = ['ma_lop', 'so_hoc_sinh', 'nam_hoc']  # Các trường cần nhập vào form

#     # Tùy chỉnh widget cho trường 'nam_hoc' nếu cần thiết (thêm select box)
#     nam_hoc = forms.ModelChoiceField(
#         queryset=NamHoc.objects.all(), 
#         empty_label="Chọn năm học", 
#         required=True  # Mặc định sẽ yêu cầu chọn năm học
#     )
    
#     # Làm cho trường 'so_hoc_sinh' không bắt buộc
#     so_hoc_sinh = forms.IntegerField(
#         required=False,  # Không bắt buộc
#         widget=forms.NumberInput(attrs={'placeholder': 'Số học sinh'}),
#     )


class LopHocForm(forms.ModelForm):
    class Meta:
        model = LopHoc
        fields = ['ma_lop', 'so_hoc_sinh', 'nam_hoc', 'giao_vien_chu_nhiem']  # Thêm 'giao_vien_chu_nhiem'

    # Tùy chỉnh widget cho trường 'nam_hoc' để hiển thị dưới dạng chọn năm học
    nam_hoc = forms.ModelChoiceField(
        queryset=NamHoc.objects.all(),
        empty_label="Chọn năm học", 
        required=True  # Yêu cầu chọn năm học
    )

    # Làm cho trường 'so_hoc_sinh' không bắt buộc
    so_hoc_sinh = forms.IntegerField(
        required=False,  # Trường này không bắt buộc
        widget=forms.NumberInput(attrs={'placeholder': 'Số học sinh'}),  # Placeholder cho trường này
    )

    # Thêm trường 'giao_vien_chu_nhiem' để chọn giáo viên chủ nhiệm
    giao_vien_chu_nhiem = forms.ModelChoiceField(
        queryset=GiaoVien.objects.all(),  # Lấy tất cả giáo viên từ cơ sở dữ liệu
        required=False,  # Trường này không bắt buộc
        empty_label="Chọn giáo viên chủ nhiệm",  # Lựa chọn mặc định
    )

class MonHocForm(forms.ModelForm):
    class Meta:
        model = MonHoc
        fields = ['ma_mon', 'ten_mon', 'diem_chuan']  # Các trường trong form


    # Làm cho 'diem_chuan' có các thuộc tính thêm
    diem_chuan = forms.FloatField(
        required=True,  # Bắt buộc nhập
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Điểm chuẩn',
            'min': 0,  # Điểm chuẩn không được âm
        })
    )

    # Tùy chỉnh các trường khác
    ma_mon = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mã môn học',
        })
    )

    ten_mon = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên môn học',
        })
    )



class KetQuaForm(forms.ModelForm):
    class Meta:
        model = KetQua
        fields = [ 'diem_15phut', 'diem_1tiet', 'diem_gk', 'diem_ck']
        widgets = {
            'diem_15phut': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'diem_1tiet': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'diem_gk': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'diem_ck': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
        }
    
    def clean_diem_15phut(self):
        diem = self.cleaned_data.get('diem_15phut')
        if diem is not None and (diem < 0 or diem > 10):
            raise forms.ValidationError("Điểm 15 phút phải nằm trong khoảng từ 0 đến 10.")
        return diem
    
    def clean_diem_1tiet(self):
        diem = self.cleaned_data.get('diem_1tiet')
        if diem is not None and (diem < 0 or diem > 10):
            raise forms.ValidationError("Điểm 1 tiết phải nằm trong khoảng từ 0 đến 10.")
        return diem
    
    def clean_diem_gk(self):
        diem = self.cleaned_data.get('diem_gk')
        if diem is not None and (diem < 0 or diem > 10):
            raise forms.ValidationError("Điểm giữa kỳ phải nằm trong khoảng từ 0 đến 10.")
        return diem
    
    def clean_diem_ck(self):
        diem = self.cleaned_data.get('diem_ck')
        if diem is not None and (diem < 0 or diem > 10):
            raise forms.ValidationError("Điểm cuối kỳ phải nằm trong khoảng từ 0 đến 10.")
        return diem



class GiaoVienForm(NguoiDungForm):  # Kế thừa từ NguoiDungForm
    # Trường cho môn dạy
    mon_day = forms.ModelChoiceField(
        queryset=MonHoc.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True  # Môn dạy bắt buộc
    )

    # Trường cho các lớp mà giáo viên dạy (nhiều lớp)
    lop_day = forms.ModelMultipleChoiceField(
        queryset=LopHoc.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        required=False  # Không bắt buộc
    )

    class Meta:
        model = GiaoVien
        fields = NguoiDungForm.Meta.fields + ['mon_day', 'lop_day']

    def __init__(self, *args, **kwargs):
        super(GiaoVienForm, self).__init__(*args, **kwargs)
        # Đảm bảo các trường 'mon_day' bắt buộc và 'lop_day' không bắt buộc
        self.fields['mon_day'].required = False
        self.fields['lop_day'].required = False  # Không bắt buộc chọn lớp

    def save(self, commit=True):
        # Lưu đối tượng NguoiDung trước
        nguoi_dung = super().save(commit=False)
        if commit:
            nguoi_dung.save()

        # Tạo hoặc lấy đối tượng GiaoVien dựa trên NguoiDung
        giao_vien, created = GiaoVien.objects.get_or_create(nguoi_dung=nguoi_dung)

        # Gán môn học và các lớp dạy cho giáo viên
        if self.cleaned_data.get('mon_day'):
            giao_vien.mon_day = self.cleaned_data['mon_day']
        
        if self.cleaned_data.get('lop_day'):
            giao_vien.lop_day.set(self.cleaned_data['lop_day'])  # Gán nhiều lớp học nếu có

        if commit:
            giao_vien.save()

        return giao_vien
