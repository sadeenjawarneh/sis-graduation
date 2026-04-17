from django.db import models
from django.contrib.auth.models import User

# 1. موديل الطالب
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.user.username

# 2. موديل الفريق (تعريف واحد فقط!)
class Team(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Locked', 'Locked'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def member_count(self):
        # يحسب عدد الأعضاء المقبولين فقط (Leader + Member)
        return self.memberships.filter(role__in=['Leader', 'Member']).count()

    def __str__(self):
        return self.name

# 3. موديل العضوية (تعريف واحد يدمج التصويت والمهام)
class Membership(models.Model):
    ROLE_CHOICES = [
        ('Leader', 'Leader'),
        ('Member', 'Member'),
        ('Pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    # حقل التصويت المطلوب
    voted_by = models.ManyToManyField(User, related_name='memberships_voted_for', blank=True)

    class Meta:
        unique_together = ('user', 'team')

    def __str__(self):
        return f"{self.user.username} in {self.team.name} ({self.role})"

# 4. موديل الرسائل (للشات)
class TeamMessage(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_voice = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg from {self.user.username} at {self.timestamp}"

# 5. موديل التنبيهات
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]

# داخل ملف models.py

class JoinRequest(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE) # الطالب اللي بعث الطلب
    team = models.ForeignKey(Team, on_delete=models.CASCADE)    # التيم المستهدف
    created_at = models.DateTimeField(auto_now_add=True)       # وقت إرسال الطلب

    def __str__(self):
        return f"{self.student.username} -> {self.team.name}"