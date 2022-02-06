from essential_generators import DocumentGenerator

LISTING_EXPIRATION_DAYS = 14        # global value for how long listings are active
GEN = DocumentGenerator()

# Images
# Thumbnail size
THUMBNAIL_SIZE = (100, 100)
MAX_UPLOADS_PER_LISTING = 10

# Notification styling
ICON_DANGER = 'exclamation-octagon'
ICON_WARNING = 'exclamation-triangle'
ICON_SUCCESS = 'check'
ICON_GENERIC = 'info-circle'
TYPE_INFO = 'info'
TYPE_DANGER = 'danger'
TYPE_WARNING = 'warning'
TYPE_SUCCESS = 'success'

# AJAX variables
AJAX_DELETE_COMMENT = "delete_comment"
AJAX_DISMISS_NOTIFICATION = "dismiss_notification"
AJAX_GENERATE_COMMENT = "generate_comment"
AJAX_GENERATE_USER = "generate_user"
AJAX_PURGE_MEDIA = "purge_media"
AJAX_REPLY_COMMENT = "reply_comment"
AJAX_UPLOAD_MEDIA = "upload_media"
AJAX_WATCH_LISTING = "watch_listing"