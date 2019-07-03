from django.db import models

# Create your models here.
class NameField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(NameField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()


class Department(models.Model):
    department_no=models.IntegerField(default=0,unique=True)
    department_name=models.CharField(max_length=100,unique=True)

    def __str__(self):
        return(str(self.department_no)+" - "+self.department_name)

class Employee(models.Model):
    employee_id=models.CharField(max_length=20,unique=True)
    employee_name=models.CharField(max_length=100)
    employee_department=models.ForeignKey(Department,on_delete=models.CASCADE)

    def __str__(self):
        return(self.employee_id+' - '+self.employee_name+' - '+self.employee_department.department_name)


class SkillGroup(models.Model):
    skill_group_no=models.IntegerField(default=0,unique=True)
    skill_group_name=NameField(max_length=200,default="",unique=True)

    def __str__(self):
        return(str(self.skill_group_no)+" - "+self.skill_group_name)

class SkillLevel(models.Model):
    skill_level_name=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return(self.skill_level_name)

class Skill(models.Model):
    skill_name=NameField(max_length=200,unique=True)
    skill_group=models.ForeignKey(SkillGroup,on_delete=models.CASCADE)
    def __str__(self):
        return(str(self.skill_group)+" - "+self.skill_name)

class EmployeeSkillList(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    skill=models.ForeignKey(Skill,on_delete=models.CASCADE)
    skill_level=models.ForeignKey(SkillLevel,on_delete=models.CASCADE)
    class Meta:
        unique_together = ["employee", "skill"]
    def __str__(self):
        return(self.employee.employee_id+" - "+self.employee.employee_name+" - "+self.skill.skill_name+" - "+self.skill_level.skill_level_name)
        