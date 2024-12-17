from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import HocSinh, KetQuaMonHoc, KetQuaNamHoc, LopHoc, MonHoc, KetQua

from django.db.models import Q

# Hàm tạo KetQua cho học kỳ
def create_ket_qua(hoc_sinh, mon_hoc, lop, hoc_ki):
    if not KetQua.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=lop.nam_hoc, hoc_ki=hoc_ki).exists():
        KetQua.objects.create(
            hoc_sinh=hoc_sinh,
            mon_hoc=mon_hoc,
            nam_hoc=lop.nam_hoc,
            hoc_ki=hoc_ki,
            diem_15phut=0,
            diem_1tiet=0,
            diem_gk=0,
            diem_ck=0
        )

# Hàm tạo KetQuaMonHoc cho học sinh
def create_ket_qua_mon_hoc(hoc_sinh, mon_hoc, lop):
    if not KetQuaMonHoc.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=lop.nam_hoc).exists():
        KetQuaMonHoc.objects.create(
            hoc_sinh=hoc_sinh,
            mon_hoc=mon_hoc,
            nam_hoc=lop.nam_hoc
        )

# Hàm tạo KetQuaNamHoc cho học sinh
def create_ket_qua_nam_hoc(hoc_sinh, lop):
    if not KetQuaNamHoc.objects.filter(hoc_sinh=hoc_sinh, nam_hoc=lop.nam_hoc).exists():
        KetQuaNamHoc.objects.create(
            hoc_sinh=hoc_sinh,
            nam_hoc=lop.nam_hoc
        )

# Receiver xử lý khi học sinh được thêm vào lớp học
@receiver(m2m_changed, sender=HocSinh.lop_hoc.through)
def create_ket_qua_for_new_student(sender, instance, action, **kwargs):
    if action == 'post_add':  # Khi học sinh được thêm vào lớp học
        hoc_sinh = instance  # Đây là đối tượng HocSinh vừa được thay đổi

        # Áp dụng map để tạo KetQua cho học kỳ 1 và học kỳ 2
        for lop in hoc_sinh.lop_hoc.all():
            # Tạo KetQua cho học kỳ 1 và học kỳ 2
            list(map(lambda mon_hoc: create_ket_qua(hoc_sinh, mon_hoc, lop, '1'), MonHoc.objects.all()))
            list(map(lambda mon_hoc: create_ket_qua(hoc_sinh, mon_hoc, lop, '2'), MonHoc.objects.all()))

            # Tạo KetQuaMonHoc cho học sinh
            list(map(lambda mon_hoc: create_ket_qua_mon_hoc(hoc_sinh, mon_hoc, lop), MonHoc.objects.all()))

            # Tạo KetQuaNamHoc cho học sinh
            create_ket_qua_nam_hoc(hoc_sinh, lop)

from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=LopHoc)
def xoa_ket_qua_khi_xoa_lop(sender, instance, **kwargs):
    """
    Khi lớp học bị xóa, xóa tất cả các điểm và kết quả liên quan đến học sinh thuộc lớp đó.
    """
    # Lấy tất cả học sinh thuộc lớp học bị xóa
    hoc_sinh_list = instance.hocsinh_set.all()

    for hoc_sinh in hoc_sinh_list:
        print(f"Xóa dữ liệu kết quả của học sinh {hoc_sinh.nguoi_dung.username} liên quan đến lớp {instance.ma_lop}")
        
        # Lấy danh sách các môn học của lớp học bị xóa
        cac_mon_hoc_bi_xoa = MonHoc.objects.all()

        # Xóa dữ liệu trong `KetQua`, `KetQuaMonHoc` cho các môn học trong lớp học bị xóa
        for mon_hoc in cac_mon_hoc_bi_xoa:
            KetQua.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=instance.nam_hoc).delete()
            KetQuaMonHoc.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=instance.nam_hoc).delete()

        # Xóa dữ liệu trong `KetQuaNamHoc` liên quan đến năm học của lớp học bị xóa
        KetQuaNamHoc.objects.filter(hoc_sinh=hoc_sinh, nam_hoc=instance.nam_hoc).delete()



@receiver(m2m_changed, sender=HocSinh.lop_hoc.through)
def xoa_ket_qua_khi_hoc_sinh_xoa_lop(sender, instance, action, **kwargs):
    """
    Khi học sinh bị xóa khỏi lớp, xóa tất cả các điểm và kết quả liên quan đến lớp đó.
    """
    if action == 'post_remove':  # Hành động khi học sinh bị xóa khỏi lớp
        hoc_sinh = instance  # `instance` là đối tượng `HocSinh`
        
        # Lấy danh sách các lớp mà học sinh bị xóa khỏi lớp, sử dụng `pk_set` trong kwargs
        lop_hoc_bi_xoa_ids = kwargs.get('pk_set', [])

        # Lấy các lớp học bị xóa
        lop_bi_xoa = LopHoc.objects.filter(id__in=lop_hoc_bi_xoa_ids)

        if lop_bi_xoa.exists():  # Nếu có lớp bị xóa
            lop_bi_xoa = lop_bi_xoa.first()  # Lấy lớp bị xóa đầu tiên

            print(f"Lớp bị xóa: {lop_bi_xoa.nam_hoc} - {lop_bi_xoa.ma_lop}")

            # Lấy danh sách các môn học trong lớp bị xóa
            cac_mon_hoc_bi_xoa = MonHoc.objects.all()

            # Xóa dữ liệu trong `KetQua`, `KetQuaMonHoc` cho lớp bị xóa
            for mon_hoc in cac_mon_hoc_bi_xoa:
                KetQua.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=lop_bi_xoa.nam_hoc).delete()
                KetQuaMonHoc.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=lop_bi_xoa.nam_hoc).delete()

            # Xóa dữ liệu trong `KetQuaNamHoc` liên quan đến năm học của lớp bị xóa
            KetQuaNamHoc.objects.filter(hoc_sinh=hoc_sinh, nam_hoc=lop_bi_xoa.nam_hoc).delete()

        else:
            print(f"Học sinh {hoc_sinh.nguoi_dung.username} không thuộc lớp nào bị xóa.")


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import KetQuaMonHoc, KetQuaNamHoc

@receiver(post_save, sender=KetQua)
def update_ket_qua_mon_hoc_and_nam_hoc(sender, instance, **kwargs):
    """Cập nhật KetQuaMonHoc và KetQuaNamHoc khi KetQua thay đổi"""
    
    # Cập nhật KetQuaMonHoc
    ket_qua_mon_hoc = KetQuaMonHoc.objects.filter(
        hoc_sinh=instance.hoc_sinh,
        mon_hoc=instance.mon_hoc,
        nam_hoc=instance.nam_hoc
    ).first()

    if ket_qua_mon_hoc:
        # Tính lại điểm tổng kết của môn học này
        ket_qua_mon_hoc.save()  # Lưu lại điểm tổng kết cho môn học
    
    # Cập nhật KetQuaNamHoc
    # Lấy hoặc tạo đối tượng KetQuaNamHoc cho học sinh trong năm học
    ket_qua_nam_hoc = KetQuaNamHoc.objects.filter(
        hoc_sinh=instance.hoc_sinh,
        nam_hoc=instance.nam_hoc
    ).first()

    if ket_qua_nam_hoc:
        # Tính lại điểm tổng kết cho cả năm học
        ket_qua_nam_hoc.save()  # Lưu lại kết quả năm học
