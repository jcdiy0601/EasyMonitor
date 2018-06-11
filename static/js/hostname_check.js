$(function () {
    // 主机名检测
    $("#hostname-check").click(function () {
        var hostname = $("input[name='hostname']").val();
        // 不为空发送到后台
        if (hostname.length) {
            $.ajax({
                url: "/monitor_web/hostname_check.html",
                type: "POST",
                data: {"hostname": hostname},
                dataType: "JSON",
                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                success: function (response) {
                    if (response.status) {
                        $("#hostname-check").css("display", "none");
                        $("#hostname-check-icon").css("display", "inline-block");
                    } else {
                        alert("主机名在CMDB中不存在，不可使用");
                    }
                },
                error: function () {

                }
            });
        } else {
            return false;
        }
    });

    // 检测主机名栏检测后又被更改
    $("input[name='hostname']").on("input", function () {
        $("#hostname-check").css("display", "inline-block");
        $("#hostname-check-icon").css("display", "none");
    });

    // 如果没有检测成功不予许提交数据
    $("button[type='submit']").click(function () {
        if ($("#hostname-check").css("display") === "inline-block") {
            alert("请进行主机名检测");
            return false;
        }
    });
});
