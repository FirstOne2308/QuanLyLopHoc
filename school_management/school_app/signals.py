from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import HocSinh, MonHoc, KetQua

@receiver(m2m_changed, sender=HocSinh.lop_hoc.through)
def create_ket_qua_for_new_student(sender, instance, action, **kwargs):
    if action == 'post_add':  # Khi học sinh được thêm vào lớp học
        hoc_sinh = instance  # Đây là đối tượng HocSinh vừa được thay đổi
        for lop in hoc_sinh.lop_hoc.all():  # Lấy tất cả các lớp học mà học sinh tham gia
            for mon_hoc in MonHoc.objects.filter(nam_hoc=lop.nam_hoc):  # Lấy các môn học trong lớp
                KetQua.objects.create(
                    hoc_sinh=hoc_sinh,
                    mon_hoc=mon_hoc,
                    hoc_ki='1',  # Mặc định học kỳ 1
                    diem_15phut=0,
                    diem_1tiet=0,
                    diem_gk=0,
                    diem_ck=0
                )
                KetQua.objects.create(
                    hoc_sinh=hoc_sinh,
                    mon_hoc=mon_hoc,
                    hoc_ki='2',  # Mặc định học kỳ 2
                    diem_15phut=0,
                    diem_1tiet=0,
                    diem_gk=0,
                    diem_ck=0
                )
    
@receiver(m2m_changed, sender=HocSinh.lop_hoc.through)
def xoa_ket_qua_khi_hoc_sinh_xoa_lop(sender, instance, action, **kwargs):
    if action == 'post_remove':  # Khi học sinh được xóa khỏi lớp
        print(f"Xóa học sinh {instance} khỏi lớp")
        hoc_sinh = instance  # instance là đối tượng HocSinh
        # Đảm bảo rằng học sinh còn lớp học trước khi bị xóa khỏi lớp
        for lop in hoc_sinh.lop_hoc.all():  # Lấy tất cả các lớp học mà học sinh tham gia trước khi xóa
            for mon_hoc in MonHoc.objects.filter(nam_hoc=lop.nam_hoc):  # Lấy tất cả môn học trong lớp
                print(f"Xóa kết quả của học sinh {hoc_sinh} trong môn học {mon_hoc}")
                # Xóa kết quả học tập của học sinh đối với môn học trong lớp đó
                KetQua.objects.filter(
                    hoc_sinh=hoc_sinh,
                    mon_hoc=mon_hoc
                ).delete()  # Xóa tất cả các bản ghi kết quả học tập của học sinh đó
