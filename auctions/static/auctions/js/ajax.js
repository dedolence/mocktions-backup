// This global constant is defined in layout.html; just pointing it out here.
AJAX_URLS


async function makeFetch(formData, url, method="POST") {
    // need some way to timeout a request
    const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return fetch(url, {
        method: method,
        body: formData,
        headers: {'X-CSRFToken': csrf_token}
    })
    .then(res => {
        if (res.status >= 200 && res.status <= 299) {
            return res.json();
        }
        else {
            throw Error(res.statusText);
        }
    })
    .catch(() => {
        // this catches 4xx and 5xx errors
        // return a rejected promise so i can catch() it elsewhere
        return new Promise((res, rej) => {
            rej();
        })
    })
}


function commentDelete(commentId) {
    const modalElement = $('deleteCommentModal');
    const modal = new bootstrap.Modal(modalElement);

    const quoteElement = $('deleteOriginalComment');
    const originalComment = $('commentText-' + commentId);
    quoteElement.innerHTML = originalComment.innerHTML;

    const submitButton = $('deleteSubmitButton');
    submitButton.addEventListener('click', function() {
        const url = AJAX_URLS.ajax_delete_comment;
        const formData = new FormData();
              formData.append('comment_id', commentId);
        makeFetch(formData, url)
        .then((r) => {
            const originalComment = $('comment-' + commentId);
            originalComment.parentElement.removeChild(originalComment);
            modal.hide();
        });
    })
    modal.show();
}


function commentReply(commentId) {
    const url = AJAX_URLS.ajax_reply_comment;
    const formData = new FormData();
          formData.append('comment_id', commentId);

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


function dismissNotification(notificationId) {
    let notificationElement = $('notification-' + notificationId);
    let formData = new FormData();
        formData.append('notification_id', notificationId);
    
    const url = AJAX_URLS.ajax_dismiss_notification;
    makeFetch(formData, url)
    .then((r) => {
        notificationElement.parentElement.removeChild(notificationElement);
    })
    .catch((error) => {
        console.log(error);
    })
}


function generateComment() {
    const textInputElement = $('id_content');
    const url = AJAX_URLS.ajax_generate_comment;
    makeFetch(null, url)
    .then((r) => {
        const comment = r.comment;
        textInputElement.innerHTML = comment;
        console.log(textInputElement);
    })
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

        uploadMedia();
    })
}


function uploadMedia(listingId=null) {
    // - Close the modal.
    // - Gather the images to upload:
    //      - Either an image was uploaded,
    //      - An image URL was entered,
    //      - Or neither (server will provide a random image)
    // - Send request to server with relevant form data
    // - Receive response:
    //      - (Success) Formatted HTML to append to a thumbnail container element
    //      - (Failure) An error message
    // - Append formatted HTML or display error message
    // - Add ID of new image(s) to a placeholder select list

    // get required elements and information
    const errorContainerElement = $('uploadImageError');
    const thumbnailContainer = $('formThumbnails');
    const currentImageCount = thumbnailContainer.children.length;
    const url = AJAX_URLS.ajax_upload_media;
    const uploadElement = $('id_upload_image');
    const formData = new FormData();
    const multiple = uploadElement.multiple? true : false;
    const selectElement = $('selectImageInput');
    
    // set up the form data
    formData.append('listing_id', listingId);
    formData.append('url', $('id_url_image').value);
    formData.append('currentImageCount', currentImageCount);
    // obnoxiously, files must be appended to form data individually
    for (let i = 0, n = uploadElement.files.length; i < n; i++) {
            formData.append('files', uploadElement.files[i]);
    }

    // loading progress modal
    const loadingModalElement = $('loadingImageModal');
    const loadingModal = new bootstrap.Modal(loadingModalElement);
    loadingModal.show();

    // clear out any other errors
    errorContainerElement.innerHTML = '';
    errorContainerElement.style.display = "none";

    makeFetch(formData, url)
    .then((r) => {
        // success
        if (r.html && r.ids && r.paths) {
            // check to see if multiple images can be appended, or if one image only
            if (multiple) {
                thumbnailContainer.innerHTML += r.html;
            }
            else {
                thumbnailContainer.innerHTML = r.html;
            }
            // append new IDs to a select field for inclusion with new listing
            for (let id of r.ids) {
                if (!multiple) {
                    selectElement.innerHTML = '';
                }
                const optionElement = document.createElement('option');
                optionElement.value = id;
                optionElement.defaultSelected = true;
                selectElement.appendChild(optionElement);
            }
        }
        // failure
        else {
            errorContainerElement.style.display = "block";
            errorContainerElement.innerHTML = r.error;
        }
    })

    loadingModal.hide();
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