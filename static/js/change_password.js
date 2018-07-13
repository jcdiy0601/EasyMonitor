$(function () {

    // 打开模态对话框
    $("#change-password").click(function () {
        $("#change-password-div").css("display", "block");
    });

    // 关闭模态对话框
    $("#close").click(function () {
        $("#change-password-div").css("display", "none");
    });

    //
    $("#confirm").click(function () {
        $.ajax({
            url: "/user_info.html",
            type: "POST",
            dataType: "JSON",
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: $("#change-password-form").serialize(),
            success: function (arg) {
                if (arg.status) {
                    $("#change-password-div").css("display", "none");
                    $("#show-change-password-result").removeClass("hidden").addClass("btn-success").text("密码修改成功");
                    setTimeout(function () {
                        window.location.reload();
                    }, 2000);

                } else {
                    var message = arg.message;
                    $("#change-password-div").css("display", "none");
                    $("#show-change-password-result").removeClass("hidden").addClass("btn-danger").text(message);
                    setTimeout(function () {
                        $("#show-change-password-result").removeClass("btn-danger").addClass("hidden").text("");
                    }, 2000);
                }
            },
            error: function () {

            }
        });
    });
});