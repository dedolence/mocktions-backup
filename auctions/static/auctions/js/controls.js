
// This global contains all elements that have the attribute "data-target".
// Those are the elements that will be required by event handlers. All other
// elements can be ignored.
const TARGETS = [];
const GLOBALS = {};


// On page load (or fire if page is loaded by the time it gets here)
if (document.readyState === 'loading') {
    // NB this does block final load of images/stylesheets; keep it light
    document.addEventListener("DOMContentLoaded", populateTargets);
} else {
    populateTargets();
}


document.addEventListener("click", e => {
    let target = e.target;
    let clickAction = target.dataset.clickAction;
    if (!clickAction) {
        // Ignore anything that doesn't have the "data-click-action" attribute
        return;
    }
    else {
        // get all the relevant elements
        // relevant elements have a target data attribute = to the trigger's click-action value
        let elementArray = TARGETS.filter(function(e) {
            if (e.dataset.target == clickAction) {
                return e;
            }
        })
        // automatically calls a function based only on its name
        var url = AJAX_URLS[clickAction] ? AJAX_URLS[clickAction] : null;
        window[clickAction](elementArray, url, e);
    }
});


function changeSlide(listingId, direction) {
    // get current slide index
    let currentSlideIndex;
    const bannerImage = $('banner-'+listingId);
    const allImages = bannerImage.parentElement.children;
    for (let i = 0; i < allImages.length; i++) {
        if (!allImages[i].classList.contains('d-none')) {
            currentSlideIndex = i;
        }
    }

    // check to see if new slide index goes out of bounds
    let newSlideIndex = currentSlideIndex + direction;
    if (newSlideIndex < 0) {
        newSlideIndex = allImages.length - 1;
    }
    if (newSlideIndex > allImages.length - 1) {
        newSlideIndex = 0;
    }

    // display new indexed image
    for (let i = 0; i < allImages.length; i++) {
        allImages[i].classList.add('d-none');
    }
    allImages[newSlideIndex].classList.remove('d-none');
}


function editComment(id) {
    let anchor = $("commentInputAnchor");
    let comment_text = $("commentText-" + id);
    let comment_box = $("commentInput");
    let submit_button = $("commentSubmitButton");
    let hidden_id = $("commentId");
    comment_box.innerHTML = comment_text.innerText;
    submit_button.value = "Save Changes";
    hidden_id.value = id;
    // set height to show entire comment
    comment_box.style.height = 'auto';
    comment_box.style.height = comment_box.scrollHeight + 10 + "px";
    comment_box.focus();
    anchor.scrollIntoView();

}


function generateListingFormError(error) {
    let alertElement = document.createElement('div');
        alertElement.className = "alert alert-danger alert-dismissible";
        alertElement.id = 'errorDiv';
    let textSpan = document.createElement('span');
        textSpan.innerHTML = error;
    let dismissButton = document.createElement('button');
        dismissButton.type = 'button';
        dismissButton.classList.add('btn-close');
        dismissButton.dataset.bsDismiss = 'alert';
        dismissButton.ariaLabel = 'Close';
    alertElement.appendChild(textSpan).appendChild(dismissButton);
    return alertElement;
}


function generateUser() {
    const url = 'https://randomuser.me/api/';
    const usernameField = $('id_username');
    const password1Field = $('id_password1');
    const password2Field = $('id_password2');
    const firstNameField = $('id_first_name');
    const lastNameField = $('id_last_name');
    const emailField = $('id_email');
    const streetField = $('id_street');
    const cityField = $('id_city');
    const stateField = $('id_state');
    const postcodeField = $('id_postcode');
    const countryField = $('id_country');
    const phoneField = $('id_phone');
    
    make_fetch(null, url, "GET")
    .then((r) => {
        const res = r.results[0];
        console.log(res);
        usernameField.value = res.login.username;
        password1Field.value = password2Field.value = res.login.password;
        firstNameField.value = res.name.first;
        lastNameField.value = res.name.last;
        emailField.value = res.email;
        streetField.value = res.location.street.number + " " + res.location.street.name;
        cityField.value = res.location.city;
        stateField.value = res.location.state;
        postcodeField.value = res.location.postcode;
        countryField.value = res.location.country;
        phoneField.value = res.phone;
    })
}


function populateTargets() {
    // Clear the targets object then repopulate it.
    Object.keys(TARGETS).forEach(key => delete TARGETS[key]);
    document.querySelectorAll('*[data-target]').forEach(function(e) {
        TARGETS.push(e);
    });
}


function reply_comment(r) {
    const orig_comment = (JSON.parse(r.comment))[0];
        // author is not part of the serialized model data, added separately
    const orig_author = r.author; 
    const modalElement = $("replyModal");
    const originalCommentId = $("originalCommentId");
    const modal = new bootstrap.Modal(modalElement);

        // This works fine, but...
    originalCommentId.value = orig_comment.pk;
        // ...for some unimaginable reason, jquery is the only thing that works.
        // Calls to innerHTML or innerText simply do not apply. No idea why.
    $("#originalCommentAuthor").html(orig_author);
    $("#originalCommentContent").html(orig_comment.fields.content);
    $("#commentInputLabel").html("Reply to " + orig_author + ": ");
    modal.show();
}


function setImageBanner(listingId, newSlideIndex) {
    const bannerImage = $('banner-'+listingId);
    const allImages = bannerImage.parentElement.children;
    for (let i = 0; i < allImages.length; i++) {
        allImages[i].classList.add('d-none');
    }
    allImages[newSlideIndex].classList.remove('d-none');
}


function showImageEditModal(elementArray) {
    let functionName = elementArray[0].dataset.clickAction;
    let imagePath = elementArray[0].dataset.imagePath;
    let modalElement = $(functionName);
    showImageModal(modalElement, imagePath)
}


function showImageModal(modalElement, imagePath) {
    let modal = new bootstrap.Modal(modalElement);
    let modalImagePlaceholder = $('modalImagePlaceholder');
        modalImagePlaceholder.src = imagePath;
    modal.show();
}


function showImageViewModal(elementArray, url=null) {
    let modalElement = $('viewImageModal');
    let imageElement = elementArray[0];
    let imageId = imageElement.id.split('-')[1];
    showImageModal(modalElement, imagePath)
}


function watchListing(listingId) {
    const url = AJAX_URLS.ajax_watch_listing;
    let formData = new FormData();
        formData.append('listing_id', listingId)
    
    make_fetch(formData, url)
    .then((r) => {
        // find/replace the watchlist button group with the rendered html
        let buttonContainer = $('watchButton-' + listingId);
            buttonContainer.innerHTML = r.html;

        // initialize and display the toast
        let toastElement = $('watchlistToast-' + listingId);
        let toast = new bootstrap.Toast(toastElement, {'autohide': true, 'delay': 2000});
        toast.show();
    })
    .catch((error) => {
        console.log(error);
    })
}