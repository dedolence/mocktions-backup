# Notifications

# This is the template used by generate_notification
MESSAGE_GENERIC_TEMPLATE = "<i class='bi bi-{icon} pe-2'></i> {message}"

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
+ "because the listing currently has bids on it, or because the listing does "
+ "not belong to you.<br/>If this listing belongs to you, you may still "
+ "delete the listing.")

# User index messages
MESSAGE_USER_DELETE_PROHIBITED = ("You are not allowed to delete this listing.")
MESSAGE_USER_LISTING_DELETED = "Listing \"{}\" has been deleted."
MESSAGE_USER_PICTURE_UPLOAD_SUCCESS = "Upload successful!"
MESSAGE_USER_PICTURE_UPLOAD_FAILURE = "Upload failed. Try a different picture maybe?"
MESSAGE_USER_PICTURE_UPLOAD_FORMAT = "Upload failed. File format must be .jpg/.jpeg, .gif, .png, or .tiff."