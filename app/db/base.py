# Import all models here so Alembic's autogenerate can discover them
# through Base.metadata. This module has no other purpose.

from app.db.database import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_profile import UserProfile  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.order_item import OrderItem  # noqa: F401
