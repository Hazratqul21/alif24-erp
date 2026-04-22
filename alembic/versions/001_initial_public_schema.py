"""initial public schema

Revision ID: 001_initial_public
Revises:
Create Date: 2026-04-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_public'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── PUBLIC SCHEMA TABLES ────────────────────────────────────────────────

    # super_admins
    op.execute("CREATE SCHEMA IF NOT EXISTS public")
    op.create_table(
        'super_admins',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='public',
    )

    # plans
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('price_monthly', sa.Numeric(12, 2), default=0),
        sa.Column('price_yearly', sa.Numeric(12, 2), default=0),
        sa.Column('max_users', sa.Integer(), default=100),
        sa.Column('max_students', sa.Integer(), default=500),
        sa.Column('max_teachers', sa.Integer(), default=50),
        sa.Column('has_library', sa.Boolean(), default=True),
        sa.Column('has_transport', sa.Boolean(), default=False),
        sa.Column('has_canteen', sa.Boolean(), default=False),
        sa.Column('has_medical', sa.Boolean(), default=True),
        sa.Column('has_psychology', sa.Boolean(), default=False),
        sa.Column('has_interlibrary', sa.Boolean(), default=False),
        sa.Column('has_competitions', sa.Boolean(), default=True),
        sa.Column('has_portfolio', sa.Boolean(), default=False),
        sa.Column('has_surveys', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='public',
    )

    # central_books
    op.create_table(
        'central_books',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('isbn', sa.String(20), unique=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('author', sa.String(300), nullable=False),
        sa.Column('publisher', sa.String(300)),
        sa.Column('year', sa.Integer()),
        sa.Column('genre', sa.String(100)),
        sa.Column('language', sa.String(50), default='uz'),
        sa.Column('pages', sa.Integer()),
        sa.Column('description', sa.Text()),
        sa.Column('cover_image', sa.String(500)),
        sa.Column('added_by_tenant', sa.Integer()),
        sa.Column('added_by_user', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='public',
    )

    # tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('domain', sa.String(200), unique=True),
        sa.Column('schema_name', sa.String(100), unique=True, nullable=False),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('public.plans.id', ondelete='SET NULL')),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_blocked', sa.Boolean(), default=False),
        sa.Column('subscription_end', sa.Date()),
        sa.Column('admin_email', sa.String(255)),
        sa.Column('admin_phone', sa.String(30)),
        sa.Column('address', sa.Text()),
        sa.Column('region', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='public',
    )

    # ─── TENANT SCHEMA TABLES ────────────────────────────────────────────────

    # users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True),
        sa.Column('phone', sa.String(30), unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('middle_name', sa.String(100)),
        sa.Column('gender', sa.String(10)),
        sa.Column('birth_date', sa.Date()),
        sa.Column('avatar', sa.String(500)),
        sa.Column('alif24_user_id', sa.String(20)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('refresh_token', sa.Text()),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # user_roles
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )

    # permissions
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('module', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
    )

    # role_permissions
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('allowed', sa.Boolean(), default=True),
    )

    # academic_years
    op.create_table(
        'academic_years',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_current', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # classes
    op.create_table(
        'classes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('grade_level', sa.Integer()),
        sa.Column('academic_year_id', sa.Integer(), sa.ForeignKey('academic_years.id', ondelete='SET NULL')),
        sa.Column('homeroom_teacher_id', sa.String(36)),
        sa.Column('room_number', sa.String(20)),
        sa.Column('capacity', sa.Integer(), default=30),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # students
    op.create_table(
        'students',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('student_id', sa.String(20), unique=True, nullable=False),
        sa.Column('current_class_id', sa.Integer(), sa.ForeignKey('classes.id', ondelete='SET NULL')),
        sa.Column('enrollment_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # teachers
    op.create_table(
        'teachers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('employee_id', sa.String(20), unique=True),
        sa.Column('hire_date', sa.Date()),
        sa.Column('qualification', sa.String(200)),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # parents
    op.create_table(
        'parents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('relationship_type', sa.String(30), default='parent'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # subjects
    op.create_table(
        'subjects',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(20), unique=True),
        sa.Column('grade_level', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # grades
    op.create_table(
        'grades',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject_id', sa.Integer(), sa.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('teacher_id', sa.String(36), sa.ForeignKey('teachers.id', ondelete='SET NULL')),
        sa.Column('score', sa.Numeric(5, 2), nullable=False),
        sa.Column('grade_type', sa.String(50), default='assignment'),
        sa.Column('comment', sa.Text()),
        sa.Column('graded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # attendance
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id', ondelete='SET NULL')),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('note', sa.Text()),
        sa.Column('check_in_time', sa.DateTime(timezone=True)),
        sa.Column('marked_by', sa.String(36)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('student_id', 'date', name='uq_attendance_student_date'),
    )

    # payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('parents.id', ondelete='SET NULL')),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_type', sa.String(50), nullable=False),
        sa.Column('payment_date', sa.Date()),
        sa.Column('due_date', sa.Date()),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('transaction_id', sa.String(100), unique=True),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # payment_plans
    op.create_table(
        'payment_plans',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('frequency', sa.String(20), default='monthly'),
        sa.Column('description', sa.Text()),
    )

    # fees
    op.create_table(
        'fees',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('category', sa.String(50)),
        sa.Column('is_required', sa.Integer(), default=1),
    )

    # school_books
    op.create_table(
        'school_books',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('central_book_id', sa.Integer(), nullable=False),
        sa.Column('total_copies', sa.Integer(), default=1),
        sa.Column('available_copies', sa.Integer(), default=1),
        sa.Column('location', sa.String(200)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # book_loans
    op.create_table(
        'book_loans',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('school_book_id', sa.Integer(), sa.ForeignKey('school_books.id', ondelete='CASCADE'), nullable=False),
        sa.Column('loan_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('return_date', sa.Date()),
        sa.Column('status', sa.String(20), default='borrowed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # enrollments
    op.create_table(
        'enrollments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('class_id', sa.Integer(), sa.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('academic_year_id', sa.Integer(), sa.ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enroll_date', sa.Date(), nullable=False),
        sa.Column('leave_date', sa.Date()),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('body', sa.Text()),
        sa.Column('notification_type', sa.String(50)),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ─── INSERT DEFAULT DATA ──────────────────────────────────────────────────
    op.execute("""
        INSERT INTO roles (name, description) VALUES
        ('super_admin', 'Super Administrator'),
        ('director', 'School Director'),
        ('deputy_director', 'Deputy Director'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('accountant', 'Accountant'),
        ('librarian', 'Librarian'),
        ('medical', 'Medical Staff'),
        ('hr', 'Human Resources'),
        ('receptionist', 'Receptionist'),
        ('security', 'Security Guard'),
        ('it_admin', 'IT Administrator'),
        ('psychologist', 'Psychologist')
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('enrollments')
    op.drop_table('book_loans')
    op.drop_table('school_books')
    op.drop_table('fees')
    op.drop_table('payment_plans')
    op.drop_table('payments')
    op.drop_table('attendance')
    op.drop_table('grades')
    op.drop_table('subjects')
    op.drop_table('parents')
    op.drop_table('teachers')
    op.drop_table('students')
    op.drop_table('classes')
    op.drop_table('academic_years')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('tenants', schema='public')
    op.drop_table('central_books', schema='public')
    op.drop_table('plans', schema='public')
    op.drop_table('super_admins', schema='public')
