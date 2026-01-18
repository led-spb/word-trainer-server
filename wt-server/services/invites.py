from ..models import db
from ..models.user import Invite



class InvitesService:

    @classmethod
    def invite_is_valid(cls, invite_hash: str) -> bool:
        invite = db.session.execute(
            db.select(
                Invite
            ).filter(
                Invite.hash == invite_hash
            )
        ).scalar_one_or_none()

        return invite is not None and invite.registered_user_id is None