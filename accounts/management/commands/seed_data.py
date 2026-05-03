"""
Seed-файл для проекту Palamar (Електронний щоденник)
======================================================
Розміщення: accounts/management/commands/seed_data.py

Спочатку створіть директорії:
    mkdir -p accounts/management/commands
    touch accounts/management/__init__.py
    touch accounts/management/commands/__init__.py

Запуск:
    python manage.py seed_data
    python manage.py seed_data --clear     # очистити БД перед заповненням

Що буде створено:
  - 1 адміністратор
  - 8 викладачів (з профілями Teacher)
  - 6 груп (2 факультети × 3 курси)
  - 16 предметів (по семестрах)
  - 48 студентів (по 8 у кожній групі)
  - Розклад (5 занять на день × 5 днів × 6 груп)
  - Оцінки (поточні, модульні, іспити) — ~600 записів
  - Завдання (3 на предмет) + здані роботи (~400 записів)
  - Відвідуваність (за останні 60 днів) — ~2000 записів
"""

import random
from datetime import date, timedelta, datetime, time

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone


# ─── Реалістичні дані для генерації ────────────────────────────────────────────

MALE_FIRST_NAMES = [
    "Олексій", "Андрій", "Максим", "Дмитро", "Іван", "Михайло",
    "Сергій", "Богдан", "Тарас", "Владислав", "Назар", "Євген",
    "Роман", "Ярослав", "Артем", "Олег", "Данило", "Кирило",
    "Вадим", "Павло",
]

FEMALE_FIRST_NAMES = [
    "Анастасія", "Вікторія", "Катерина", "Юлія", "Марія", "Ірина",
    "Оксана", "Людмила", "Тетяна", "Наталія", "Ольга", "Аліна",
    "Діана", "Соломія", "Дарина", "Поліна", "Валерія", "Єлизавета",
    "Христина", "Лариса",
]

MALE_LAST_NAMES = [
    "Коваленко", "Мельник", "Шевченко", "Бондаренко", "Ткаченко",
    "Кравченко", "Іваненко", "Олійник", "Шевчук", "Гриценко",
    "Захаренко", "Марченко", "Петренко", "Савченко", "Назаренко",
    "Даниленко", "Павленко", "Тимченко", "Луценко", "Романенко",
    "Власенко", "Лисенко", "Клименко", "Семененко", "Яременко",
    "Пилипенко", "Дяченко", "Хоменко", "Рибаченко", "Волошин",
]

FEMALE_LAST_NAMES = [
    "Коваленко", "Мельник", "Шевченко", "Бондаренко", "Ткаченко",
    "Кравченко", "Іваненко", "Олійник", "Шевчук", "Гриценко",
    "Захаренко", "Марченко", "Петренко", "Савченко", "Назаренко",
    "Даниленко", "Павленко", "Тимченко", "Луценко", "Романенко",
    "Власенко", "Лисенко", "Клименко", "Семененко", "Яременко",
    "Пилипенко", "Дяченко", "Хоменко", "Рибаченко", "Волошин",
]

MIDDLE_NAMES_MALE = [
    "Олексійович", "Андрійович", "Максимович", "Дмитрович", "Іванович",
    "Михайлович", "Сергійович", "Богданович", "Тарасович", "Владиславович",
]

MIDDLE_NAMES_FEMALE = [
    "Олексіївна", "Андріївна", "Максимівна", "Дмитрівна", "Іванівна",
    "Михайлівна", "Сергіївна", "Богданівна", "Тарасівна", "Владиславівна",
]


# ─── Дані викладачів ────────────────────────────────────────────────────────────

TEACHERS_DATA = [
    {
        "username": "kovalchuk_v",
        "first_name": "Василь",
        "last_name": "Ковальчук",
        "email": "kovalchuk@university.edu.ua",
        "department": "Кафедра комп'ютерних наук",
        "academic_degree": "кандидат технічних наук, доцент",
    },
    {
        "username": "petrenko_o",
        "first_name": "Оксана",
        "last_name": "Петренко",
        "email": "petrenko@university.edu.ua",
        "department": "Кафедра програмної інженерії",
        "academic_degree": "доктор технічних наук, професор",
    },
    {
        "username": "lysenko_m",
        "first_name": "Михайло",
        "last_name": "Лисенко",
        "email": "lysenko@university.edu.ua",
        "department": "Кафедра математики та фізики",
        "academic_degree": "кандидат фізико-математичних наук, доцент",
    },
    {
        "username": "savchenko_n",
        "first_name": "Наталія",
        "last_name": "Савченко",
        "email": "savchenko@university.edu.ua",
        "department": "Кафедра економіки та менеджменту",
        "academic_degree": "кандидат економічних наук",
    },
    {
        "username": "bondarenko_i",
        "first_name": "Ігор",
        "last_name": "Бондаренко",
        "email": "bondarenko@university.edu.ua",
        "department": "Кафедра комп'ютерних наук",
        "academic_degree": "асистент",
    },
    {
        "username": "marchenko_t",
        "first_name": "Тетяна",
        "last_name": "Марченко",
        "email": "marchenko@university.edu.ua",
        "department": "Кафедра іноземних мов",
        "academic_degree": "кандидат педагогічних наук, доцент",
    },
    {
        "username": "hrychenko_d",
        "first_name": "Денис",
        "last_name": "Гриценко",
        "email": "hrychenko@university.edu.ua",
        "department": "Кафедра кібербезпеки",
        "academic_degree": "доктор технічних наук, професор",
    },
    {
        "username": "kravchenko_a",
        "first_name": "Алла",
        "last_name": "Кравченко",
        "email": "kravchenko@university.edu.ua",
        "department": "Кафедра програмної інженерії",
        "academic_degree": "кандидат технічних наук",
    },
]


# ─── Групи ──────────────────────────────────────────────────────────────────────

GROUPS_DATA = [
    # Факультет інформаційних технологій
    {"name": "КН-11", "faculty": "Факультет інформаційних технологій", "year_formed": 2025, "specialty": "Комп'ютерні науки", "year_of_study": 1},
    {"name": "КН-21", "faculty": "Факультет інформаційних технологій", "year_formed": 2024, "specialty": "Комп'ютерні науки", "year_of_study": 2},
    {"name": "КН-31", "faculty": "Факультет інформаційних технологій", "year_formed": 2023, "specialty": "Комп'ютерні науки", "year_of_study": 3},
    # Факультет економіки та управління
    {"name": "МН-11", "faculty": "Факультет економіки та управління", "year_formed": 2025, "specialty": "Менеджмент", "year_of_study": 1},
    {"name": "МН-21", "faculty": "Факультет економіки та управління", "year_formed": 2024, "specialty": "Менеджмент", "year_of_study": 2},
    {"name": "МН-31", "faculty": "Факультет економіки та управління", "year_formed": 2023, "specialty": "Менеджмент", "year_of_study": 3},
]


# ─── Предмети ────────────────────────────────────────────────────────────────────

SUBJECTS_DATA = [
    # ІТ-спеціальності
    {"name": "Вища математика", "credits": 6, "semester": 1, "description": "Математичний аналіз, лінійна алгебра, аналітична геометрія.", "teacher_idx": 2},
    {"name": "Дискретна математика", "credits": 4, "semester": 1, "description": "Теорія множин, комбінаторика, теорія графів.", "teacher_idx": 2},
    {"name": "Основи програмування (C++)", "credits": 5, "semester": 1, "description": "Основні конструкції мови C++. Процедурне програмування.", "teacher_idx": 0},
    {"name": "Комп'ютерна архітектура", "credits": 4, "semester": 2, "description": "Будова процесора, пам'яті та периферійних пристроїв.", "teacher_idx": 4},
    {"name": "Алгоритми та структури даних", "credits": 5, "semester": 2, "description": "Сортування, пошук, дерева, хеш-таблиці, графові алгоритми.", "teacher_idx": 0},
    {"name": "Об'єктно-орієнтоване програмування", "credits": 5, "semester": 3, "description": "Принципи ООП: інкапсуляція, спадкування, поліморфізм. Мова Java.", "teacher_idx": 7},
    {"name": "Бази даних", "credits": 5, "semester": 3, "description": "Реляційні СУБД, SQL, нормалізація, транзакції.", "teacher_idx": 4},
    {"name": "Програмування на Python", "credits": 5, "semester": 3, "description": "Основи Python та фреймворку Django для веб-розробки.", "teacher_idx": 0},
    {"name": "Операційні системи", "credits": 4, "semester": 4, "description": "Linux/Unix, процеси, файлові системи, мережеві утиліти.", "teacher_idx": 6},
    {"name": "Комп'ютерні мережі", "credits": 4, "semester": 4, "description": "Стек TCP/IP, маршрутизація, протоколи, мережева безпека.", "teacher_idx": 6},
    {"name": "Веб-технології", "credits": 4, "semester": 5, "description": "HTML5, CSS3, JavaScript, фреймворки React та Vue.js.", "teacher_idx": 7},
    {"name": "Кібербезпека", "credits": 4, "semester": 5, "description": "Захист інформації, шифрування, аудит безпеки, пентестинг.", "teacher_idx": 6},
    # Загальноосвітні
    {"name": "Іноземна мова (англійська)", "credits": 3, "semester": 1, "description": "Ділова та технічна англійська мова. Рівень B1–B2.", "teacher_idx": 5},
    {"name": "Ділова комунікація", "credits": 3, "semester": 2, "description": "Навички ділового спілкування, презентацій та ведення переговорів.", "teacher_idx": 5},
    {"name": "Основи економіки", "credits": 4, "semester": 1, "description": "Мікро- та макроекономіка, ринкові механізми.", "teacher_idx": 3},
    {"name": "Менеджмент організацій", "credits": 5, "semester": 3, "description": "Функції управління, організаційні структури, стратегічний менеджмент.", "teacher_idx": 3},
]

# Предмети для кожної групи (за семестрами)
GROUP_SUBJECTS_MAP = {
    "КН-11": [0, 1, 2, 12, 14],       # 1-й семестр ІТ + Іноземна + Економіка
    "КН-21": [3, 4, 13],               # 2-й семестр ІТ + Ділова комунікація
    "КН-31": [5, 6, 7, 15],            # 3-й семестр ІТ + Менеджмент
    "МН-11": [14, 12, 1],              # Економіка + Іноземна + Дискретна
    "МН-21": [13, 3, 15],              # Ділова + Комп. арх. + Менеджмент
    "МН-31": [15, 10, 11],             # Менеджмент + Веб + Кібербезпека
}

# ─── Завдання ────────────────────────────────────────────────────────────────────

ASSIGNMENT_TEMPLATES = {
    "Вища математика": [
        {"title": "Домашня робота №1: Границі та неперервність", "description": "Обчислити границі функцій за варіантами (10 задач). Виконати аналітично та перевірити графічно."},
        {"title": "Домашня робота №2: Похідні та диференціали", "description": "Знайти похідні складних функцій (15 задач). Застосувати правило Лопіталя для 5 невизначеностей."},
        {"title": "Розрахункова робота: Інтегральне числення", "description": "Обчислити визначені та невизначені інтеграли. Знайти площу фігури, обмеженої кривими."},
    ],
    "Основи програмування (C++)": [
        {"title": "Лабораторна №1: Базові конструкції C++", "description": "Реалізувати програму для обчислення математичних виразів з умовами та циклами. Варіанти у додатку."},
        {"title": "Лабораторна №2: Масиви та рядки", "description": "Написати функції обробки одновимірних та двовимірних масивів. Реалізувати пошук та сортування."},
        {"title": "Курсова робота: Менеджер завдань", "description": "Розробити консольний менеджер завдань із можливістю додавання, редагування, видалення та збереження у файл."},
    ],
    "Алгоритми та структури даних": [
        {"title": "Практична №1: Реалізація стека та черги", "description": "Реалізувати стек та чергу на масиві та зв'язному списку. Порівняти ефективність обох підходів."},
        {"title": "Практична №2: Дерева пошуку", "description": "Реалізувати BST та AVL-дерево. Виміряти час операцій вставки, пошуку та видалення для N=1000, 10000, 100000 елементів."},
        {"title": "Індивідуальне завдання: Графові алгоритми", "description": "Реалізувати алгоритм Дейкстри та BFS/DFS. Знайти найкоротший шлях у заданому графі."},
    ],
    "Програмування на Python": [
        {"title": "Лабораторна №1: Основи Python", "description": "Написати скрипти для обробки текстових файлів, роботи зі словниками та генераторами списків."},
        {"title": "Лабораторна №2: ООП у Python", "description": "Реалізувати ієрархію класів для предметної галузі. Застосувати магічні методи та властивості."},
        {"title": "Проект: Django-застосунок", "description": "Розробити повноцінний веб-застосунок на Django з автентифікацією, CRUD-операціями та адмін-панеллю."},
    ],
    "Бази даних": [
        {"title": "Лабораторна №1: DDL та DML-команди", "description": "Створити схему бази даних (5+ таблиць) для обраної предметної галузі. Заповнити тестовими даними."},
        {"title": "Лабораторна №2: Складні SELECT-запити", "description": "Написати 15 запитів з використанням JOIN, підзапитів, агрегатних функцій та GROUP BY."},
        {"title": "Курсова: Проектування ІС", "description": "Спроектувати та реалізувати інформаційну систему з документованою схемою БД, ER-діаграмою та демо-застосунком."},
    ],
    "Іноземна мова (англійська)": [
        {"title": "Writing Task: IT Cover Letter", "description": "Write a professional cover letter (250–300 words) for a junior developer position at a tech company."},
        {"title": "Reading Comprehension: Tech Articles", "description": "Read 3 assigned articles about AI trends. Write a summary (150 words each) and answer 10 comprehension questions."},
        {"title": "Presentation: My Tech Project", "description": "Prepare a 5-minute presentation in English about your programming project. Include slides and Q&A section."},
    ],
    "Менеджмент організацій": [
        {"title": "Реферат: Аналіз організаційної структури", "description": "Проаналізувати організаційну структуру відомої компанії (Apple, Google, Нова Пошта тощо). Обсяг: 15–20 сторінок."},
        {"title": "Кейс-завдання: Прийняття управлінських рішень", "description": "Вирішити запропонований кейс із застосуванням методів SWOT-аналізу та дерева рішень."},
        {"title": "Бізнес-план стартапу", "description": "Розробити повноцінний бізнес-план для стартапу за обраною ідеєю. Захист на семінарі."},
    ],
    "DEFAULT": [
        {"title": "Домашнє завдання №1", "description": "Виконати завдання за варіантом. Здати у форматі PDF до вказаного дедлайну."},
        {"title": "Лабораторна робота №1", "description": "Практична реалізація теоретичного матеріалу лекцій 1–4. Звіт оформити за стандартом кафедри."},
        {"title": "Контрольна робота", "description": "Виконати теоретичні питання (20 балів) та практичну задачу (80 балів). Здати до кінця тижня."},
    ],
}

# ─── Комментарі до оцінок ────────────────────────────────────────────────────────

GRADE_COMMENTS_POSITIVE = [
    "Чудова робота, повна відповідь.",
    "Відмінно! Студент продемонстрував глибоке розуміння матеріалу.",
    "Бездоганне виконання завдання.",
    "Творчий підхід до вирішення задачі.",
    "Дуже добре! Незначні неточності в оформленні.",
    None, None, None,  # частина без коментаря
]

GRADE_COMMENTS_NEGATIVE = [
    "Поверхневе розкриття теми. Рекомендую доопрацювати.",
    "Допущені помилки в розрахунках. Перездати.",
    "Робота виконана не в повному обсязі.",
    "Відповідь не відповідає вимогам. Потребує доопрацювання.",
    None,
]

# ─── Причини відсутності ─────────────────────────────────────────────────────────

ABSENCE_REASONS = [
    "Хвороба",
    "Лікарняний",
    "Сімейні обставини",
    "Участь у конференції",
    "Змагання",
    None,  # без причини
    None,
    None,
]

# ─── Аудиторії ───────────────────────────────────────────────────────────────────

ROOMS = ["101", "102", "103", "201", "202", "203", "301", "302", "Л-101", "Л-201", "Комп-1", "Комп-2"]

# ─── Розклад (шаблони часів занять) ─────────────────────────────────────────────

LESSON_TIMES = [
    (time(8, 0),  time(9, 35)),
    (time(9, 50), time(11, 25)),
    (time(11, 40), time(13, 15)),
    (time(13, 30), time(15, 5)),
    (time(15, 20), time(16, 55)),
]


# ══════════════════════════════════════════════════════════════════════════════════
class Command(BaseCommand):
    help = "Заповнює базу даних реалістичними тестовими даними для всіх модулів."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистити всі дані перед заповненням (залишає суперкористувачів).",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        self.stdout.write(self.style.MIGRATE_HEADING("\n📚 Запуск seed-файлу Palamar...\n"))

        groups    = self._create_groups()
        subjects  = self._create_subjects()
        admin     = self._create_admin()
        teachers  = self._create_teachers()
        students  = self._create_students(groups)
        self._create_schedule(groups, subjects, teachers)
        self._create_grades(students, subjects, teachers)
        assignments = self._create_assignments(subjects, teachers)
        self._create_submissions(assignments, students, groups)
        self._create_attendance(students, subjects)

        self.stdout.write(self.style.SUCCESS("\n✅ Seed завершено успішно!\n"))
        self._print_summary(groups, subjects, teachers, students, assignments)

    # ─── ОЧИЩЕННЯ ────────────────────────────────────────────────────────────────

    def _clear_data(self):
        self.stdout.write("🗑  Очищення бази даних...")
        from attendance.models import Attendance
        from grades.models import Grade
        from assignments.models import Submission, Assignment
        from schedule.models import Schedule
        from accounts.models import Student, Teacher, User
        from subjects.models import Subject, Group

        Attendance.objects.all().delete()
        Submission.objects.all().delete()
        Assignment.objects.all().delete()
        Grade.objects.all().delete()
        Schedule.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Subject.objects.all().delete()
        Group.objects.all().delete()
        self.stdout.write(self.style.WARNING("  Дані очищено.\n"))

    # ─── ГРУПИ ───────────────────────────────────────────────────────────────────

    def _create_groups(self):
        from subjects.models import Group
        self.stdout.write("📁 Створення груп...")
        groups = []
        for data in GROUPS_DATA:
            group, created = Group.objects.get_or_create(
                name=data["name"],
                defaults={
                    "faculty": data["faculty"],
                    "year_formed": data["year_formed"],
                },
            )
            groups.append((group, data))
            status = "створено" if created else "вже існує"
            self.stdout.write(f"   {group.name} ({data['faculty']}) — {status}")
        return groups

    # ─── ПРЕДМЕТИ ─────────────────────────────────────────────────────────────────

    def _create_subjects(self):
        from subjects.models import Subject
        self.stdout.write("📖 Створення предметів...")
        subjects = []
        for data in SUBJECTS_DATA:
            subject, created = Subject.objects.get_or_create(
                name=data["name"],
                semester=data["semester"],
                defaults={
                    "credits": data["credits"],
                    "description": data["description"],
                },
            )
            subjects.append(subject)
            status = "створено" if created else "вже існує"
            self.stdout.write(f"   [{subject.semester} сем.] {subject.name} — {status}")
        return subjects

    # ─── АДМІНІСТРАТОР ────────────────────────────────────────────────────────────

    def _create_admin(self):
        from accounts.models import User
        self.stdout.write("👤 Створення адміністратора...")
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Адміністратор",
                "last_name": "Системи",
                "email": "admin@university.edu.ua",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "password": make_password("admin123"),
            },
        )
        if created:
            self.stdout.write(f"   admin / admin123 — створено")
        else:
            self.stdout.write(f"   admin — вже існує")
        return admin

    # ─── ВИКЛАДАЧІ ────────────────────────────────────────────────────────────────

    def _create_teachers(self):
        from accounts.models import User, Teacher
        self.stdout.write("👨‍🏫 Створення викладачів...")
        teachers = []
        for data in TEACHERS_DATA:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "role": "teacher",
                    "password": make_password("teacher123"),
                },
            )
            teacher, _ = Teacher.objects.update_or_create(  # <--- ЗМІНА ТУТ
                user=user,
                defaults={
                    "department": data["department"],
                    "academic_degree": data["academic_degree"],
                },
            )
            teachers.append(teacher)
            status = "створено" if created else "вже існує"
            self.stdout.write(
                f"   {user.last_name} {user.first_name} — {data['department']} — {status}"
            )
        return teachers

    # ─── СТУДЕНТИ ─────────────────────────────────────────────────────────────────

    def _create_students(self, groups):
        from accounts.models import User, Student
        self.stdout.write("🎓 Створення студентів...")
        students_by_group = {}
        card_counter = 1000

        for group_obj, group_data in groups:
            group_students = []
            students_by_group[group_obj.name] = group_students

            # 8 студентів у кожній групі (приблизно 60/40 чол/жін)
            genders = ["male"] * 5 + ["female"] * 3
            random.shuffle(genders)

            used_names = set()
            for i, gender in enumerate(genders):
                if gender == "male":
                    first = random.choice(MALE_FIRST_NAMES)
                    last  = random.choice(MALE_LAST_NAMES)
                    mid   = random.choice(MIDDLE_NAMES_MALE)
                else:
                    first = random.choice(FEMALE_FIRST_NAMES)
                    last  = random.choice(FEMALE_LAST_NAMES)
                    mid   = random.choice(MIDDLE_NAMES_FEMALE)

                # Унікальне ім'я в межах групи
                attempts = 0
                while f"{last}{first}" in used_names and attempts < 20:
                    first = random.choice(MALE_FIRST_NAMES if gender == "male" else FEMALE_FIRST_NAMES)
                    last  = random.choice(MALE_LAST_NAMES  if gender == "male" else FEMALE_LAST_NAMES)
                    attempts += 1
                used_names.add(f"{last}{first}")

                card_counter += 1
                card_no = f"{group_obj.name}-{card_counter}"
                username = f"{last.lower()[:8]}_{group_obj.name.lower()}_{i+1}"
                username = username.replace("'", "").replace(" ", "_")[:30]

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": first,
                        "last_name": last,
                        "email": f"{username}@student.university.edu.ua",
                        "role": "student",
                        "password": make_password("student123"),
                    },
                )
                student, _ = Student.objects.update_or_create(  # <--- ЗМІНА ТУТ
                    user=user,
                    defaults={
                        "group": group_obj,
                        "specialty": group_data["specialty"],
                        "year_of_study": group_data["year_of_study"],
                        "student_card_no": card_no,
                    },
                )
                group_students.append(student)

            self.stdout.write(
                f"   {group_obj.name}: {len(group_students)} студентів"
            )

        return students_by_group

    # ─── РОЗКЛАД ──────────────────────────────────────────────────────────────────

    def _create_schedule(self, groups, subjects, teachers):
        from schedule.models import Schedule
        self.stdout.write("📅 Створення розкладу...")
        created_count = 0

        # Відстежуємо зайнятість: (day, start_time) -> {teacher_ids, room, group_ids}
        occupied_teachers = {}  # (day, slot_idx) -> set of teacher ids
        occupied_rooms    = {}  # (day, slot_idx) -> set of rooms
        occupied_groups   = {}  # (day, slot_idx) -> set of group ids

        subject_map = {s.name: s for s in subjects}

        for group_obj, group_data in groups:
            group_name = group_obj.name
            subject_indices = GROUP_SUBJECTS_MAP.get(group_name, [])
            group_subjects = [subjects[i] for i in subject_indices if i < len(subjects)]

            lesson_type_cycle = (
                ["lecture", "practice", "lab", "lecture", "practice"]
            )

            day = 1  # Починаємо з понеділка
            slot_in_day = 0
            lessons_created = 0

            for subj_idx, subject in enumerate(group_subjects):
                # Кожен предмет — 2 заняття в тиждень
                for repeat in range(2):
                    lesson_type = lesson_type_cycle[(subj_idx * 2 + repeat) % len(lesson_type_cycle)]

                    # Знайти вільний слот
                    attempts = 0
                    placed = False
                    for try_day in range(day, 6):  # пн–пт
                        for try_slot in range(len(LESSON_TIMES)):
                            key = (try_day, try_slot)
                            t_set = occupied_teachers.get(key, set())
                            r_set = occupied_rooms.get(key, set())
                            g_set = occupied_groups.get(key, set())

                            # Визначаємо викладача для предмета
                            subj_data = SUBJECTS_DATA[subject_indices[subj_idx] if subj_idx < len(subject_indices) else 0]
                            teacher_idx = subj_data.get("teacher_idx", 0)
                            teacher = teachers[teacher_idx % len(teachers)]

                            if teacher.user.pk in t_set:
                                continue
                            if group_obj.pk in g_set:
                                continue

                            # Знайти вільну аудиторію
                            room = None
                            for r in ROOMS:
                                if r not in r_set:
                                    # Для лаб — комп. зали
                                    if lesson_type == "lab" and not r.startswith("Комп"):
                                        if r not in ("Комп-1", "Комп-2"):
                                            continue
                                    room = r
                                    break
                            if room is None:
                                # будь-яка кімната
                                for r in ROOMS:
                                    if r not in r_set:
                                        room = r
                                        break
                            if room is None:
                                continue

                            # Створюємо заняття
                            start_t, end_t = LESSON_TIMES[try_slot]
                            schedule_entry, cr = Schedule.objects.get_or_create(
                                subject=subject,
                                group=group_obj,
                                day_of_week=try_day,
                                start_time=start_t,
                                defaults={
                                    "teacher": teacher,
                                    "end_time": end_t,
                                    "room": room,
                                    "lesson_type": lesson_type,
                                },
                            )
                            if cr:
                                created_count += 1
                                occupied_teachers.setdefault(key, set()).add(teacher.user.pk)
                                occupied_rooms.setdefault(key, set()).add(room)
                                occupied_groups.setdefault(key, set()).add(group_obj.pk)

                            placed = True
                            day = try_day
                            slot_in_day = try_slot
                            break
                        if placed:
                            break

        self.stdout.write(f"   Створено {created_count} занять у розкладі")

    # ─── ОЦІНКИ ───────────────────────────────────────────────────────────────────

    def _create_grades(self, students_by_group, subjects, teachers):
        from grades.models import Grade
        self.stdout.write("📊 Виставлення оцінок...")
        total = 0

        today = date.today()
        semester_start = today - timedelta(days=90)

        for group_name, group_students in students_by_group.items():
            subject_indices = GROUP_SUBJECTS_MAP.get(group_name, [])
            group_subjects = [subjects[i] for i in subject_indices if i < len(subjects)]

            for student in group_students:
                for subject in group_subjects:
                    subj_data_idx = next(
                        (i for i, s in enumerate(SUBJECTS_DATA) if s["name"] == subject.name), 0
                    )
                    teacher = teachers[SUBJECTS_DATA[subj_data_idx]["teacher_idx"] % len(teachers)]

                    # --- Поточні оцінки (4–6 за семестр) ---
                    num_current = random.randint(4, 6)
                    for j in range(num_current):
                        grade_date = semester_start + timedelta(
                            days=random.randint(0, 85)
                        )
                        # Реалістичний розподіл: більше оцінок 70–95
                        value = self._realistic_grade()
                        comment = random.choice(
                            GRADE_COMMENTS_POSITIVE if value >= 70 else GRADE_COMMENTS_NEGATIVE
                        )
                        Grade.objects.get_or_create(
                            student=student,
                            subject=subject,
                            teacher=teacher,
                            type="current",
                            date=grade_date,
                            defaults={"value": value, "comment": comment},
                        )
                        total += 1

                    # --- Модульна (1–2 за семестр) ---
                    for j in range(random.randint(1, 2)):
                        grade_date = semester_start + timedelta(days=random.randint(30, 75))
                        value = self._realistic_grade(mu=72, sigma=12)
                        comment = random.choice(GRADE_COMMENTS_POSITIVE if value >= 70 else GRADE_COMMENTS_NEGATIVE)
                        Grade.objects.get_or_create(
                            student=student,
                            subject=subject,
                            teacher=teacher,
                            type="module",
                            date=grade_date,
                            defaults={"value": value, "comment": comment},
                        )
                        total += 1

                    # --- Іспит або залік (1 на предмет) ---
                    if random.random() < 0.75:  # 75% студентів вже здали
                        exam_type = "exam" if subject.credits >= 5 else "credit"
                        exam_date = today - timedelta(days=random.randint(1, 14))
                        value = self._realistic_grade(mu=74, sigma=14)
                        comment = random.choice(GRADE_COMMENTS_POSITIVE if value >= 60 else GRADE_COMMENTS_NEGATIVE)
                        Grade.objects.get_or_create(
                            student=student,
                            subject=subject,
                            teacher=teacher,
                            type=exam_type,
                            date=exam_date,
                            defaults={"value": value, "comment": comment},
                        )
                        total += 1

        self.stdout.write(f"   Виставлено {total} оцінок")

    def _realistic_grade(self, mu=78, sigma=13):
        """Нормально розподілена оцінка 40–100, правильно округлена."""
        value = int(random.gauss(mu, sigma))
        return max(40, min(100, value))

    # ─── ЗАВДАННЯ ─────────────────────────────────────────────────────────────────

    def _create_assignments(self, subjects, teachers):
        from assignments.models import Assignment
        self.stdout.write("📝 Створення завдань...")
        assignments = {}
        total = 0

        today = date.today()

        for subject in subjects:
            templates = ASSIGNMENT_TEMPLATES.get(subject.name, ASSIGNMENT_TEMPLATES["DEFAULT"])
            subj_data_idx = next(
                (i for i, s in enumerate(SUBJECTS_DATA) if s["name"] == subject.name), 0
            )
            teacher = teachers[SUBJECTS_DATA[subj_data_idx]["teacher_idx"] % len(teachers)]
            subject_assignments = []

            for tmpl_idx, tmpl in enumerate(templates):
                # Дедлайни: перше — вже минуло, решта — в майбутньому або близько
                if tmpl_idx == 0:
                    deadline = today - timedelta(days=random.randint(10, 30))
                elif tmpl_idx == 1:
                    deadline = today + timedelta(days=random.randint(3, 14))
                else:
                    deadline = today + timedelta(days=random.randint(15, 45))

                deadline_dt = timezone.make_aware(
                    datetime.combine(deadline, time(23, 59, 0))
                )

                assignment, created = Assignment.objects.get_or_create(
                    subject=subject,
                    teacher=teacher,
                    title=tmpl["title"],
                    defaults={
                        "description": tmpl["description"],
                        "deadline": deadline_dt,
                        "max_score": 100,
                    },
                )
                subject_assignments.append(assignment)
                if created:
                    total += 1

            assignments[subject.pk] = subject_assignments

        self.stdout.write(f"   Створено {total} завдань")
        return assignments

    # ─── ЗДАНІ РОБОТИ ─────────────────────────────────────────────────────────────

    def _create_submissions(self, assignments, students_by_group, groups):
        from assignments.models import Submission
        self.stdout.write("📤 Створення зданих робіт...")
        total = 0
        today = timezone.now()

        for group_obj, group_data in groups:
            group_name = group_obj.name
            group_students = students_by_group.get(group_name, [])
            subject_indices = GROUP_SUBJECTS_MAP.get(group_name, [])

            for subj_idx in subject_indices:
                if subj_idx >= len(SUBJECTS_DATA):
                    continue
                from subjects.models import Subject
                try:
                    subj_name = SUBJECTS_DATA[subj_idx]["name"]
                    subj_semester = SUBJECTS_DATA[subj_idx]["semester"]
                    subject = Subject.objects.get(name=subj_name, semester=subj_semester)
                except Subject.DoesNotExist:
                    continue

                subject_assignments = assignments.get(subject.pk, [])

                for assignment in subject_assignments:
                    deadline_passed = assignment.deadline < today

                    for student in group_students:
                        # Не всі студенти здали всі роботи
                        if deadline_passed:
                            # Минулий дедлайн: 85% здали
                            if random.random() > 0.85:
                                continue
                            status = random.choices(
                                ["submitted", "checked"],
                                weights=[20, 80],
                            )[0]
                        else:
                            # Майбутній дедлайн: 40% вже здали
                            if random.random() > 0.40:
                                continue
                            status = "submitted"

                        score = None
                        if status == "checked":
                            score = self._realistic_grade(mu=76, sigma=13)

                        # Текстові відповіді (без реальних файлів)
                        text_answers = [
                            f"Виконана робота з предмету '{subject.name}'. Завдання виконано відповідно до вимог.\n\nВикористані методи: аналіз задачі, розробка алгоритму, реалізація, тестування.\n\nВисновок: завдання виконано повністю.",
                            f"Лабораторна робота виконана. Всі пункти завдання реалізовано.\n\nРезультати відповідають очікуваним. Код протестований на крайових випадках.",
                            f"Домашнє завдання з '{subject.name}' виконане в повному обсязі. Відповіді на всі питання наведено нижче.",
                        ]

                        _, created = Submission.objects.get_or_create(
                            assignment=assignment,
                            student=student,
                            defaults={
                                "text_answer": random.choice(text_answers),
                                "status": status,
                                "score": score,
                            },
                        )
                        if created:
                            total += 1

        self.stdout.write(f"   Створено {total} зданих робіт")

    # ─── ВІДВІДУВАНІСТЬ ───────────────────────────────────────────────────────────

    def _create_attendance(self, students_by_group, subjects):
        from attendance.models import Attendance
        self.stdout.write("✅ Заповнення відвідуваності...")
        total = 0
        today = date.today()

        # Генеруємо навчальні дні (пн–пт) за останні 60 днів
        school_days = []
        for i in range(60, 0, -1):
            d = today - timedelta(days=i)
            if d.weekday() < 5:  # пн–пт
                school_days.append(d)

        for group_name, group_students in students_by_group.items():
            subject_indices = GROUP_SUBJECTS_MAP.get(group_name, [])
            group_subjects = [subjects[i] for i in subject_indices if i < len(subjects)]

            for student in group_students:
                # Базовий відсоток відвідуваності для студента (75–98%)
                base_attendance = random.uniform(0.75, 0.98)

                for subject in group_subjects:
                    # 2 заняття на тиждень = приблизно 17 занять за 60 днів
                    subject_days = random.sample(
                        school_days, min(17, len(school_days))
                    )
                    subject_days.sort()

                    for lesson_date in subject_days:
                        is_present = random.random() < base_attendance
                        reason = None
                        if not is_present:
                            reason = random.choice(ABSENCE_REASONS)

                        _, created = Attendance.objects.get_or_create(
                            student=student,
                            subject=subject,
                            date=lesson_date,
                            defaults={
                                "is_present": is_present,
                                "reason": reason,
                            },
                        )
                        if created:
                            total += 1

        self.stdout.write(f"   Додано {total} записів відвідуваності")

    # ─── ПІДСУМОК ─────────────────────────────────────────────────────────────────

    def _print_summary(self, groups, subjects, teachers, students, assignments):
        from grades.models import Grade
        from assignments.models import Submission, Assignment
        from attendance.models import Attendance
        from schedule.models import Schedule

        total_students = sum(len(v) for v in students.values())
        total_assignments = sum(len(v) for v in assignments.values())

        self.stdout.write("\n" + "═" * 55)
        self.stdout.write(self.style.SUCCESS("  ПІДСУМОК SEED-ФАЙЛУ"))
        self.stdout.write("═" * 55)
        self.stdout.write(f"  👥 Викладачів:            {len(teachers)}")
        self.stdout.write(f"  🏫 Груп:                  {len(groups)}")
        self.stdout.write(f"  📖 Предметів:             {len(subjects)}")
        self.stdout.write(f"  🎓 Студентів:             {total_students}")
        self.stdout.write(f"  📅 Занять у розкладі:     {Schedule.objects.count()}")
        self.stdout.write(f"  📊 Оцінок:                {Grade.objects.count()}")
        self.stdout.write(f"  📝 Завдань:               {total_assignments}")
        self.stdout.write(f"  📤 Зданих робіт:          {Submission.objects.count()}")
        self.stdout.write(f"  ✅ Записів відвідуваності: {Attendance.objects.count()}")
        self.stdout.write("═" * 55)
        self.stdout.write("\n  🔑 Облікові дані:")
        self.stdout.write("     admin        → admin123")
        self.stdout.write("     kovalchuk_v  → teacher123")
        self.stdout.write("     (усі викладачі → teacher123)")
        self.stdout.write("     (усі студенти  → student123)")
        self.stdout.write("═" * 55 + "\n")