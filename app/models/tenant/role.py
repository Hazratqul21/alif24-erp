from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    level = Column(Integer, default=0)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_roles = relationship("UserRole", back_populates="role", lazy="selectin")
    permissions = relationship("RolePermission", back_populates="role", lazy="selectin")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(20), nullable=False)
    description = Column(Text)

    role_permissions = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    allowed = Column(Boolean, default=True)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")


DEFAULT_ROLES = [
    {"name": "super_admin", "display_name": "Super Admin", "level": 0, "is_system": True},
    {"name": "director", "display_name": "Direktor", "level": 1, "is_system": True},
    {"name": "administrator", "display_name": "Administrator", "level": 2, "is_system": True},
    {"name": "deputy_academic", "display_name": "O'quv ishlari bo'yicha direktor o'rinbosari", "level": 3, "is_system": True},
    {"name": "deputy_discipline", "display_name": "Tarbiyaviy ishlar bo'yicha direktor o'rinbosari", "level": 3, "is_system": True},
    {"name": "deputy_finance", "display_name": "Moliya bo'yicha direktor o'rinbosari", "level": 3, "is_system": True},
    {"name": "class_teacher", "display_name": "Sinf rahbari", "level": 4, "is_system": True},
    {"name": "department_head", "display_name": "Fan yo'nalishi rahbari", "level": 5, "is_system": True},
    {"name": "teacher", "display_name": "O'qituvchi", "level": 6, "is_system": True},
    {"name": "student", "display_name": "O'quvchi", "level": 7, "is_system": True},
    {"name": "parent", "display_name": "Ota-ona", "level": 8, "is_system": True},
    {"name": "accountant", "display_name": "Buxgalter", "level": 9, "is_system": True},
    {"name": "medical_staff", "display_name": "Tibbiyot xodimi", "level": 10, "is_system": True},
    {"name": "psychologist", "display_name": "Psixolog", "level": 11, "is_system": True},
    {"name": "librarian", "display_name": "Kutubxonachi", "level": 12, "is_system": True},
    {"name": "it_admin", "display_name": "IT Administrator", "level": 13, "is_system": True},
    {"name": "canteen_manager", "display_name": "Oshxona mudiri", "level": 14, "is_system": True},
    {"name": "transport_manager", "display_name": "Transport bo'limi", "level": 15, "is_system": True},
    {"name": "security", "display_name": "Qo'riqchi", "level": 16, "is_system": True},
    {"name": "parent_council", "display_name": "Ota-onalar kengashi a'zosi", "level": 17, "is_system": True},
    {"name": "alumni", "display_name": "Bitiruvchi", "level": 18, "is_system": True},
]

DEFAULT_PERMISSIONS = [
    # Users module
    {"name": "users.view", "module": "users", "action": "view"},
    {"name": "users.create", "module": "users", "action": "create"},
    {"name": "users.edit", "module": "users", "action": "edit"},
    {"name": "users.delete", "module": "users", "action": "delete"},
    # Attendance
    {"name": "attendance.view", "module": "attendance", "action": "view"},
    {"name": "attendance.create", "module": "attendance", "action": "create"},
    {"name": "attendance.edit", "module": "attendance", "action": "edit"},
    {"name": "attendance.delete", "module": "attendance", "action": "delete"},
    # Schedule
    {"name": "schedule.view", "module": "schedule", "action": "view"},
    {"name": "schedule.create", "module": "schedule", "action": "create"},
    {"name": "schedule.edit", "module": "schedule", "action": "edit"},
    {"name": "schedule.delete", "module": "schedule", "action": "delete"},
    # Grades
    {"name": "grades.view", "module": "grades", "action": "view"},
    {"name": "grades.create", "module": "grades", "action": "create"},
    {"name": "grades.edit", "module": "grades", "action": "edit"},
    {"name": "grades.delete", "module": "grades", "action": "delete"},
    # Payments
    {"name": "payments.view", "module": "payments", "action": "view"},
    {"name": "payments.create", "module": "payments", "action": "create"},
    {"name": "payments.edit", "module": "payments", "action": "edit"},
    {"name": "payments.delete", "module": "payments", "action": "delete"},
    # Library
    {"name": "library.view", "module": "library", "action": "view"},
    {"name": "library.create", "module": "library", "action": "create"},
    {"name": "library.edit", "module": "library", "action": "edit"},
    {"name": "library.delete", "module": "library", "action": "delete"},
    # Medical
    {"name": "medical.view", "module": "medical", "action": "view"},
    {"name": "medical.create", "module": "medical", "action": "create"},
    {"name": "medical.edit", "module": "medical", "action": "edit"},
    {"name": "medical.delete", "module": "medical", "action": "delete"},
    # Psychology
    {"name": "psychology.view", "module": "psychology", "action": "view"},
    {"name": "psychology.create", "module": "psychology", "action": "create"},
    {"name": "psychology.edit", "module": "psychology", "action": "edit"},
    {"name": "psychology.delete", "module": "psychology", "action": "delete"},
    # Canteen
    {"name": "canteen.view", "module": "canteen", "action": "view"},
    {"name": "canteen.create", "module": "canteen", "action": "create"},
    {"name": "canteen.edit", "module": "canteen", "action": "edit"},
    {"name": "canteen.delete", "module": "canteen", "action": "delete"},
    # Transport
    {"name": "transport.view", "module": "transport", "action": "view"},
    {"name": "transport.create", "module": "transport", "action": "create"},
    {"name": "transport.edit", "module": "transport", "action": "edit"},
    {"name": "transport.delete", "module": "transport", "action": "delete"},
    # Documents
    {"name": "documents.view", "module": "documents", "action": "view"},
    {"name": "documents.create", "module": "documents", "action": "create"},
    {"name": "documents.edit", "module": "documents", "action": "edit"},
    {"name": "documents.delete", "module": "documents", "action": "delete"},
    # Competitions
    {"name": "competitions.view", "module": "competitions", "action": "view"},
    {"name": "competitions.create", "module": "competitions", "action": "create"},
    {"name": "competitions.edit", "module": "competitions", "action": "edit"},
    {"name": "competitions.delete", "module": "competitions", "action": "delete"},
    # Rooms
    {"name": "rooms.view", "module": "rooms", "action": "view"},
    {"name": "rooms.create", "module": "rooms", "action": "create"},
    {"name": "rooms.edit", "module": "rooms", "action": "edit"},
    {"name": "rooms.delete", "module": "rooms", "action": "delete"},
    # Reports
    {"name": "reports.view", "module": "reports", "action": "view"},
    {"name": "reports.export", "module": "reports", "action": "export"},
    # Audit
    {"name": "audit.view", "module": "audit", "action": "view"},
    # Students
    {"name": "students.view", "module": "students", "action": "view"},
    {"name": "students.create", "module": "students", "action": "create"},
    {"name": "students.edit", "module": "students", "action": "edit"},
    {"name": "students.delete", "module": "students", "action": "delete"},
    # Teachers
    {"name": "teachers.view", "module": "teachers", "action": "view"},
    {"name": "teachers.create", "module": "teachers", "action": "create"},
    {"name": "teachers.edit", "module": "teachers", "action": "edit"},
    {"name": "teachers.delete", "module": "teachers", "action": "delete"},
    # Parents
    {"name": "parents.view", "module": "parents", "action": "view"},
    {"name": "parents.create", "module": "parents", "action": "create"},
    {"name": "parents.edit", "module": "parents", "action": "edit"},
    # Exams & Homework
    {"name": "exams.view", "module": "exams", "action": "view"},
    {"name": "exams.create", "module": "exams", "action": "create"},
    {"name": "exams.edit", "module": "exams", "action": "edit"},
    {"name": "exams.delete", "module": "exams", "action": "delete"},
    {"name": "homework.view", "module": "homework", "action": "view"},
    {"name": "homework.create", "module": "homework", "action": "create"},
    {"name": "homework.edit", "module": "homework", "action": "edit"},
    {"name": "homework.delete", "module": "homework", "action": "delete"},
    # Admissions
    {"name": "admissions.view", "module": "admissions", "action": "view"},
    {"name": "admissions.create", "module": "admissions", "action": "create"},
    {"name": "admissions.edit", "module": "admissions", "action": "edit"},
    # Portfolio
    {"name": "portfolio.view", "module": "portfolio", "action": "view"},
    {"name": "portfolio.create", "module": "portfolio", "action": "create"},
    {"name": "portfolio.edit", "module": "portfolio", "action": "edit"},
    # Surveys
    {"name": "surveys.view", "module": "surveys", "action": "view"},
    {"name": "surveys.create", "module": "surveys", "action": "create"},
    {"name": "surveys.edit", "module": "surveys", "action": "edit"},
    # Notifications
    {"name": "notifications.view", "module": "notifications", "action": "view"},
    {"name": "notifications.create", "module": "notifications", "action": "create"},
    # Discipline
    {"name": "discipline.view", "module": "discipline", "action": "view"},
    {"name": "discipline.create", "module": "discipline", "action": "create"},
    {"name": "discipline.edit", "module": "discipline", "action": "edit"},
    # Holidays
    {"name": "holidays.view", "module": "holidays", "action": "view"},
    {"name": "holidays.create", "module": "holidays", "action": "create"},
    {"name": "holidays.edit", "module": "holidays", "action": "edit"},
    {"name": "holidays.delete", "module": "holidays", "action": "delete"},
]
