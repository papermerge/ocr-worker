import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column
from ocrworker.db.base import Base


class Document(Base):
    __tablename__ = "core_document"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        insert_default=uuid.uuid4()
    )
    title: Mapped[str] = mapped_column(String(200))
    # actually `lang` attribute should be part of the document
    lang: Mapped[str] = mapped_column(String(8))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("core_user.id"))
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now()
    )

    __mapper_args__ = {
        "polymorphic_identity": "document",
    }


class DocumentVersion(Base):
    __tablename__ = "core_documentversion"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    number: Mapped[int]
    file_name: Mapped[str]
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("core_document.basetreenode_ptr_id")
    )


class Page(Base):
    __tablename__ = "core_page"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    number: Mapped[int]
    lang: Mapped[str] = mapped_column(
        insert_default='en'
    )
    text: Mapped[str] = mapped_column(
        insert_default=''
    )
    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("core_documentversion.id")
    )


class User(Base):
    __tablename__ = "core_user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        insert_default=uuid.uuid4()
    )
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    first_name: Mapped[str] = mapped_column(default=' ')
    last_name: Mapped[str] = mapped_column(default=' ')
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    date_joined: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now()
    )


