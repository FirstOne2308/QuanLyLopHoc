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


# Lớp học
class LopHoc(models.Model):
    ma_lop = models.CharField(max_length=10, null=False, unique=False)
    so_hoc_sinh = models.IntegerField(null=False)
    nam_hoc = models.ForeignKey(
        NamHoc, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.nam_hoc.nam + '_' + self.ma_lop


# Môn học
class MonHoc(models.Model):
    ma_mon = models.CharField(max_length=200, null=False, unique=True)
    ten_mon = models.CharField(max_length=200, null=False, unique=True)
    diem_chuan = models.FloatField(null=False)
    nam_hoc = models.ForeignKey(NamHoc, null=False, on_delete=models.CASCADE)

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

    def __str__(self):
        return self.nguoi_dung.username


# Bảng kết quả
class KetQua(models.Model):
    HOC_KI = (
        ('1', "Học kỳ 1"),
        ('2', "Học kỳ 2")
    )
    hoc_sinh = models.ForeignKey(HocSinh, on_delete=models.CASCADE)
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
    hoc_ki = models.CharField(
        max_length=200, null=False, choices=HOC_KI)
    diem_15phut = models.FloatField(null=True, blank=True)
    diem_1tiet = models.FloatField(null=True, blank=True)
    diem_final = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.hoc_sinh.nguoi_dung.username}_{self.hoc_ki}"


# Tạo profile người dùng dựa theo vai trò
@receiver(post_save, sender=NguoiDung)
def tao_profile(sender, instance, created, **kwargs):
    if created:
        if instance.vai_tro == '1':
            QuanTriVien.objects.create(nguoi_dung=instance)
        if instance.vai_tro == '2':
            GiaoVien.objects.create(nguoi_dung=instance)
        if instance.vai_tro == '3':
            HocSinh.objects.create(nguoi_dung=instance)


@receiver(post_save, sender=NguoiDung)
def luu_profile(sender, instance, **kwargs):
    if instance.vai_tro == '1':
        instance.nhanvien.save()
    if instance.vai_tro == '2':
        instance.giao_vien.save()
    if instance.vai_tro == '3':
        instance.hoc_sinh.save()
