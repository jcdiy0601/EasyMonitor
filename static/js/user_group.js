$(function () {
    // 全选
    $("thead input").click(function () {
        // 判断是否被点中
        if ($(this).prop("checked")) {  // 点中
            $("tbody input").prop("checked", true).parent().addClass("active");
        } else {                       // 取消
            $("tbody input").prop("checked", false).parent().removeClass("active");
        }
    });
    // 计算被选中check-box个数
    $("table input").click(function () {
        var count=0;
        $("tbody input").each(function () {
            if ($(this).prop("checked")) {
                count=count+1;
            }
        });
        $("#selected_count span").text(count);
    })
});