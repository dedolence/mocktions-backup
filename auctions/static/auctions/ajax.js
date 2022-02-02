// This is defined in the layout template, just reminding myself it exists.
AJAX_URL;

// This global contains all elements that have the attribute "data-target".
// Those are the elements that will be required by event handlers. All other
// elements can be ignored.
const TARGETS = [];
$(function() {
    // Gather all elements that are required for any event handlers.
    let targetQuery = document.querySelectorAll('*[data-target]');
    targetQuery.forEach(function(e) {
        TARGETS.push(e);
    })
});


// Set up event handlers
document.addEventListener("click", e => {
    let target = e.target;
    let clickAction = target.dataset.clickAction;
    if (!clickAction) {
        // Ignore anything that doesn't have the "data-click-action" attribute
        return;
    }
    else {
        // get all the relevant elements
        // relevant elements have a target data attribute that's = the trigger's click-action attribute
        let elementArray = TARGETS.filter(function(e) {
            if (e.dataset.target == clickAction) {
                return e;
            }
        })
        // automatically calls a function based only on its name (string)
        window[clickAction](elementArray);
    }
});


// Upload an image an return its properties
function uploadImage(elementArray) {
    // check to see if we can upload any more images
    const thumbnailContainer = document.getElementById('thumbnails');
    const currentImages = thumbnailContainer.children.length;
    console.log(elementArray);
    // get POST url
    const url = AJAX_URL('upload_image');
    let csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value
    let formData = new FormData();
    let listing_id = document.querySelector('*[data-listing-id]').dataset.listingId;
        formData.append('listing_id', listing_id);
    let fileSourceElement;
    elementArray.forEach(function(e) {
        if (e.value && !fileSourceElement) {
            fileSourceElement = e;
            switch (e.type) {
                case "file":
                    let i = 0;
                    let n = fileSourceElement.files.length;
                    for (i, n; i < n; i++) {
                        formData.append('files', fileSourceElement.files[i]);
                    }
                    break;
                case "url":
                    formData.append('url', fileSourceElement.value);
                    break;
                default:
                    break;
            }
        }
        else {
            return;
        }
    });
    // load a loading progress modal because this can take some time
    let loadingModalElement = document.getElementById('loadingImageModal');
    let loadingModal = new bootstrap.Modal(loadingModalElement);
    loadingModal.show();
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {'X-CSRFToken': csrf_token}
    })
    .then(res => res.json())
    .then(r => {
        if (r.error) {
            let errorDiv = generateListingFormError(r.error);
            let errorContainer = document.getElementById('formErrors');
            errorContainer.appendChild(errorDiv);
        }
        else {
            // r is an array containing the paths to each full-size image
            let i = 0
            let n = r.paths.length;
            if (n > 0) {
                // create card elements and append them to the form
                for (i, n; i < n; i++) {
                    // remove placeholder
                    let fc = thumbnailContainer.firstChild;
                    if (fc && fc.nodeName == "#text") {
                        thumbnailContainer.innerHTML = '';
                    }
                    thumbnailContainer.append(buildImageCard(r.paths[i], r.ids[i]));
                }
            }
            loadingModal.hide();
            /* hide() doesn't always work, as when users upload images. No idea why.
             * From this script's perspective there is no difference in these methods.
             * So, set a timer (arbitrarily for one second) just to manually hide
             * the modal if it's still being displayed. */
            window.setTimeout(() => { loadingModal.hide(); }, 1000);
        }
    })
}


function buildImageCard(image_path, image_id) {
    let div = document.createElement('div');
        div.className = "me-3 mb-3 image-thumbnail border"
        div.style.backgroundImage = `url(${image_path})`;
        div.id = "img_thumbnail-" + image_id;
        div.dataset.target = 'removeImage';
        TARGETS.push(div);
    let a = document.createElement('a');
        a.href = "#";
        a.classList.add('stretched-link')
        a.addEventListener('click', e => {
            let modalElement = document.getElementById('editImageModal');
            let modal = new bootstrap.Modal(modalElement);
            let img = document.getElementById('imageForEdit');
                img.src = image_path;
            modal.show();
        })
    div.appendChild(a);
    return div;
}


function removeImage(elementArray) {
    let img_target = elementArray[0];
    // remove this from targets as it's no longer target-able
    TARGETS.splice(TARGETS.indexOf(img_target), 1);
    img_target.parentElement.removeChild(img_target);

    const url = AJAX_URL("purge_image");
    const img_id = img_target.id.split('-')[1];
    const formData = new FormData();
    formData.append('img_id', img_id);
    fetch(url, { 
        method: "POST",
        body: formData
    })
}


function generateListingFormError(error) {
    let alertElement = document.createElement('div');
        alertElement.className = "alert alert-danger alert-dismissible";
        alertElement.id = 'errorDiv';
    let textSpan = document.createElement('span');
    let dismissButton = document.createElement('button');
        dismissButton.type = 'button';
        dismissButton.classList.add('btn-close');
        dismissButton.dataset.bsDismiss = 'alert';
        dismissButton.ariaLabel = 'Close';
    switch (error) {
        case "DecompressionBombError":
            textSpan.innerHTML = "Couldn't upload image: too large.";
            break;
        default:
            break;
    }
    alertElement.appendChild(textSpan).appendChild(dismissButton);
    return alertElement;
}


function ajax(full_url, disappear = false) {
    // params[0] will be a leading '/'; params[1] will be 'ajax'
    let params = full_url.split('/');
    let action = params[2];
    let id = params[3];
    let csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value
    fetch(full_url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrf_token}
        })
        .then(res => res.json())
        .then(r => {
            let comment_input = document.getElementById("commentInput");
            switch (action) {

                case 'add_image':
                    console.log("Adding image");
                    break;

                case 'delete_comment':
                    let card = document.getElementById("comment-" + id);
                    let alert = document.createElement("div");
                        alert.classList.add("alert");
                        alert.classList.add("alert-warning");
                        alert.ariaRoleDescription = "alert";
                        alert.innerHTML = r.message;
                    let parent = card.parentElement;
                    parent.replaceChild(alert, card);
                    setTimeout(function() {
                        $(alert).fadeOut();
                    }, 1000);
                    break;

                case 'dismiss':
                    let el = document.getElementById("notification-" + id);
                    $(el).fadeOut();
                    break;

                case 'edit_comment':
                    editComment(id);
                    break;
                    
                case 'generate_comment':
                    comment_input.innerHTML = r.message;
                    comment_input.style.height = 'auto';
                    comment_input.style.height = comment_input.scrollHeight + 10 + "px";
                    break;

                case 'generate_random_user':
                    dob = r.dob.date.split('-');
                    dob_year = dob[0];
                    dob_month = dob[1];
                    dob_day = dob[2].split('T')[0];
                    dob_full = `${dob_month}/${dob_day}/${dob_year}`;
                    street_full = `${r.location.street.number} ${r.location.street.name}`;
                    document.getElementById("id_username").value = r.login.username;
                    document.getElementById("id_email").value = r.email;
                    document.getElementById("id_password").value = r.login.password;
                    document.getElementById("id_confirm_password").value = r.login.password;
                    document.getElementById("id_first_name").value = r.name.first;
                    document.getElementById("id_last_name").value = r.name.last;
                    document.getElementById("id_street").value = street_full;
                    document.getElementById("id_city").value = r.location.city;
                    document.getElementById("id_state").value = r.location.state;
                    document.getElementById("id_postcode").value = r.location.postcode;
                    document.getElementById("id_country").value = r.location.country;
                    document.getElementById("id_phone").value = r.phone;
                    break;
                
                case 'reply_comment':
                    reply_comment(r);
                    break;

                case 'watch_listing':
                    watchListing(r, id, disappear);
                    break;

                default:
                    break;
            }
            return;
        });
}

function editComment(id) {
    let anchor = document.getElementById("commentInputAnchor");
    let comment_text = document.getElementById("commentText-" + id);
    let comment_box = document.getElementById("commentInput");
    let submit_button = document.getElementById("commentSubmitButton");
    let hidden_id = document.getElementById("commentId");
    comment_box.innerHTML = comment_text.innerText;
    submit_button.value = "Save Changes";
    hidden_id.value = id;
    // set height to show entire comment
    comment_box.style.height = 'auto';
    comment_box.style.height = comment_box.scrollHeight + 10 + "px";
    comment_box.focus();
    anchor.scrollIntoView();

}

function reply_comment(r) {
    const orig_comment = (JSON.parse(r.comment))[0];
        // author is not part of the serialized model data, added separately
    const orig_author = r.author; 
    const modalElement = document.getElementById("replyModal");
    const originalCommentId = document.getElementById("originalCommentId");
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

function watchListing(res, id, disappear) { 
    let listing = document.getElementById("listing-" + id);
    let toastElement = document.getElementById("toast-" + id);
    let toastBody = document.getElementById("toast-body-" + id);
    let buttonText = document.getElementById("toast-button-text-" + id);
    let toastIcon = document.getElementById("toast-icon-" + id);

    toastBody.innerHTML = res.message;
        // toggle icon and text
    if (!res.undo) {
        toastIcon.classList.toggle("bi-heart");
        toastIcon.classList.toggle("bi-heart-fill");
        buttonText.innerHTML = res.button_text;
    }
        // create Toast instance
    let toast = new bootstrap.Toast(toastElement);
    // display Toast
    toast.show();
    if (disappear) {
        $(listing).fadeOut();
    }
}
