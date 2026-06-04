# GP System — Graduation Project Management
### Jordan University of Science & Technology

---

## المتطلبات

| البرنامج | الإصدار | الرابط |
|---------|---------|--------|
| **Python** | 3.10 أو أحدث | https://www.python.org/downloads/ |
| **Node.js** | 16 أو أحدث (للاختبارات فقط) | https://nodejs.org/ |

> ⚠️ عند تثبيت Python، **تأكد من تفعيل خيار "Add Python to PATH"**

---

## تشغيل المشروع

### الطريقة الأولى — دبل كليك
```
انقر نقراً مزدوجاً على START.bat
```
سيفتح المتصفح تلقائياً على `http://127.0.0.1:8000`

### الطريقة الثانية — Terminal
```powershell
cd backend
.\venv_new\Scripts\activate
python manage.py runserver
```

---

## تشغيل الاختبارات

### اختبارات pytest-django (Backend)
```powershell
cd backend
.\venv_new\Scripts\python.exe -m pytest tests/ -v
```
- **78 اختبار** يغطي: Login, Teams, Supervisor Assignment, Grading, Notifications, Archiving, Meetings

### اختبارات Cypress (E2E)
تأكد أن الخادم يعمل أولاً، ثم:

```powershell
cd gp_final
npm install
```

**واجهة رسومية:**
```powershell
npm run cy:open
```

**تشغيل كل الاختبارات دفعة واحدة:**
```powershell
npm run cy:run
```

**تشغيل مع Admin (لاختبارات Team Merge):**
```powershell
npx cypress run --env ADMIN_EMAIL=admin@just.edu.jo,ADMIN_PASSWORD=Admin@GP2025
```

**تشغيل ملف محدد:**
```powershell
npx cypress run --spec "cypress/e2e/login.cy.js"
```

### ملفات الاختبارات (Cypress)
| الملف | ما يختبره | الحالات |
|-------|-----------|---------|
| `login.cy.js` | تسجيل الدخول | TC-1 → TC-13 |
| `creat_team.cy.js` | إنشاء الفرق | TC-T1 → TC-T9 |
| `notifications.cy.js` | الإشعارات | TC-N1 → TC-N7 |
| `team_change.cy.js` | تغيير الفريق | TC-1 → TC-10 |
| `supervisor_assignment.cy.js` | تعيين المشرف | TC-1 → TC-6 |
| `meetings.cy.js` | جدولة الاجتماعات | TC-1 → TC-3 |
| `grading.cy.js` | نظام الدرجات | TC-1 → TC-4 |
| `archiving.cy.js` | أرشفة المشاريع | TC-1 → TC-5 |

---

## بيانات الدخول

### المشرف العام (Admin)
| البريد | كلمة السر |
|--------|-----------|
| admin@just.edu.jo | Admin@GP2025 |

### المشرفون (Supervisors)
| الاسم | البريد | كلمة السر |
|-------|--------|-----------|
| Hamza Alkofahi | Hamza@just.edu.jo | Hamza0* |
| Mohammed Radaideh | Mohammed@just.edu.jo | Mohammed0* |
| Malik Qasimeh | Malik@just.edu.jo | Malik0* |
| Sadeen | sadeen@just.edu.jo | Sadeen0* |
| Razan | razan@just.edu.jo | Razan0* |
| Bayan | bayan@just.edu.jo | Bayan0* |
| Yanal Alahmad | Yanal@just.edu.jo | Yanal0* |
| Zakarea Alshara | Zakarea@just.edu.jo | Zakaria0* |
| Hasan Albzoor | Hasan@just.edu.jo | Hasan0* |
| Khaldoon Alzoubi | Khaldoon@just.edu.jo | Khaldoon0* |
| Raed Shatnawi | Raed@just.edu.jo | Raed0* |
| Asmahan Alhasan | Asmahan@just.edu.jo | Asmahan0* |
| Luay Alawneh | Luay@just.edu.jo | Luay0* |

### الطلاب (Students)
| الاسم | البريد | كلمة السر |
|-------|--------|-----------|
| Sadeen | sadeen@cit.just.edu.jo | Sadeen0* |
| Razan | razan@cit.just.edu.jo | Razan0* |
| Bayan | bayan@cit.just.edu.jo | Bayan0* |
| AbdulKarim | abdulKarim@cit.just.edu.jo | AbdulKarim0* |
| Hamam | hamam@cit.just.edu.jo | Hamam0* |
| Sara | sara@cit.just.edu.jo | Sara0* |
| Seham | seham@cit.just.edu.jo | Seham0* |
| Omar | omar@cit.just.edu.jo | Omar0* |
| Hala | hala@cit.just.edu.jo | Hala0* |

---

## هيكل المشروع

```
gp_final/
├── START.bat                    <- ابدأ من هنا (Windows)
├── README.md
├── package.json                 <- Cypress config
├── cypress.config.js
├── cypress/
│   ├── e2e/                     <- ملفات اختبارات Cypress (8 ملفات)
│   └── support/
│       └── commands.js          <- custom commands
├── frontend/                    <- صفحات HTML + JS + CSS
│   ├── login.html
│   ├── student_dashboard.html
│   ├── team_dashboard.html
│   ├── chat.html
│   ├── create_team.html
│   ├── supervisors_list.html
│   ├── Supervisor_dashboard.html
│   ├── supervisor_grading_reports.html
│   ├── supervisor_notifications.html
│   └── api.js
└── backend/                     <- Django REST API
    ├── manage.py
    ├── requirements.txt
    ├── pytest.ini
    ├── tests/                   <- اختبارات pytest-django (78 test)
    │   ├── test_login.py
    │   ├── test_teams.py
    │   ├── test_supervisor_assignment.py
    │   ├── test_grading.py
    │   ├── test_notifications.py
    │   ├── test_meetings.py
    │   └── test_archiving.py
    └── apps/
        ├── accounts/            <- المستخدمون + JWT
        ├── teams/               <- الفرق + supervision requests
        ├── requests/            <- طلبات المشرف
        ├── meetings/            <- الاجتماعات
        ├── grading/             <- الدرجات (50/25/25)
        ├── notifications/       <- الإشعارات
        ├── files/               <- الملفات
        └── supervisor_context/  <- DDD context للمشرف
```

---

## API Endpoints الرئيسية

| Endpoint | الوصف |
|----------|-------|
| `POST /api/v1/auth/login/` | تسجيل الدخول |
| `GET/POST /api/v1/teams/` | الفرق |
| `GET /api/v1/teams/my/` | فريق المستخدم الحالي |
| `GET /api/v1/teams/supervisors/` | قائمة المشرفين |
| `POST /api/v1/teams/<id>/supervisor-request/` | طلب مشرف |
| `GET /api/v1/teams/supervisor-inbox/` | صندوق المشرف |
| `POST /api/v1/grading/preview/` | حساب الدرجة (معاينة) |
| `GET /api/v1/notifications/` | الإشعارات |
| `GET /api/v1/supervisor/slots/` | مواعيد المشرف |
