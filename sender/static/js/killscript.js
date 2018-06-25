function ajaxKill() {
    var xhr = $.ajax(
        {
            url: "/killSwitch",
            context: document.body
        }
    );
    xhr.success(function(){feedback("success")});
    xhr.fail(function(){feedback("fail")});
}

function feedback(note) {
    console.log(note);
    $(document.body).addClass("done");
    setTimeout(removeFeedback, 500);
}

function removeFeedback() {
    console.log('Remove Feedback');
    $(document.body).removeClass("done");
}