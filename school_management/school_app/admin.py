from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    pass


admin.site.register(NguoiDung, UserModel)

admin.site.register(HocSinh)
admin.site.register(GiaoVien)
admin.site.register(QuanTriVien)
admin.site.register(LopHoc)
admin.site.register(NamHoc)
admin.site.register(MonHoc)
admin.site.register(KetQua)
# admin.site.register(CustomUser)
