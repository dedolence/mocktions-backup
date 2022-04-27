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


function dismissNotification(id) {
    let notificationElement = $('notification-' + id);
    let formData = new FormData();
        formData.append('notification_id', id);
    
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


function uploadMedia(id=null) {
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

    // get required elements and information\
    const errorContainerElement = $('uploadImageError');
    const thumbnailContainer = $('formThumbnails');
    const currentImageCount = thumbnailContainer.children.length;
    const url = AJAX_URLS.ajax_upload_media;
    const uploadElement = $('id_upload_image');
    const formData = new FormData();
    const multiple = uploadElement.multiple? true : false;
    const selectElement = $('selectImageInput');
    
    // set up the form data
    formData.append('listing_id', id);
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