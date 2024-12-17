from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser
from django.contrib.auth.hashers import make_password
from datetime import datetime, date
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_migrate

# Custom User Manager
class NguoiDungManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        """
        Hàm tạo đối tượng người dùng

        Input:
            - username (str): Tên đăng nhập của người dùng.
            - password (str): Mật khẩu của người dùng.
            - **extra_fields (dict): Các trường bổ sung như quyền hạn hoặc thông tin người dùng.

        Output:
            - Trả về một đối tượng `NguoiDung` sau khi đã lưu vào cơ sở dữ liệu.
        """
        user = NguoiDung(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, username, password, **extra_fields):
        """
        Phương thức tạo một đối tượng người dùng.

        Input:
            - username (str): Tên đăng nhập của người dùng.
            - password (str): Mật khẩu của người dùng.
            - **extra_fields (dict): Các trường bổ sung như quyền hạn hoặc thông tin người dùng.

        Output:
            - Trả về một đối tượng `NguoiDung` sau khi đã lưu vào cơ sở dữ liệu.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """
        Tạo một tài khoản quản trị viên với đầy đủ quyền hạn.

        Input:
            - username (str): Tên đăng nhập của quản trị viên.
            - password (str): Mật khẩu của quản trị viên.
            - **extra_fields (dict): Các trường bổ sung cho tài khoản quản trị viên.

        Output:
            - Trả về một đối tượng `NguoiDung` với quyền `is_staff=True` và `is_superuser=True`.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(username, password, **extra_fields)


# Mô hình người dùng
class NguoiDung(AbstractUser):
    """
    Lớp người dùng tùy chỉnh mở rộng từ AbstractUser trong Django.

    Mô hình này đại diện cho các loại người dùng như quản trị viên, giáo viên và học sinh. 

    Các trường:
    - LOAI_NGUOI_DUNG (tuple): Danh sách các vai trò người dùng
    - GIOI_TINH (list): Danh sách lựa chọn giới tính
    - username (CharField): Tên đăng nhập của người dùng, duy nhất.
    - vai_tro (CharField): Vai trò của người dùng
    - is_active (BooleanField): Trạng thái kích hoạt của tài khoản
    - is_staff (BooleanField): Xác định quyền nhân viên (staff)
    - is_superuser (BooleanField): Xác định quyền quản trị viên
    - ho_ten (CharField): Họ và tên 
    - ngay_sinh (DateField): Ngày sinh của người dùng
    - gioi_tinh (CharField): Giới tính của người dùng
    - so_dien_thoai (CharField): Số điện thoại liên hệ
    - email (EmailField): Địa chỉ email của người dùng, duy nhất.
    - dia_chi (TextField): Địa chỉ của người dùng

    Thuộc tính đặc biệt:
        - USERNAME_FIELD (str): Trường sử dụng để đăng nhập (username).
        - REQUIRED_FIELDS (list): Danh sách các trường bắt buộc khi tạo superuser (email là duy nhất nhưng không bắt buộc).
        - objects (NguoiDungManager): Trình quản lý người dùng tùy chỉnh.

    Ràng buộc:
        - `unique_user`: Đảm bảo tính duy nhất của cặp `username` và `email`.
    """
    LOAI_NGUOI_DUNG = (('1', "Quản trị viên"), ('2', "Giáo viên"), ('3', "Học sinh"))
    GIOI_TINH = [("1", "Nam"), ("0", "Nữ")]

    username = models.CharField(max_length=200, unique=True)
    vai_tro = models.CharField(default='1', choices=LOAI_NGUOI_DUNG, max_length=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    ho_ten = models.CharField(default='', max_length=200)
    ngay_sinh = models.DateField(default=date.today)
    gioi_tinh = models.CharField(default='1', choices=GIOI_TINH, max_length=1)
    so_dien_thoai = models.CharField(default='', max_length=20, blank=True)
    email = models.EmailField(max_length=200, unique=True)
    dia_chi = models.TextField(default='', blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = NguoiDungManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name="unique_user")
        ]

    def __str__(self):
        """
        Hàm trả về họ tên của người dùng.

        Kết quả:
            - str: Họ và tên đầy đủ của người dùng.
        """
        return self.ho_ten


# Mô hình tuổi học sinh
class NamHoc(models.Model):
    """
    Lớp Năm Học thể hiện năm học

    Các trường:
    - nam: năm học chuỗi có dạng xxxx-yyyy
    - tuoi_toi_da : tuổi tối đa của học sinh tham gia học
    - tuoi_toi_thieu: tuổi tối thiểu của học sinh tham gia học
    """
    nam = models.CharField(max_length=200, unique=True)
    tuoi_toi_da = models.IntegerField(null=False)
    tuoi_toi_thieu = models.IntegerField(null=False)

    def __str__(self):
        """
        Hàm trả về chuỗi biểu diễn đối tượng

        Trả về: năm học
        """
        return self.nam


@receiver(post_migrate)
def create_default_nam_hoc(sender, **kwargs):
    """
    Hàm nhận tạo năm học tự động khi migrate chương trình
    """
    current_year = datetime.now().year
    for year in range(2021, current_year + 1):
        nam_hoc = f"{year}-{year + 1}"
        if not NamHoc.objects.filter(nam=nam_hoc).exists():
            NamHoc.objects.create(nam=nam_hoc, tuoi_toi_da=20, tuoi_toi_thieu=14)

# Lớp học
class LopHoc(models.Model):
    """
    Lớp LopHoc thể hiện các lớp của các năm học khác nhau

    Các trường: 
    - ma_lop: mã lớp 
    - so_hoc_sinh: số học sinh tối đa của lớp
    - nam_hoc: năm học là khóa khóa ngoại tham chiếu tới lớp NamHoc
    - giao_vien_chu_nhiem: giáo viên chủ nhiệm là khóa ngoại tham chiếu tới GiaoVien
    """
    ma_lop = models.CharField(max_length=10, null=False, unique=False)
    so_hoc_sinh = models.IntegerField(null=True)
    nam_hoc = models.ForeignKey(
        NamHoc, null=False, on_delete=models.CASCADE)
    giao_vien_chu_nhiem = models.ForeignKey("GiaoVien", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        """
        Hàm biểu diễn đối tượng dưới dạng string

        Trả về: chuỗi kết hợp năm học và lớp học
        """
        return self.nam_hoc.nam + '_' + self.ma_lop


# Môn học
class MonHoc(models.Model):
    """
    Lớp MonHoc thể hiện các môn học của trường 

    Các trường:
    - ma_mon: mã môn học mỗi môn là duy nhất
    - ten_mon: tên môn học mỗi môn là duy nhất
    - diem_chuan: điểm để vượt qua môn học đó 
    """
    ma_mon = models.CharField(max_length=200, null=False, unique=True, blank=True)
    ten_mon = models.CharField(max_length=200, null=False, unique=True, blank=True)
    diem_chuan = models.FloatField(null=False)

    def __str__(self):
        """
        Hàm biểu diễn môn học dưới dạng string

        Trả về: chuỗi tên môn học
        """
        return self.ten_mon


# Quản trị viên
class QuanTriVien(models.Model):
    """
    Lớp QuanTriVien là lớp đại diện cho người dùng có quyền cao nhất

    Các trường:
    - nguoi_dung: có mối quan hệ 1 1 với NguoiDung
    """
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE)

    def __str__(self):
        """
        Hàm biểu diễn quản trị viên dưới dạng string

        Trả về: chuỗi tên quản trị viên
        """
        return self.nguoi_dung.username


# Học sinh
class HocSinh(models.Model):
    """
    Lớp HocSinh là lớp đại diện cho học sinh

    Các trường:
    - nguoi_dung: có mối quan hệ 1 1 với NguoiDung
    - lop_hoc: lớp học của học sinh có mối quan hệ nhiều nhiều
    """
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE)
    lop_hoc = models.ManyToManyField(LopHoc, blank=True)

    def __str__(self):
        """
        Hàm biểu diễn học sinh dưới dạng string

        Trả về: chuỗi tên học sinh
        """
        return self.nguoi_dung.username


# Giáo viên
class GiaoVien(models.Model):
    """
    Lớp GiaoVien là lớp đại diện cho giáo viên

    Các trường:
    - nguoi_dung: có mối quan hệ 1 1 với NguoiDung
    - mon_day: môn học là chuyên môn của giáo viên
    - lop_day: lớp học mà giáo viên đó dạy, có mối quan hệ nhiều nhiều
    """
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE)
    mon_day = models.ForeignKey(MonHoc, blank=True, on_delete=models.CASCADE)
    lop_day = models.ManyToManyField(LopHoc, blank=True)
    def __str__(self):
        """
            Hàm biểu diễn giáo viên dưới dạng string

            Trả về: chuỗi tên giáo viên
        """
        return f'{self.nguoi_dung.ho_ten}({self.nguoi_dung.username})'


# Bảng kết quả
class KetQua(models.Model):
    """
    Mô hình KetQua lưu kết quả học tập của học sinh trong một môn học cụ thể.

    Các trường:
    - HOC_KI (tuple): Danh sách các lựa chọn học kỳ.
    - hoc_sinh (ForeignKey): Tham chiếu đến HocSinh
    - mon_hoc (ForeignKey): Tham chiếu đến MonHoc
    - nam_hoc (ForeignKey): Tham chiếu đến NamHoc
    - hoc_ki (CharField): Học kỳ hiện tại, có giá trị trong HOC_KI.
    - diem_15phut (FloatField): Điểm kiểm tra 15 phút 
    - diem_1tiet (FloatField): Điểm kiểm tra 1 tiết 
    - diem_gk (FloatField): Điểm giữa kỳ 
    - diem_ck (FloatField): Điểm cuối kỳ 
    - diem_tong (FloatField): Điểm tổng kết của môn học (được tính tự động).
    """
    HOC_KI = (
        ('1', "Học kỳ 1"),
        ('2', "Học kỳ 2")
    )
    hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE)
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
    nam_hoc = models.ForeignKey(NamHoc, null=False, on_delete=models.CASCADE)
    hoc_ki = models.CharField(max_length=200, null=False, choices=HOC_KI)
    diem_15phut = models.FloatField(null=True, blank=True)
    diem_1tiet = models.FloatField(null=True, blank=True)
    diem_gk = models.FloatField(null=True, blank=True)
    diem_ck = models.FloatField(null=True, blank=True)
    diem_tong = models.FloatField(null=True, blank=True)

    def __str__(self):
        """
        hàm trả về chuỗi đại diện cho đối tượng KetQua.

        Trả về:
            - str: Chuỗi có định dạng tên "học sinh - học kỳ".
        """
        return f"{self.hoc_sinh.nguoi_dung.username}_{self.hoc_ki}"

    def tinh_diem_tong(self):
        """Tính điểm tổng của học sinh trong một môn học theo công thức."""
        self.diem_tong = round(self.diem_15phut * 0.1 + self.diem_1tiet * 0.2 +
                                self.diem_gk * 0.3 + self.diem_ck * 0.4, 2)

    def save(self, *args, **kwargs):
        """Override method save() để tự động tính điểm tổng trước khi lưu"""
        self.tinh_diem_tong()
        super().save(*args, **kwargs)
        
        # Sau khi lưu KetQua, cập nhật điểm tổng trong KetQuaMonHoc
        self.update_ket_qua_mon_hoc()

    def update_ket_qua_mon_hoc(self):
        """Cập nhật điểm tổng kết trong KetQuaMonHoc sau khi thay đổi điểm trong KetQua."""
        # Tìm đối tượng KetQuaMonHoc tương ứng
        ket_qua_mon_hoc = KetQuaMonHoc.objects.filter(
            hoc_sinh=self.hoc_sinh,
            mon_hoc=self.mon_hoc,
            nam_hoc=self.nam_hoc
        ).first()

        if ket_qua_mon_hoc:
            # Cập nhật điểm tổng kết trong KetQuaMonHoc
            ket_qua_mon_hoc.save()


class KetQuaMonHoc(models.Model):
    """
        Mô hình này lấy dữ liệu từ bảng KetQua để tính toán điểm tổng kết của học sinh dựa trên điểm tổng
    của học kỳ 1 và học kỳ 2.

    Các trường:
        - hoc_sinh (ForeignKey): Tham chiếu đến học sinh 
        - mon_hoc (ForeignKey): Tham chiếu đến môn học 
        - nam_hoc (ForeignKey): Tham chiếu đến năm học 
        - diem_tong_ket (FloatField): Điểm tổng kết của môn học 
    """
    hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE)
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
    nam_hoc = models.ForeignKey(NamHoc, on_delete=models.CASCADE)
    
    diem_tong_ket = models.FloatField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """
        Ghi đè phương thức save() để tính điểm tổng kết từ bảng KetQua trước khi lưu.

        Hành động:
            - Lấy điểm tổng kết của học kỳ 1 và học kỳ 2 từ mô hình KetQua.
            - Tính điểm tổng kết theo công thức:
                Điểm tổng kết = (Điểm HK1 + Điểm HK2 * 2) / 3
            - Lưu giá trị `diem_tong_ket` vào trường tương ứng.

        Input:
            - *args, **kwargs: Các tham số được truyền cho phương thức save() gốc.

        Kết quả:
            - Đối tượng KetQuaMonHoc được lưu vào cơ sở dữ liệu với điểm tổng kết đã tính.
        """
        diem_hk1 = KetQua.objects.filter(
            hoc_sinh=self.hoc_sinh,
            mon_hoc=self.mon_hoc,
            nam_hoc=self.nam_hoc,
            hoc_ki='1'
        ).first()  

        diem_hk2 = KetQua.objects.filter(
            hoc_sinh=self.hoc_sinh,
            mon_hoc=self.mon_hoc,
            nam_hoc=self.nam_hoc,
            hoc_ki='2'
        ).first() 

        if diem_hk1 and diem_hk2:
            self.diem_tong_ket = (diem_hk1.diem_tong + diem_hk2.diem_tong * 2) / 3
        super().save(*args, **kwargs)

    def __str__(self):

        """
        Trả về chuỗi đại diện cho đối tượng KetQuaMonHoc.

        Kết quả:
            - str: Chuỗi có định dạng "username - tên môn học - năm học".
        """
        return f"{self.hoc_sinh.nguoi_dung.username} - {self.mon_hoc.ten_mon} - {self.nam_hoc.nam}"



class KetQuaNamHoc(models.Model):
    """
    Mô hình KetQuaNamHoc lưu kết quả tổng kết của học sinh cho cả năm học.

    Các trường:
        - hoc_sinh: Tham chiếu đến học sinh (mô hình HocSinh).
        - nam_hoc: Tham chiếu đến năm học (mô hình NamHoc).
        - diem_tong_ket: Điểm tổng kết trung bình của học sinh trong năm học.
        - ket_qua: Kết quả đạt hay không đạt ('Dat' hoặc 'KhongDat').
        - hanh_kiem: Hạnh kiểm của học sinh trong năm học ('Tot', 'Kha', 'TrungBinh', 'Yeu'
    """
    HANH_KIEM_CHOICES = [
        ('Tot', 'Tốt'),
        ('Kha', 'Khá'),
        ('TrungBinh', 'Trung bình'),
        ('Yeu', 'Yếu'),
    ]

    hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE)
    nam_hoc = models.ForeignKey(NamHoc, on_delete=models.CASCADE)

    diem_tong_ket = models.FloatField(null=True, blank=True)
    ket_qua = models.CharField(
        max_length=10,
        choices=[('Dat', 'Đạt'), ('KhongDat', 'Không đạt')],
        null=True, blank=True
    )
    hanh_kiem = models.CharField(
        max_length=10,
        choices=HANH_KIEM_CHOICES,
        null=True, blank=True
    )

    def save(self, *args, **kwargs):
        """
        Ghi đè phương thức save() để tính điểm tổng kết và xét kết quả cho năm học.

        Hành động:
            - Lấy danh sách các môn học trong năm học từ bảng MonHoc.
            - Tính điểm tổng kết năm học dựa trên điểm tổng kết của từng môn học
              từ bảng KetQuaMonHoc.
            - Xét kết quả 'Dat' hay 'KhongDat' dựa vào:
                - Điểm tổng kết >= 5
                - Hạnh kiểm không phải là 'Yeu'
            - Gọi phương thức save() gốc để lưu đối tượng vào cơ sở dữ liệu.

        Input:
            - *args, **kwargs: Các tham số được truyền cho phương thức save() gốc.

        Ghi chú:
            - Nếu không có điểm tổng kết cho bất kỳ môn học nào, `diem_tong_ket` sẽ không thay đổi.
            - Kết quả sẽ là 'Dat' nếu đủ điều kiện về điểm số và hạnh kiểm, ngược lại là 'KhongDat'.
        """
        mon_hocs = MonHoc.objects.all()
        total_points = 0
        total_subjects = 0

        for mon_hoc in mon_hocs:
            ket_qua_mon_hoc = KetQuaMonHoc.objects.filter(
                hoc_sinh=self.hoc_sinh, mon_hoc=mon_hoc, nam_hoc=self.nam_hoc
            ).first()

            if ket_qua_mon_hoc and ket_qua_mon_hoc.diem_tong_ket is not None:
                total_points += ket_qua_mon_hoc.diem_tong_ket
                total_subjects += 1

        if total_subjects > 0:
            self.diem_tong_ket = total_points / total_subjects

        if self.diem_tong_ket is not None:
            if self.diem_tong_ket >= 5 and self.hanh_kiem != 'Yeu':
                self.ket_qua = 'Dat'
            else:
                self.ket_qua = 'KhongDat'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hoc_sinh.nguoi_dung.username} - {self.nam_hoc.nam} - {self.ket_qua}"




# Tạo profile người dùng dựa theo vai trò
# @receiver(post_save, sender=NguoiDung)
# def tao_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.vai_tro == '1':
#             QuanTriVien.objects.create(nguoi_dung=instance)
#         if instance.vai_tro == '2':
#             GiaoVien.objects.create(nguoi_dung=instance)
#         if instance.vai_tro == '3':
#             HocSinh.objects.create(nguoi_dung=instance)


# @receiver(post_save, sender=NguoiDung)
# def luu_profile(sender, instance, **kwargs):
#     if instance.vai_tro == '1':
#         instance.quantrivien.save()
#     if instance.vai_tro == '2':
#         instance.giaovien.save()
#     if instance.vai_tro == '3':
#         instance.hocsinh.save()

