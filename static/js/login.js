$(function () {
    $("#accloginForm").submit(function () {
        $("#errorMessage").text('');
        var email = $("input[name='email']").val();
        // 判断用户输入的用户名是否为邮件地址格式 0为真 -1为假
        if (email.search(/^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/) == -1) {
            var errorMessage = "用户名必须为邮件格式";
            $("#errorMessage").text(errorMessage);
            return false;
        }
    });
});
