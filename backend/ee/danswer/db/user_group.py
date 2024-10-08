from collections.abc import Sequence
from operator import and_
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session

from danswer.db.connector_credential_pair import get_connector_credential_pair_from_id
from danswer.db.enums import ConnectorCredentialPairStatus
from danswer.db.models import ConnectorCredentialPair
from danswer.db.models import Credential__UserGroup
from danswer.db.models import Document
from danswer.db.models import DocumentByConnectorCredentialPair
from danswer.db.models import LLMProvider__UserGroup
from danswer.db.models import TokenRateLimit__UserGroup
from danswer.db.models import User
from danswer.db.models import User__UserGroup
from danswer.db.models import UserGroup
from danswer.db.models import UserGroup__ConnectorCredentialPair
from danswer.db.models import UserRole
from danswer.db.users import fetch_user_by_id
from danswer.utils.logger import setup_logger
from ee.danswer.server.user_group.models import SetCuratorRequest
from ee.danswer.server.user_group.models import UserGroupCreate
from ee.danswer.server.user_group.models import UserGroupUpdate

logger = setup_logger()


def fetch_user_group(db_session: Session, user_group_id: int) -> UserGroup | None:
    stmt = select(UserGroup).where(UserGroup.id == user_group_id)
    return db_session.scalar(stmt)


def fetch_user_groups(
    db_session: Session, only_current: bool = True
) -> Sequence[UserGroup]:
    stmt = select(UserGroup)
    if only_current:
        stmt = stmt.where(UserGroup.is_up_to_date == True)  # noqa: E712
    return db_session.scalars(stmt).all()


def fetch_user_groups_for_user(
    db_session: Session, user_id: UUID, only_curator_groups: bool = False
) -> Sequence[UserGroup]:
    stmt = (
        select(UserGroup)
        .join(User__UserGroup, User__UserGroup.user_group_id == UserGroup.id)
        .join(User, User.id == User__UserGroup.user_id)  # type: ignore
        .where(User.id == user_id)  # type: ignore
    )
    if only_curator_groups:
        stmt = stmt.where(User__UserGroup.is_curator == True)  # noqa: E712
    return db_session.scalars(stmt).all()


def fetch_documents_for_user_group_paginated(
    db_session: Session,
    user_group_id: int,
    last_document_id: str | None = None,
    limit: int = 100,
) -> tuple[Sequence[Document], str | None]:
    stmt = (
        select(Document)
        .join(
            DocumentByConnectorCredentialPair,
            Document.id == DocumentByConnectorCredentialPair.id,
        )
        .join(
            ConnectorCredentialPair,
            and_(
                DocumentByConnectorCredentialPair.connector_id
                == ConnectorCredentialPair.connector_id,
                DocumentByConnectorCredentialPair.credential_id
                == ConnectorCredentialPair.credential_id,
            ),
        )
        .join(
            UserGroup__ConnectorCredentialPair,
            UserGroup__ConnectorCredentialPair.cc_pair_id == ConnectorCredentialPair.id,
        )
        .join(
            UserGroup,
            UserGroup__ConnectorCredentialPair.user_group_id == UserGroup.id,
        )
        .where(UserGroup.id == user_group_id)
        .order_by(Document.id)
        .limit(limit)
    )
    if last_document_id is not None:
        stmt = stmt.where(Document.id > last_document_id)
    stmt = stmt.distinct()

    documents = db_session.scalars(stmt).all()
    return documents, documents[-1].id if documents else None


def fetch_user_groups_for_documents(
    db_session: Session,
    document_ids: list[str],
) -> Sequence[tuple[int, list[str]]]:
    stmt = (
        select(Document.id, func.array_agg(UserGroup.name))
        .join(
            UserGroup__ConnectorCredentialPair,
            UserGroup.id == UserGroup__ConnectorCredentialPair.user_group_id,
        )
        .join(
            ConnectorCredentialPair,
            ConnectorCredentialPair.id == UserGroup__ConnectorCredentialPair.cc_pair_id,
        )
        .join(
            DocumentByConnectorCredentialPair,
            and_(
                DocumentByConnectorCredentialPair.connector_id
                == ConnectorCredentialPair.connector_id,
                DocumentByConnectorCredentialPair.credential_id
                == ConnectorCredentialPair.credential_id,
            ),
        )
        .join(Document, Document.id == DocumentByConnectorCredentialPair.id)
        .where(Document.id.in_(document_ids))
        .where(UserGroup__ConnectorCredentialPair.is_current == True)  # noqa: E712
        # don't include CC pairs that are being deleted
        # NOTE: CC pairs can never go from DELETING to any other state -> it's safe to ignore them
        .where(ConnectorCredentialPair.status != ConnectorCredentialPairStatus.DELETING)
        .group_by(Document.id)
    )

    return db_session.execute(stmt).all()  # type: ignore


def _check_user_group_is_modifiable(user_group: UserGroup) -> None:
    if not user_group.is_up_to_date:
        raise ValueError(
            "Specified user group is currently syncing. Wait until the current "
            "sync has finished before editing."
        )


def _add_user__user_group_relationships__no_commit(
    db_session: Session, user_group_id: int, user_ids: list[UUID]
) -> list[User__UserGroup]:
    """NOTE: does not commit the transaction."""
    relationships = [
        User__UserGroup(user_id=user_id, user_group_id=user_group_id)
        for user_id in user_ids
    ]
    db_session.add_all(relationships)
    return relationships


def _add_user_group__cc_pair_relationships__no_commit(
    db_session: Session, user_group_id: int, cc_pair_ids: list[int]
) -> list[UserGroup__ConnectorCredentialPair]:
    """NOTE: does not commit the transaction."""
    relationships = [
        UserGroup__ConnectorCredentialPair(
            user_group_id=user_group_id, cc_pair_id=cc_pair_id
        )
        for cc_pair_id in cc_pair_ids
    ]
    db_session.add_all(relationships)
    return relationships


def insert_user_group(db_session: Session, user_group: UserGroupCreate) -> UserGroup:
    db_user_group = UserGroup(name=user_group.name)
    db_session.add(db_user_group)
    db_session.flush()  # give the group an ID

    _add_user__user_group_relationships__no_commit(
        db_session=db_session,
        user_group_id=db_user_group.id,
        user_ids=user_group.user_ids,
    )
    _add_user_group__cc_pair_relationships__no_commit(
        db_session=db_session,
        user_group_id=db_user_group.id,
        cc_pair_ids=user_group.cc_pair_ids,
    )

    db_session.commit()
    return db_user_group


def _cleanup_user__user_group_relationships__no_commit(
    db_session: Session,
    user_group_id: int,
    user_ids: list[UUID] | None = None,
) -> None:
    """NOTE: does not commit the transaction."""
    where_clause = User__UserGroup.user_group_id == user_group_id
    if user_ids:
        where_clause &= User__UserGroup.user_id.in_(user_ids)

    user__user_group_relationships = db_session.scalars(
        select(User__UserGroup).where(where_clause)
    ).all()
    for user__user_group_relationship in user__user_group_relationships:
        db_session.delete(user__user_group_relationship)


def _cleanup_credential__user_group_relationships__no_commit(
    db_session: Session,
    user_group_id: int,
) -> None:
    """NOTE: does not commit the transaction."""
    db_session.query(Credential__UserGroup).filter(
        Credential__UserGroup.user_group_id == user_group_id
    ).delete(synchronize_session=False)


def _cleanup_llm_provider__user_group_relationships__no_commit(
    db_session: Session, user_group_id: int
) -> None:
    """NOTE: does not commit the transaction."""
    db_session.query(LLMProvider__UserGroup).filter(
        LLMProvider__UserGroup.user_group_id == user_group_id
    ).delete(synchronize_session=False)


def _mark_user_group__cc_pair_relationships_outdated__no_commit(
    db_session: Session, user_group_id: int
) -> None:
    """NOTE: does not commit the transaction."""
    user_group__cc_pair_relationships = db_session.scalars(
        select(UserGroup__ConnectorCredentialPair).where(
            UserGroup__ConnectorCredentialPair.user_group_id == user_group_id
        )
    )
    for user_group__cc_pair_relationship in user_group__cc_pair_relationships:
        user_group__cc_pair_relationship.is_current = False


def _validate_curator_status__no_commit(
    db_session: Session,
    users: list[User],
) -> None:
    for user in users:
        # Check if the user is a curator in any of their groups
        curator_relationships = (
            db_session.query(User__UserGroup)
            .filter(
                User__UserGroup.user_id == user.id,
                User__UserGroup.is_curator == True,  # noqa: E712
            )
            .all()
        )

        if curator_relationships:
            user.role = UserRole.CURATOR
        elif user.role == UserRole.CURATOR:
            user.role = UserRole.BASIC
        db_session.add(user)


def remove_curator_status__no_commit(db_session: Session, user: User) -> None:
    stmt = (
        update(User__UserGroup)
        .where(User__UserGroup.user_id == user.id)
        .values(is_curator=False)
    )
    db_session.execute(stmt)
    _validate_curator_status__no_commit(db_session, [user])


def update_user_curator_relationship(
    db_session: Session,
    user_group_id: int,
    set_curator_request: SetCuratorRequest,
) -> None:
    user = fetch_user_by_id(db_session, set_curator_request.user_id)
    if not user:
        raise ValueError(f"User with id '{set_curator_request.user_id}' not found")
    requested_user_groups = fetch_user_groups_for_user(
        db_session=db_session,
        user_id=set_curator_request.user_id,
        only_curator_groups=False,
    )

    group_ids = [group.id for group in requested_user_groups]
    if user_group_id not in group_ids:
        raise ValueError(f"user is not in group '{user_group_id}'")

    relationship_to_update = (
        db_session.query(User__UserGroup)
        .filter(
            User__UserGroup.user_group_id == user_group_id,
            User__UserGroup.user_id == set_curator_request.user_id,
        )
        .first()
    )

    if relationship_to_update:
        relationship_to_update.is_curator = set_curator_request.is_curator
    else:
        relationship_to_update = User__UserGroup(
            user_group_id=user_group_id,
            user_id=set_curator_request.user_id,
            is_curator=True,
        )
        db_session.add(relationship_to_update)

    _validate_curator_status__no_commit(db_session, [user])
    db_session.commit()


def update_user_group(
    db_session: Session,
    user: User | None,
    user_group_id: int,
    user_group_update: UserGroupUpdate,
) -> UserGroup:
    stmt = select(UserGroup).where(UserGroup.id == user_group_id)
    db_user_group = db_session.scalar(stmt)
    if db_user_group is None:
        raise ValueError(f"UserGroup with id '{user_group_id}' not found")

    _check_user_group_is_modifiable(db_user_group)

    current_user_ids = set([user.id for user in db_user_group.users])
    updated_user_ids = set(user_group_update.user_ids)
    added_user_ids = list(updated_user_ids - current_user_ids)
    removed_user_ids = list(current_user_ids - updated_user_ids)

    # LEAVING THIS HERE FOR NOW FOR GIVING DIFFERENT ROLES
    # ACCESS TO DIFFERENT PERMISSIONS
    # if (removed_user_ids or added_user_ids) and (
    #     not user or user.role != UserRole.ADMIN
    # ):
    #     raise ValueError("Only admins can add or remove users from user groups")

    if removed_user_ids:
        _cleanup_user__user_group_relationships__no_commit(
            db_session=db_session,
            user_group_id=user_group_id,
            user_ids=removed_user_ids,
        )

    if added_user_ids:
        _add_user__user_group_relationships__no_commit(
            db_session=db_session,
            user_group_id=user_group_id,
            user_ids=added_user_ids,
        )

    cc_pairs_updated = set([cc_pair.id for cc_pair in db_user_group.cc_pairs]) != set(
        user_group_update.cc_pair_ids
    )
    if cc_pairs_updated:
        _mark_user_group__cc_pair_relationships_outdated__no_commit(
            db_session=db_session, user_group_id=user_group_id
        )
        _add_user_group__cc_pair_relationships__no_commit(
            db_session=db_session,
            user_group_id=db_user_group.id,
            cc_pair_ids=user_group_update.cc_pair_ids,
        )

    # only needs to sync with Vespa if the cc_pairs have been updated
    if cc_pairs_updated:
        db_user_group.is_up_to_date = False

    removed_users = db_session.scalars(
        select(User).where(User.id.in_(removed_user_ids))  # type: ignore
    ).unique()
    _validate_curator_status__no_commit(db_session, list(removed_users))
    db_session.commit()
    return db_user_group


def _cleanup_token_rate_limit__user_group_relationships__no_commit(
    db_session: Session, user_group_id: int
) -> None:
    """NOTE: does not commit the transaction."""
    token_rate_limit__user_group_relationships = db_session.scalars(
        select(TokenRateLimit__UserGroup).where(
            TokenRateLimit__UserGroup.user_group_id == user_group_id
        )
    ).all()
    for (
        token_rate_limit__user_group_relationship
    ) in token_rate_limit__user_group_relationships:
        db_session.delete(token_rate_limit__user_group_relationship)


def prepare_user_group_for_deletion(db_session: Session, user_group_id: int) -> None:
    stmt = select(UserGroup).where(UserGroup.id == user_group_id)
    db_user_group = db_session.scalar(stmt)
    if db_user_group is None:
        raise ValueError(f"UserGroup with id '{user_group_id}' not found")

    _check_user_group_is_modifiable(db_user_group)

    _cleanup_credential__user_group_relationships__no_commit(
        db_session=db_session, user_group_id=user_group_id
    )
    _cleanup_user__user_group_relationships__no_commit(
        db_session=db_session, user_group_id=user_group_id
    )
    _mark_user_group__cc_pair_relationships_outdated__no_commit(
        db_session=db_session, user_group_id=user_group_id
    )
    _cleanup_token_rate_limit__user_group_relationships__no_commit(
        db_session=db_session, user_group_id=user_group_id
    )

    db_user_group.is_up_to_date = False
    db_user_group.is_up_for_deletion = True
    db_session.commit()


def _cleanup_user_group__cc_pair_relationships__no_commit(
    db_session: Session, user_group_id: int, outdated_only: bool
) -> None:
    """NOTE: does not commit the transaction."""
    stmt = select(UserGroup__ConnectorCredentialPair).where(
        UserGroup__ConnectorCredentialPair.user_group_id == user_group_id
    )
    if outdated_only:
        stmt = stmt.where(
            UserGroup__ConnectorCredentialPair.is_current == False  # noqa: E712
        )
    user_group__cc_pair_relationships = db_session.scalars(stmt)
    for user_group__cc_pair_relationship in user_group__cc_pair_relationships:
        db_session.delete(user_group__cc_pair_relationship)


def mark_user_group_as_synced(db_session: Session, user_group: UserGroup) -> None:
    # cleanup outdated relationships
    _cleanup_user_group__cc_pair_relationships__no_commit(
        db_session=db_session, user_group_id=user_group.id, outdated_only=True
    )
    user_group.is_up_to_date = True
    db_session.commit()


def delete_user_group(db_session: Session, user_group: UserGroup) -> None:
    _cleanup_llm_provider__user_group_relationships__no_commit(
        db_session=db_session, user_group_id=user_group.id
    )
    _cleanup_user__user_group_relationships__no_commit(
        db_session=db_session, user_group_id=user_group.id
    )
    _cleanup_user_group__cc_pair_relationships__no_commit(
        db_session=db_session,
        user_group_id=user_group.id,
        outdated_only=False,
    )

    # need to flush so that we don't get a foreign key error when deleting the user group row
    db_session.flush()

    db_session.delete(user_group)
    db_session.commit()


def delete_user_group_cc_pair_relationship__no_commit(
    cc_pair_id: int, db_session: Session
) -> None:
    """Deletes all rows from UserGroup__ConnectorCredentialPair where the
    connector_credential_pair_id matches the given cc_pair_id.

    Should be used very carefully (only for connectors that are being deleted)."""
    cc_pair = get_connector_credential_pair_from_id(cc_pair_id, db_session)
    if not cc_pair:
        raise ValueError(f"Connector Credential Pair '{cc_pair_id}' does not exist")

    if cc_pair.status != ConnectorCredentialPairStatus.DELETING:
        raise ValueError(
            f"Connector Credential Pair '{cc_pair_id}' is not in the DELETING state"
        )

    delete_stmt = delete(UserGroup__ConnectorCredentialPair).where(
        UserGroup__ConnectorCredentialPair.cc_pair_id == cc_pair_id,
    )
    db_session.execute(delete_stmt)
