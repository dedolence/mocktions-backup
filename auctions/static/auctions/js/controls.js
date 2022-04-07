
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



function populateTargets() {
    // Clear the targets object then repopulate it.
    Object.keys(TARGETS).forEach(key => delete TARGETS[key]);
    document.querySelectorAll('*[data-target]').forEach(function(e) {
        TARGETS.push(e);
    });
}


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


function setImageBanner(listingId, newSlideIndex) {
    const bannerImage = document.getElementById('banner-'+listingId);
    const allImages = bannerImage.parentElement.children;
    for (let i = 0; i < allImages.length; i++) {
        allImages[i].classList.add('d-none');
    }
    allImages[newSlideIndex].classList.remove('d-none');
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