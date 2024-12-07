import uuid
from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ocrworker.db.base import Base

CType = Literal["document", "folder"]


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, insert_default=uuid.uuid4()
    )
    title: Mapped[str] = mapped_column(String(200))
    ctype: Mapped[CType] = mapped_column(insert_default="document")
    lang: Mapped[str] = mapped_column(String(8))
    tags: list[str] = []
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        "node_id",
        ForeignKey("nodes.id"),
        primary_key=True,
        insert_default=uuid.uuid4(),
    )
    ctype: Mapped[CType] = mapped_column(insert_default="document")
    title: Mapped[str] = mapped_column(String(200))
    # actually `lang` attribute should be part of the document
    lang: Mapped[str] = mapped_column(String(8))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    number: Mapped[int]
    lang: Mapped[str]
    file_name: Mapped[str]
    size: Mapped[int] = mapped_column(insert_default=0)
    page_count: Mapped[int]
    text: Mapped[str] = mapped_column(insert_default="")
    short_description: Mapped[str] = mapped_column(insert_default="")
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.node_id"))


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    number: Mapped[int]
    lang: Mapped[str] = mapped_column(insert_default="en")
    text: Mapped[str] = mapped_column(insert_default="")
    page_count: Mapped[int]

    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, insert_default=uuid.uuid4()
    )
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    first_name: Mapped[str] = mapped_column(default=" ")
    last_name: Mapped[str] = mapped_column(default=" ")
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    date_joined: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )
