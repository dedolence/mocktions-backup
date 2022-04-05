# Notifications

# This is the template used by generate_notification
from .globals import MAX_UPLOADS_PER_LISTING, MIN_UPLOADS_PER_LISTING


MESSAGE_GENERIC_TEMPLATE = "<i class='bi bi-{icon} pe-2'></i> {message}"
MESSAGE_GENERIC_LOGIN_REQUIRED = "You must be logged in to do that."
MESSAGE_GENERIC_ERROR = "An error occurred, please try again or email me about it at nhahoyt+mocktions@gmail.com"
MESSAGE_GENERIC_PERMISSIONS = "You don't have permission to perform that action. Try bribery. Venmo: @Nathaniel_Hoyt"

# Splash message
MESSAGE_SPLASH_WELCOME = ("<p><strong>Welcome to Mocktions!</strong></p>"
    + "<p>While you're here, I'd appreciate it if you could try out some of the features. "
    + "To make it easier, I've added buttons to fill out most forms with randomly-"
    + "generated information.</p><p>For instance, you can generate a random user by "
    + "clicking on <a href='register' class='alert-link'>register</a> "
    + "and then clicking the \"Generate a random user\" button. However, if you'd "
    + "like, you can also log in with one of the following generic users: "
    + "<ul><li><strong>Username - <em>Password</em></strong></li>"
    + "<li>alice - <em>default</em></li><li>bob - <em>default</em></li><li>charlie - <em>default</em></li>"
    + "</ul><p>If you notice any problems, please let me know "
    + "by emailing me at <a href='mailto:nhahoyt+mocktions@gmail.com' class='alert-link'>"
    + "nhahoyt@gmail.com</a>. Thanks!</p>")

# This is used by notify_winner
MESSAGE_NOTIFY_WINNER = ("<h4 class='alert-heading'>Congratulations!</h4>"
    + "<p>You've won <a href='{listing_url}' class='alert-link'>{listing_title}</a>. "
    + "Your item has been automatically added to your shopping cart.</p><hr>"
    + "<p><a href='{shopping_cart_url}' class='alert-link'><i class='bi bi-cart-plus pe-2'>"
    + "</i> Click here</a> to go to your shopping cart and check out.")


# Listing page messages
MESSAGE_LISTING_BID_FORMATTING = ("Bid must be whole numbers.")
MESSAGE_LISTING_BID_TOO_LOW = ("Your bid must be higher than the current bid.")
MESSAGE_LISTING_BID_TOO_HIGH = ("Your bid must be less than $100,000")
MESSAGE_LISTING_BID_SUCCESSFUL = ("Your bid was placed successfully!")
MESSAGE_LISTING_EXPIRED = ("This listing has expired.")
MESSAGE_LISTING_EDIT_SUCCESSFUL = "The listing, \"{},\" has been successfully edited."
MESSAGE_LISTING_EDIT_PROHIBITED = ("The listing, \"{},\" cannot be edited. This is either "
+ "because the listing currently has bids on it, is expired, or because the listing does "
+ "not belong to you.<br/>If this listing belongs to you, you may still "
+ "delete the listing.")
MESSAGE_LISTING_MAX_UPLOADS_EXCEEDED = ("Too many images: a listing can only have a "
+ "up to " + str(MAX_UPLOADS_PER_LISTING) + " images.")
MESSAGE_LISTING_UPLOAD_TOO_LARGE = ("Sorry, that file was too large to upload. I'm not actually "
    + "sure what size is too big because the documentation doesn't really tell me. I know "
    + "that's kinda pathetic but I have to move on and fix some other stuff now. "
    + "Try uploading something smaller. Ok, bye.")
MESSAGE_WATCHLIST_PROMPT = "Add to watchlist"
MESSAGE_WATCHLIST_ADDED = "Listing added to watchlist"
MESSAGE_WATCHLIST_REMOVED = "Listing removed from watchlist"
MESSAGE_LISTING_DRAFT_SAVED = ("Your listing has been saved to drafts. You can leave this "
    + "page and finish editing it later if you want.")
MESSAGE_LISTING_DRAFT_CAP_EXCEEDED = ("You currently have too many listing drafts already. "
    + "Please publish or delete a draft to free up more space for a new listing.")

# User index messages
MESSAGE_USER_DELETE_PROHIBITED = ("You are not allowed to delete this listing.")
MESSAGE_USER_LISTING_DELETED = "Listing \"{}\" has been deleted."
MESSAGE_USER_PICTURE_UPLOAD_SUCCESS = "Upload successful!"
MESSAGE_USER_PICTURE_UPLOAD_FAILURE = "Upload failed. Try a different picture maybe?"
MESSAGE_USER_PICTURE_UPLOAD_FORMAT = "Upload failed. File format must be .jpg/.jpeg, .gif, .png, or .tiff."

# Registration messages
MESSAGE_REG_PASSWORD_MISMATCH = "Passwords must match."
MESSAGE_REG_USERNAME_TAKEN = "That username has been taken already."
MESSAGE_REG_SUCCESS = ("<p><strong>Success!</strong> Welcome to Mocktions, a fake but (nearly) "
    + "fully-functional auction site.</p>"
    + "<p>While you're here I'd appreciate it if you could test out some of the features, "
    + "like creating listings, bidding on them, deleting them, editing them, and adding "
    + "comments. I know that's a lot to ask, so for many of these functions I've added "
    + "a button that will fill out the forms with randomized data for you.</p>"
    + "<p>Thanks for visiting, and if you run into any issues please let me know at "
    + "<a href='mailto:nhahoyt@gmail.com' class='alert-link'>nhahoyt@gmail.com</a>.</p>")

# Listing creation message
MESSAGE_LISTING_CREATION_INVALID_USER = ("Couldn't access listing. Listing owner and user don't match. "
    + "This could happen if you logged in as a different user and tried to access a listing draft.")
MESSAGE_LISTING_CREATION_IMAGES_REQUIRED = ("Each listing must have at least " + str(MIN_UPLOADS_PER_LISTING)
    + " and no more than " + str(MAX_UPLOADS_PER_LISTING) + " images. Otherwise, how are people gonna know what"
    + " they're buying?")