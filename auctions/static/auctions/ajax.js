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
                case 'dismiss':
                    let el = document.getElementById("notification-" + id);
                    $(el).fadeOut();
                    break;
                case 'watch_listing':
                    watchListing(r, id, disappear);
                    break;
                case 'generate_comment':
                    comment_input.innerHTML = r.message;
                    comment_input.style.height = 'auto';
                    comment_input.style.height = comment_input.scrollHeight + 10 + "px";
                    break;
                case 'reply_comment':
                    reply_comment(r);
                    break;
                case 'edit_comment':
                    editComment(id);
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

    // reset on losing focus
    comment_box.addEventListener("focusout", function() {
        comment_box.innerHTML = "";
        submit_button.value = "Submit";
        hidden_id.removeAttribute("value");
    })
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
