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


function commentEdit(commentId) {
    const modalElement = $('editModal');
    const modal = new bootstrap.Modal(modalElement);

    const textInputElement = $('edit_content');
    const originalComment = $('commentText-' + commentId).innerText;
    const originalIdInput = $('originalCommentId');
    
    textInputElement.innerHTML = originalComment;
    originalIdInput.value = commentId;

    modal.show();
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