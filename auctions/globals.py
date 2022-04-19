import stripe
from essential_generators import DocumentGenerator

# STRIPE PAYMENT VALUES
# stripe public key: 'pk_test_51KpzPvJhMiuLwzG6ikPeT4xruXBkU43RqykksSfTX5BlphCecxPl8JL9xt7mrfm1rmYip7T3m7VEOL09DMa5nZ3p001CjRiksn'
stripe.api_key = 'sk_test_51KpzPvJhMiuLwzG6CYjat9cTVFCWAjRopTymyPyH32XKY3JZb7wwkvoFpUnRlJn3gM8BHVwVFfrBWdEjE351u0Ta008sFt5jT1'
STRIPE_ALLOWED_SHIPPING_COUNTRIES = {'allowed_countries': ['US', 'CA']}


LISTING_EXPIRATION_DAYS = 14        # global value for how long listings are active
LISTING_DRAFT_EXPIRATION_DAYS = 30  
LISTING_DRAFT_CAP = 10              # Cap on the number of listing drafts per user
GEN = DocumentGenerator()

# Images
# Thumbnail size
THUMBNAIL_SIZE = (100, 100)
MAX_UPLOADS_PER_LISTING = 10
MIN_UPLOADS_PER_LISTING = 1

# Notification styling
ICON_DANGER = 'exclamation-octagon'
ICON_WARNING = 'exclamation-triangle'
ICON_SUCCESS = 'check'
ICON_GENERIC = 'info-circle'
TYPE_INFO = 'info'
TYPE_DANGER = 'danger'
TYPE_WARNING = 'warning'
TYPE_SUCCESS = 'success'


# Form Modes
LISTING_FORM_CREATE_NEW = "create"
LISTING_FORM_PREVIEW = "preview"
LISTING_FORM_EDIT = "edit"