from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q 
from django.contrib.auth import logout  # حل مشكلة اللوج أوت
from .models import Team, Membership, Notification, TeamMessage # حل مشكلة المسجات
from .models import Team, JoinRequest

# 1. قائمة المستخدمين التجريبيين
users_data = [
    {"email": "sadeen@cit.just.edu.jo", "password": "Sadeen0*", "type": "student", "name": "Sadeen"},
    {"email": "razan@cit.just.edu.jo", "password": "Razan0*", "type": "student", "name": "Razan"},
    {"email": "bayan@cit.just.edu.jo", "password": "Bayan0*", "type": "student", "name": "Bayan"},
    {"email": "sara@cit.just.edu.jo", "password": "Sara0*", "type": "student", "name": "Sara"},
    {"email": "Hala@cit.just.edu.jo", "password": "Hala0*", "type": "student", "name": "hala"},
]
from django.contrib.auth import login
# 2. تسجيل الدخول
# 2. تسجيل الدخول
def index(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        for user_data in users_data:
            if user_data["email"] == email and user_data["password"] == password:
                # إنشاء أو جلب اليوزر من الداتابيز
                user_obj, created = User.objects.get_or_create(
                    username=email, 
                    defaults={'email': email, 'first_name': user_data['name']}
                )
                
                # *** السطر اللي ناقص ومسبب كل المشاكل ***
                login(request, user_obj) 
                
                request.session['user_name'] = user_data['name']
                request.session['user_email'] = user_data['email']
                
                return redirect("student_dashboard")
        return render(request, "index.html", {"error_msg": "Email or password incorrect!"})
    return render(request, "index.html")


# 3. لوحة التحكم (Dashboard)
# views.py
# 3. لوحة التحكم (Dashboard)
def student_dashboard(request):
    # بدل الاعتماد على request.user مباشرة، نجلب الإيميل من السيشن
    user_email = request.session.get('user_email')
    
    if not user_email:
        return redirect('index') # إذا مش مسجل دخول يرجعه للبداية

    # نجلب كائن المستخدم الحقيقي
    current_user = get_object_or_404(User, username=user_email)

    # نستخدم current_user في الفلتر
    user_membership = Membership.objects.filter(user=current_user).exclude(role='Pending').first()
    
    pending_requests = []
    user_has_team = False
    team = None

    if user_membership:
        user_has_team = True
        team = user_membership.team
        pending_requests = Membership.objects.filter(team=team, role='Pending')

    context = {
        'user_has_team': user_has_team,
        'team': team,
        'pending_requests': pending_requests,
    }
    return render(request, 'student_dashboard.html', context)


# 4. إنشاء فريق جديد
def create_team(request):
    user_email = request.session.get('user_email')
    if not user_email: return redirect('index')
    user = get_object_or_404(User, username=user_email)

    if Membership.objects.filter(user=user, role__in=['Leader', 'Member']).exists():
        return redirect('student_dashboard')

    if request.method == "POST":
        team = Team.objects.create(
            name=request.POST['team_name'],
            description=request.POST.get('description', ''),
            leader=user
        )
        Membership.objects.create(user=user, team=team, role='Leader')
        return redirect('student_dashboard')
    return render(request, 'create_team.html')

# 5. البحث عن فريق
def join_team(request):
    user_email = request.session.get('user_email')
    if not user_email: return redirect('index')
    user = get_object_or_404(User, username=user_email)

    teams = Team.objects.annotate(
        actual_member_count=Count('memberships', filter=Q(memberships__role__in=['Leader', 'Member']))
    ).order_by('-created_at')

    pending_teams_ids = Membership.objects.filter(user=user, role='Pending').values_list('team_id', flat=True)
    
    return render(request, 'join_team.html', {
        'teams': teams,
        'pending_teams_ids': list(pending_teams_ids)
    })

# 6. إرسال طلب انضمام
def send_join_request(request, team_id):
    user_email = request.session.get('user_email')
    if not user_email: return redirect('index')
    
    user = get_object_or_404(User, username=user_email)
    team = get_object_or_404(Team, id=team_id)

    if Membership.objects.filter(user=user, role__in=['Leader', 'Member']).exists():
        return redirect('student_dashboard')
        
    Membership.objects.get_or_create(user=user, team=team, defaults={'role': 'Pending'})
    Notification.objects.create(user=team.leader, message=f"New request from {user.username} to join {team.name}")
    
    return redirect('join_team')

# 7. Workspace
def team_page(request, team_id):
    user_email = request.session.get('user_email')
    if not user_email: return redirect('index')
    
    user = get_object_or_404(User, username=user_email)
    team = get_object_or_404(Team, id=team_id)
    
    membership = Membership.objects.filter(user=user, team=team, role__in=['Leader', 'Member']).first()
    if not membership:
        return redirect('student_dashboard')

    pending_requests = team.memberships.filter(role='Pending')

    return render(request, 'team_page.html', {
        'team': team,
        'membership': membership,
        'pending_requests': pending_requests,
    })

# 8. التعامل مع الطلبات
def handle_membership_request(request, membership_id, action):
    if request.method == "POST":
        # 1. نجلب الممبرشيب المعنية (الطلب اللي الليدر ضغط عليه)
        membership = get_object_or_404(Membership, id=membership_id)
        student = membership.user  # الطالب صاحب الطلب

        if action == 'approve':
            # 2. نحول حالة الطالب من Pending إلى Member (أو Leader حسب الحاجة)
            membership.role = 'Member'
            membership.save()

            # 3. *** الخطوة السحرية ***
            # نحذف كل الممبرشيب اللي حالتها 'Pending' لهذا الطالب في أي فريق آخر
            # هيك بنظف الداتابيز وبنلغي كل ريكويستاته الثانية تلقائياً
            Membership.objects.filter(user=student, role='Pending').delete()
            
            # (اختياري) ممكن تبعث نوتيفيكيشن للطالب إنه انقبل
            Notification.objects.create(user=student, message=f"Congrats! You have been accepted in {membership.team.name}")

        elif action == 'reject':
            # إذا رفضه، بنحذف بس هاد الريكويست وبنخلي ريكويستاته للفرق الثانية شغالين
            membership.delete()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

# 9. مغادرة الفريق
def leave_team(request):
    user_email = request.session.get('user_email')
    if not user_email: return redirect('index')
    user = get_object_or_404(User, username=user_email)
    membership = Membership.objects.filter(user=user, role__in=['Leader', 'Member']).first()

    if membership:
        team = membership.team
        membership.delete()
        if not team.memberships.exists():
            team.delete()
        elif membership.role == 'Leader':
            new_leader_mem = team.memberships.first()
            if new_leader_mem:
                new_leader_mem.role = 'Leader'
                new_leader_mem.save()
                team.leader = new_leader_mem.user
                team.save()
    return redirect('student_dashboard')

# 10. المشرفين والرسائل
def supervisors_list(request):
    user_email = request.session.get('user_email')
    if not user_email: return redirect('index')
    return render(request, 'supervisors_list.html')

def send_message(request, team_id):
    if request.method == "POST":
        team = get_object_or_404(Team, id=team_id)
        user_email = request.session.get('user_email')
        user = get_object_or_404(User, username=user_email)
        
        content = request.POST.get('content', '')
        file = request.FILES.get('file')
        
        if content or file:
            TeamMessage.objects.create(
                team=team, user=user, content=content, file=file
            )
            return JsonResponse({'status': 'sent'})
    return JsonResponse({'status': 'error'}, status=400)

def get_messages(request, team_id):
    messages = TeamMessage.objects.filter(team_id=team_id).order_by('timestamp')
    data = []
    for m in messages:
        data.append({
            'user': m.user.username,
            'content': m.content,
            'file_url': m.file.url if m.file else None,
            'is_me': m.user.username == request.session.get('user_email'),
            'time': m.timestamp.strftime('%H:%M')
        })
    return JsonResponse({'messages': data})

def logout_user(request):
    logout(request) # الآن ستعمل لأننا أضفنا الـ import
    return redirect('index') # عدلتها لـ 'index' لأنه هاد الرابط الافتراضي للوجين عندك

def cancel_join_request(request, team_id):
    user_email = request.session.get('user_email')
    user = get_object_or_404(User, username=user_email)
    
    # بنحذف الريكويست من جدول الممبرشيب اللي حالته Pending
    pending_membership = Membership.objects.filter(
        user=user, 
        team_id=team_id, 
        role='Pending'
    ).first()
    
    if pending_membership:
        print(f"Deleting pending request for {user.username} in team {team_id}")
        pending_membership.delete()
    
    return redirect('join_team')

def approve_request(request, request_id):
    # بنجيب الممبرشيب اللي حالتها Pending
    membership = get_object_or_404(Membership, id=request_id)
    student = membership.user
    
    # 1. بنحول حالته من Pending لـ Member
    membership.role = 'Member'
    membership.save()
    
    # 2. بنحذف أي طلبات ثانية (Pending) لهاد الطالب في فرق ثانية
    Membership.objects.filter(user=student, role='Pending').delete()
    
    return JsonResponse({'status': 'success'})