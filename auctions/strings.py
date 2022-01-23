# Notifications

# This is the template used by generate_notification
MESSAGE_GENERIC_TEMPLATE = "<i class='bi bi-{icon} pe-2'></i> {message}"

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
+ "because the listing currently has bids on it, or because the listing does "
+ "not belong to you.<br/>If this listing belongs to you, you may still "
+ "delete the listing.")

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