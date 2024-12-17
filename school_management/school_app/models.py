from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser
from django.contrib.auth.hashers import make_password
from datetime import datetime, date
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# Custom User Manager
class NguoiDungManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        user = NguoiDung(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(username, password, **extra_fields)


# Mô hình người dùng
class NguoiDung(AbstractUser):
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
        return self.ho_ten


# Mô hình tuổi học sinh
class NamHoc(models.Model):
    nam = models.CharField(max_length=200, unique=True)
    tuoi_toi_da = models.IntegerField(null=False)
    tuoi_toi_thieu = models.IntegerField(null=False)

    def __str__(self):
        return self.nam

from django.db.models.signals import post_migrate
@receiver(post_migrate)
def create_default_nam_hoc(sender, **kwargs):
    current_year = datetime.now().year
    for year in range(2021, current_year + 1):
        nam_hoc = f"{year}-{year + 1}"
        if not NamHoc.objects.filter(nam=nam_hoc).exists():
            NamHoc.objects.create(nam=nam_hoc, tuoi_toi_da=20, tuoi_toi_thieu=14)

# Lớp học
class LopHoc(models.Model):
    ma_lop = models.CharField(max_length=10, null=False, unique=False)
    so_hoc_sinh = models.IntegerField(null=True)
    nam_hoc = models.ForeignKey(
        NamHoc, null=False, on_delete=models.CASCADE)
    giao_vien_chu_nhiem = models.ForeignKey("GiaoVien", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.nam_hoc.nam + '_' + self.ma_lop


# Môn học
class MonHoc(models.Model):
    ma_mon = models.CharField(max_length=200, null=False, unique=True)
    ten_mon = models.CharField(max_length=200, null=False, unique=True)
    diem_chuan = models.FloatField(null=False)

    def __str__(self):
        return self.ten_mon


# Quản trị viên
class QuanTriVien(models.Model):
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE)

    def __str__(self):
        return self.nguoi_dung.username


# Học sinh
class HocSinh(models.Model):
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE)
    lop_hoc = models.ManyToManyField(LopHoc, blank=True)

    def __str__(self):
        return self.nguoi_dung.username


# Giáo viên
class GiaoVien(models.Model):
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE)
    mon_day = models.ForeignKey(MonHoc, blank=True, on_delete=models.CASCADE)
    lop_day = models.ManyToManyField(LopHoc, blank=True)
    def __str__(self):
        return f'{self.nguoi_dung.ho_ten}({self.nguoi_dung.username})'


# Bảng kết quả
# class KetQua(models.Model):
#     HOC_KI = (
#         ('1', "Học kỳ 1"),
#         ('2', "Học kỳ 2")
#     )
#     hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE)
#     mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
#     nam_hoc = models.ForeignKey(NamHoc, null=False, on_delete=models.CASCADE)
#     hoc_ki = models.CharField(
#         max_length=200, null=False, choices=HOC_KI)
#     diem_15phut = models.FloatField(null=True, blank=True)
#     diem_1tiet = models.FloatField(null=True, blank=True)
#     diem_gk = models.FloatField(null=True, blank=True)
#     diem_ck = models.FloatField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.hoc_sinh.nguoi_dung.username}_{self.hoc_ki}"
class KetQua(models.Model):
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
    hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE)
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
    nam_hoc = models.ForeignKey(NamHoc, on_delete=models.CASCADE)
    
    diem_tong_ket = models.FloatField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Lấy điểm học kỳ 1 và học kỳ 2 từ bảng KetQua
        diem_hk1 = KetQua.objects.filter(
            hoc_sinh=self.hoc_sinh,
            mon_hoc=self.mon_hoc,
            nam_hoc=self.nam_hoc,
            hoc_ki='1'
        ).first()  # Dùng first() để tránh lỗi nếu có nhiều kết quả

        diem_hk2 = KetQua.objects.filter(
            hoc_sinh=self.hoc_sinh,
            mon_hoc=self.mon_hoc,
            nam_hoc=self.nam_hoc,
            hoc_ki='2'
        ).first()  # Dùng first() để tránh lỗi nếu có nhiều kết quả

        # Tính điểm tổng kết nếu có cả điểm HK1 và HK2
        if diem_hk1 and diem_hk2:
            # Công thức tính điểm tổng kết
            self.diem_tong_ket = (diem_hk1.diem_tong + diem_hk2.diem_tong * 2) / 3
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hoc_sinh.nguoi_dung.username} - {self.mon_hoc.ten_mon} - {self.nam_hoc.nam}"



class KetQuaNamHoc(models.Model):
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
        # Lấy tất cả các môn học trong năm học
        mon_hocs = MonHoc.objects.all()
        total_points = 0
        total_subjects = 0

        # Tính tổng điểm cho từng môn
        for mon_hoc in mon_hocs:
            ket_qua_mon_hoc = KetQuaMonHoc.objects.filter(
                hoc_sinh=self.hoc_sinh, mon_hoc=mon_hoc, nam_hoc=self.nam_hoc
            ).first()

            if ket_qua_mon_hoc and ket_qua_mon_hoc.diem_tong_ket is not None:
                total_points += ket_qua_mon_hoc.diem_tong_ket
                total_subjects += 1

        # Tính điểm tổng kết của năm học
        if total_subjects > 0:
            self.diem_tong_ket = total_points / total_subjects

        # Xét kết quả dựa trên điểm tổng kết và hạnh kiểm
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
