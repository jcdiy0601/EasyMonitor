$(function () {
    // 全选
    $("thead ins").click(function () {
        // 判断是否被点中
        if ($(this).parent().hasClass("checked")) {  // 点中
            $("tbody input").prop("checked", true).parent().addClass("checked");
        } else {                       // 取消
            $("tbody input").prop("checked", false).parent().removeClass("checked");
        }
    });

    // 计算被选中check-box个数
    $("table ins").click(function () {
        var count = 0;
        $("tbody input").each(function () {
            if ($(this).prop("checked")) {
                count = count + 1;
            }
        });
        $("#selected_count span").text(count);
    });

    // 获取check-box id
    $("#delete_template").click(function () {
        if (parseInt($("#selected_count span").text()) !== 0) {
            var templateList = [];
            $("tbody input").each(function () {
               if ($(this).prop("checked")) {
                   templateList.push($(this).val());
               }
            });
            // 显示模态对话框
            $("#project-del-div").css("display", "block");
            // 点击取消按钮
            $("#cancel-del").click(function () {
                // 关闭模态框
                $("#project-del-div").css("display", "none");
            });
            // 点击关闭按钮
            $("#close-modal-div").click(function () {
                // 关闭模态框
                $("#project-del-div").css("display", "none");
            });
            // 点击确认按钮
            $("#confirm-del").click(function () {
                // 关闭模态框
                $("#project-del-div").css("display", "none");
                // 发送ajax删除数据
                $.ajax({
                    url: "del_template.html",
                    type: "POST",
                    dataType: "JSON",
                    headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                    traditional: true,
                    data: {"template_list": templateList},
                    success: function (response) {
                        if (response.status) {
                            window.location.reload();
                        } else {
                            $("#project-del-fall").css("display", "block");
                            setTimeout(function () {
                                $("#project-del-fall").css("display", "none");
                            }, 2000);
                            console.log(response.error);
                        }
                    },
                    error: function () {
                    }
                });
            });
        }
    });

    // 查询
    $("#select-host-group").on("change", function () {
        var hostGroupID = $("#select-host-group option:selected").val();
        window.location.href = "/monitor_web/template.html?groupid=" + hostGroupID;
    })
});