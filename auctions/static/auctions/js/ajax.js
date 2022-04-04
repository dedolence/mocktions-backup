// This global constant is defined in layout.html; just pointing it out here.
AJAX_URLS


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
    const bannerImage = document.getElementById('banner-'+listingId);
    const allImages = bannerImage.parentElement.children;
    for (let i = 0; i < allImages.length; i++) {
        if (!allImages[i].classList.contains('d-none')) {
            currentSlideIndex = i;
        }
    }

    // check to see if new slide goes out of bounds
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


function setImageBanner(listingId, newSlideIndex) {
    const bannerImage = document.getElementById('banner-'+listingId);
    const allImages = bannerImage.parentElement.children;
    for (let i = 0; i < allImages.length; i++) {
        allImages[i].classList.add('d-none');
    }
    allImages[newSlideIndex].classList.remove('d-none');
}


function populateTargets() {
    // Clear the targets object then repopulate it.
    Object.keys(TARGETS).forEach(key => delete TARGETS[key]);
    document.querySelectorAll('*[data-target]').forEach(function(e) {
        TARGETS.push(e);
    });
}


async function make_fetch(formData, url) {
    // need some way to timeout a request
    const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return fetch(url, {
        method: 'POST',
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
    .catch((error) => {
        // this catches 4xx and 5xx errors
        // return a rejected promise so i can catch() it elsewhere
        return new Promise((res, rej) => {
            rej();
        })
    })
}

function ajax_test(elementArray, url) {
    make_fetch(null, url)
    .then(r => {
        elementArray[0].innerHTML = r.message;
    })
}

// Upload an image an return its properties
async function ajax_upload_media(elementArray, url) {
    // check to see if we can upload any more images
    const formThumbnails = document.getElementById("formThumbnails");
    const previewThumbnails = document.getElementById("previewThumbnails");
    const currentImageCount = formThumbnails.children.length;

    let formData = new FormData();
        formData.append('currentImageCount', currentImageCount);
        formData.append('click_action', 'showImageEditModal');
    
    let fileSourceElement;

    // iterate through the elements and see which type of image we're fetching:
    // user can choose to add an image from a URL or upload from their computer.
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
    const loadingModalElement = document.getElementById('loadingImageModal');
    const loadingModal = new bootstrap.Modal(loadingModalElement);
    loadingModal.show();

    make_fetch(formData, url)
    .then(r => {
        if (r.error) {
            let errorDiv = generateListingFormError(r.error);
            let errorContainer = document.getElementById('formErrors');
            errorContainer.appendChild(errorDiv);
            loadingModal.hide();
        }
        else {
            return r;
        }
    })
    .then(r => {
        // r = {
        //  paths: [source paths for images], 
        //  ids: [primary keys], 
        //  html: "html string for appending to DOM"
        // }
        if (r.paths.length > 0) {
            formThumbnails.innerHTML += r.html;
            if (previewThumbnails) {
                let placeholder = document.getElementById('imagesPlaceholder');
                if (placeholder) {
                    placeholder.parentElement.removeChild(placeholder);
                }
                previewThumbnails.innerHTML += r.html;
            }
            // add image ids to a list that will be sent to server to be referenced by the listing
            let imageIdList = document.getElementById('selectImageInput');
            let i = 0, n = r.ids.length;
            for (i, n; i < n; i++) {
                let optionElement = document.createElement('option');
                    optionElement.value = r.ids[i];
                    optionElement.defaultSelected = true;
                    imageIdList.append(optionElement);
            }
        }

        // add new elements to list of targets
        populateTargets();
        
        loadingModal.hide();
        // hide() doesn't always work when users upload images. No idea why.
        // So, set a timer (arbitrarily for one second) just to manually hide
        // the modal if it's still being displayed. 
        window.setTimeout(() => { loadingModal.hide(); }, 1000);
    })
}


function showImageEditModal(elementArray) {
    let functionName = elementArray[0].dataset.clickAction;
    let imagePath = elementArray[0].dataset.imagePath;
    let modalElement = document.getElementById(functionName);
    showImageModal(modalElement, imagePath)
}


function showImageViewModal(elementArray, url=null) {
    let modalElement = document.getElementById('viewImageModal');
    let imageElement = elementArray[0];
    let imageId = imageElement.id.split('-')[1];
    showImageModal(modalElement, imagePath)
}


function showImageModal(modalElement, imagePath) {
    let modal = new bootstrap.Modal(modalElement);
    let modalImagePlaceholder = document.getElementById('modalImagePlaceholder');
        modalImagePlaceholder.src = imagePath;
    modal.show();
}


function ajax_purge_media(elementArray, url) {
    let img_target = elementArray[0];
    const img_id = img_target.id.split('-')[1];
    const formData = new FormData();
    formData.append('img_id', img_id);
    let request = make_fetch(formData, url);
    request.then(() => {
        // remove this from targets as it's no longer target-able
        TARGETS.splice(TARGETS.indexOf(img_target), 1);
        img_target.parentElement.removeChild(img_target);
        let imageIdList = document.getElementById('selectImageInput');
        let i = 0; n = imageIdList.children.length;
        for (i, n; i < n; i++) {
            let child = imageIdList.children[i];
            if (child.value === img_id) {
                imageIdList.removeChild(child);
            }
        }
    })
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

function watchListing(listingId) {
    const url = AJAX_URLS.ajax_watch_listing;
    let formData = new FormData();
        formData.append('listing_id', listingId)
    
    make_fetch(formData, url)
    .then((r) => {
        // find/replace the watchlist button group with the rendered html
        let buttonContainer = document.getElementById('watchButton-' + listingId);
            buttonContainer.innerHTML = r.html;

        // initialize and display the toast
        let toastElement = document.getElementById('watchlistToast-' + listingId);
        let toast = new bootstrap.Toast(toastElement, {'autohide': true, 'delay': 2000});
        toast.show();
    })
    .catch((error) => {
        console.log(error);
    })
}