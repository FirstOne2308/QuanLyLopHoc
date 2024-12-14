from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import HocSinh, KetQuaMonHoc, KetQuaNamHoc, MonHoc, KetQua

@receiver(m2m_changed, sender=HocSinh.lop_hoc.through)
def create_ket_qua_for_new_student(sender, instance, action, **kwargs):
    if action == 'post_add':  # Khi học sinh được thêm vào lớp học
        hoc_sinh = instance  # Đây là đối tượng HocSinh vừa được thay đổi
        for lop in hoc_sinh.lop_hoc.all():  # Lấy tất cả các lớp học mà học sinh tham gia
            # Kiểm tra nếu KetQua cho học sinh chưa có, thì mới tạo
            for mon_hoc in MonHoc.objects.all():  # Lấy tất cả các môn học
                # Kiểm tra xem KetQua học kỳ 1 đã tồn tại chưa
                if not KetQua.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=lop.nam_hoc, hoc_ki='1').exists():
                    # Tạo đối tượng KetQua cho học kỳ 1
                    KetQua.objects.create(
                        hoc_sinh=hoc_sinh,
                        mon_hoc=mon_hoc,
                        nam_hoc=lop.nam_hoc,
                        hoc_ki='1',  # Mặc định học kỳ 1
                        diem_15phut=0,
                        diem_1tiet=0,
                        diem_gk=0,
                        diem_ck=0
                    )
                # Kiểm tra xem KetQua học kỳ 2 đã tồn tại chưa
                if not KetQua.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc, nam_hoc=lop.nam_hoc, hoc_ki='2').exists():
                    # Tạo đối tượng KetQua cho học kỳ 2
                    KetQua.objects.create(
                        hoc_sinh=hoc_sinh,
                        mon_hoc=mon_hoc,
                        nam_hoc=lop.nam_hoc,
                        hoc_ki='2',  # Mặc định học kỳ 2
                        diem_15phut=0,
                        diem_1tiet=0,
                        diem_gk=0,
                        diem_ck=0
                    )
            
            # Kiểm tra nếu KetQuaMonHoc cho học sinh chưa có, thì mới tạo
            for mon_hoc in MonHoc.objects.all():
                if not KetQuaMonHoc.objects.filter(
                    hoc_sinh=hoc_sinh,
                    mon_hoc=mon_hoc,
                    nam_hoc=lop.nam_hoc
                ).exists():
                    KetQuaMonHoc.objects.create(
                        hoc_sinh=hoc_sinh,
                        mon_hoc=mon_hoc,
                        nam_hoc=lop.nam_hoc
                    )
            
            # Kiểm tra nếu KetQuaNamHoc cho học sinh chưa có, thì mới tạo
            if not KetQuaNamHoc.objects.filter(
                hoc_sinh=hoc_sinh,
                nam_hoc=lop.nam_hoc
            ).exists():
                KetQuaNamHoc.objects.create(
                    hoc_sinh=hoc_sinh,
                    nam_hoc=lop.nam_hoc
                )


@receiver(m2m_changed, sender=HocSinh.lop_hoc.through)
def xoa_ket_qua_khi_hoc_sinh_xoa_lop(sender, instance, action, **kwargs):
    """
    Khi học sinh bị xóa khỏi lớp, xóa tất cả các điểm và kết quả liên quan đến lớp đó
    """
    if action == 'post_remove':  # Hành động khi học sinh bị xóa khỏi lớp
        hoc_sinh = instance  # `instance` là đối tượng `HocSinh`
        
        # Lấy tất cả lớp học mà học sinh còn tham gia
        cac_lop_con_lai = hoc_sinh.lop_hoc.all()

        if not cac_lop_con_lai.exists():  # Nếu học sinh không còn thuộc lớp nào
            # Xóa tất cả các kết quả liên quan đến học sinh
            print(f"Xóa tất cả dữ liệu liên quan đến học sinh {hoc_sinh.nguoi_dung.username}")

            # Xóa tất cả kết quả của học sinh trong bảng `KetQua`
            KetQua.objects.filter(hoc_sinh=hoc_sinh).delete()

            # Xóa tất cả kết quả của học sinh trong bảng `KetQuaMonHoc`
            KetQuaMonHoc.objects.filter(hoc_sinh=hoc_sinh).delete()

            # Xóa tất cả kết quả của học sinh trong bảng `KetQuaNamHoc`
            KetQuaNamHoc.objects.filter(hoc_sinh=hoc_sinh).delete()
        else:
            # Nếu học sinh vẫn còn thuộc lớp khác, chỉ xóa dữ liệu liên quan đến lớp bị xóa
            # Lấy lớp bị xóa, lớp không còn tồn tại
            lop_bi_xoa = instance.lop_hoc.exclude(id__in=cac_lop_con_lai)

            if lop_bi_xoa.exists():
                lop_bi_xoa = lop_bi_xoa.first()  # Chỉ lấy lớp bị xóa đầu tiên

                # Lấy danh sách các môn học trong lớp bị xóa
                cac_mon_hoc_bi_xoa = MonHoc.objects.filter(nam_hoc=lop_bi_xoa.nam_hoc)

                # Xóa dữ liệu trong `KetQua`, `KetQuaMonHoc` cho lớp bị xóa
                for mon_hoc in cac_mon_hoc_bi_xoa:
                    KetQua.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc).delete()
                    KetQuaMonHoc.objects.filter(hoc_sinh=hoc_sinh, mon_hoc=mon_hoc).delete()

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
