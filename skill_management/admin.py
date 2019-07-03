from django.contrib import admin
from .models import Employee,Skill,EmployeeSkillList,SkillGroup,SkillLevel,Department
# Register your models here.

admin.site.register(Employee)
admin.site.register(Skill)
admin.site.register(EmployeeSkillList)
admin.site.register(SkillGroup)
admin.site.register(SkillLevel)
admin.site.register(Department)