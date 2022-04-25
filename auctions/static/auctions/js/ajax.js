// This global constant is defined in layout.html; just pointing it out here.
AJAX_URLS


async function make_fetch(formData, url, method="POST") {
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


function ajax_dismiss_notification(elementArray, url) {
    let notificationElement = elementArray[0];
    let notificationId = notificationElement.id.split('-')[1]
    let formData = new FormData()
        formData.append('notification_id', notificationId)
    
        make_fetch(formData, url)
        .then((r) => {
            notificationElement.parentElement.removeChild(notificationElement);
        })
        .catch((error) => {
            console.log(error);
        })
}

function dismissNotification(id) {
    let notificationElement = $('notification-' + id);
    let formData = new FormData();
        formData.append('notification_id', id);
    
    const url = AJAX_URLS.ajax_dismiss_notification;
    make_fetch(formData, url)
    .then((r) => {
        notificationElement.parentElement.removeChild(notificationElement);
    })
    .catch((error) => {
        console.log(error);
    })
}


function ajax_generate_comment(elementArray, url) {
    const textInputElement = $('id_content');
    make_fetch(null, url)
    .then((r) => {
        const comment = r.comment;
        textInputElement.innerHTML = comment;
        console.log(textInputElement);
    })
}


// Upload an image and return its properties
async function ajax_upload_media(elementArray, url) {
    // check to see if we can upload any more images
    const formThumbnails = $("formThumbnails");
    //const previewThumbnails = $("previewThumbnails");
    const currentImageCount = formThumbnails.children.length;
    const imageIdList = $('selectImageInput');
    const errorContainer = $('uploadImageError');

    //const listingId = $('listingId').value? $('listingId').value : null;
    //const placeholder = $('imagesPlaceholder');
    let fileSourceElement;
    // allow multiple file uploads?
    let multiple = $('id_upload_image').multiple? true : false;

    let formData = new FormData();
    formData.append('currentImageCount', currentImageCount);
    if ($('listingId')) {
        formData.append('listing_id', listingId? listingId : null);
    }

    // loading progress modal
    const loadingModalElement = $('loadingImageModal');
    const loadingModal = new bootstrap.Modal(loadingModalElement);
    loadingModal.show();

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

    // send the file/url to the server, receive formatted HTMl in response
    make_fetch(formData, url)
    .then((r) => {
        // r = {
        //  paths: [source paths for images], 
        //  ids: [primary keys], 
        //  html: "html string for appending to DOM"
        // }
        if (r.paths.length > 0) {
            if (multiple) {
                formThumbnails.innerHTML += r.html;
            } else {
                formThumbnails.innerHTML = r.html;
                imageIdList.innerHTML = '';
            }
            // add image ids to a list that will be sent to server to be referenced by the listing
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
    .catch((error) => {
        let errorDiv = generateListingFormError(error);
        errorContainer.appendChild(errorDiv);;
        loadingModal.hide();
    });
    
}