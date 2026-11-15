from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Url
from app.shortcode import generate_code

MAX_CODE_ATTEMPTS = 5


def create_url(db: Session, target_url: str) -> Url:
    for _ in range(MAX_CODE_ATTEMPTS):
        code = generate_code(settings.short_code_length)
        url = Url(code=code, target_url=target_url)
        db.add(url)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(url)
        return url
    raise RuntimeError("Failed to generate a unique short code")


def get_url_by_code(db: Session, code: str) -> Url | None:
    return db.query(Url).filter(Url.code == code).first()
