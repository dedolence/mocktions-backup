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


// Upload an image an return its properties
async function ajax_upload_media(elementArray, url) {
    console.log(elementArray, url);
    // check to see if we can upload any more images
    const formThumbnails = $("formThumbnails");
    //const previewThumbnails = $("previewThumbnails");
    const currentImageCount = formThumbnails.children.length;
    const imageIdList = $('selectImageInput');
    const errorContainer = $('uploadImageError');
    //const placeholder = $('imagesPlaceholder');
    let fileSourceElement;
    // allow multiple file uploads?
    let multiple = $('id_upload_image').multiple? true : false;

    let formData = new FormData();
        formData.append('currentImageCount', currentImageCount);
        formData.append('click_action', 'showImageEditModal');

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
                /* if (previewThumbnails) {
                    if (placeholder) {
                        placeholder.parentElement.removeChild(placeholder);
                    }
                    previewThumbnails.innerHTML += r.html;
                } */
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
        let imageIdList = $('selectImageInput');
        let i = 0; n = imageIdList.children.length;
        for (i, n; i < n; i++) {
            let child = imageIdList.children[i];
            if (child.value === img_id) {
                imageIdList.removeChild(child);
            }
        }
    })
}