
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


function commentEdit(id) {
    const modalElement = $('editModal');
    const modal = new bootstrap.Modal(modalElement);

    const textInputElement = $('edit_content');
    const originalComment = $('commentText-' + id).innerText;
    const originalIdInput = $('originalCommentId');
    
    textInputElement.innerHTML = originalComment;
    originalIdInput.value = id;

    modal.show();
}


function commentReply(id) {
    const url = AJAX_URLS.ajax_reply_comment;
    const formData = new FormData();
          formData.append('comment_id', id);

    makeFetch(formData, url)
    .then((r) => {
        const modalElement = $('replyModal');
        const modal = new bootstrap.Modal(modalElement);

        const replyToInput = $('reply_replyTo');
        const originalAuthorElement = $('originalCommentAuthor');
        const originalCommentElement = $('originalCommentContent');
        const commentObj = JSON.parse(r.comment)[0];
        const originalAuthor = r.author;
        const listingInput = $('reply_listing'); 
        
        originalAuthorElement.innerHTML = originalAuthor;
        originalCommentElement.innerHTML = commentObj.fields.content.trim();
        replyToInput.value = commentObj.pk;
        listingInput.value = commentObj.fields.listing; // just in case Django doesn't
        modal.show();
    })

}


function commentDelete(id) {
    const modalElement = $('deleteCommentModal');
    const modal = new bootstrap.Modal(modalElement);

    const quoteElement = $('deleteOriginalComment');
    const originalComment = $('commentText-' + id);
    quoteElement.innerHTML = originalComment.innerHTML;

    const submitButton = $('deleteSubmitButton');
    submitButton.addEventListener('click', function() {
        const url = AJAX_URLS.ajax_delete_comment;
        const formData = new FormData();
              formData.append('comment_id', id);
        makeFetch(formData, url)
        .then((r) => {
            const originalComment = $('comment-' + id);
            originalComment.parentElement.removeChild(originalComment);
            modal.hide();
        });
    })
    modal.show();
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
    
    makeFetch(null, url, "GET")
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

        ajax_upload_media([], AJAX_URLS.ajax_upload_media);
    })
}


function populateTargets() {
    // Clear the targets object then repopulate it.
    Object.keys(TARGETS).forEach(key => delete TARGETS[key]);
    document.querySelectorAll('*[data-target]').forEach(function(e) {
        TARGETS.push(e);
    });
}


function setImageBanner(listingId, newSlideIndex) {
    const bannerImage = $('banner-'+listingId);
    const allImages = bannerImage.parentElement.children;
    for (let i = 0; i < allImages.length; i++) {
        allImages[i].classList.add('d-none');
    }
    allImages[newSlideIndex].classList.remove('d-none');
}


function watchListing(listingId) {
    const url = AJAX_URLS.ajax_watch_listing;
    let formData = new FormData();
        formData.append('listing_id', listingId)
    
    makeFetch(formData, url)
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