$(function () {
    var selectTag = $("#select-host").children().clone();
    // 选择主机组

    $("#select-host-group").on("change", function () {
        var hostGroupID = $("#select-host-group option:selected").val();
        if (hostGroupID === '0') {
            $("#select-host").empty();
            $("#select-host").append(selectTag);
            return false;
        }
        $.ajax({
            url: "select_host_group_for_chart.html",
            type: "POST",
            dataType: "JSON",
            traditional: true,
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"host_group_id": hostGroupID},
            success: function (response) {
                if (response.status) {
                    $("#select-host").empty();
                    var tag = '<option value="0">所有</option>';
                    $.each(response.data, function (index, item) {
                        tag += '<option value="' + item.id + '">' + item.ip + "</option>"
                    });
                    $("#select-host").append(tag);
                }
            },
            error: function () {
                
            }
        });
    });

    // 选择主机
    $("#select-host").on("change", function () {
        var hostGroupID = $("#select-host-group").val();
        var hostID = $("#select-host").val();
        if (hostID === '0') {
            return false;
        }
        $.ajax({
            url: "select_host_for_chart.html",
            type: "POST",
            dataType: "JSON",
            traditional: true,
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"host_id": hostID, 'host_group_id': hostGroupID},
            success: function (response) {
                if (response.status) {
                    $("#select-host").empty();
                    var tag = '<option value="0">所有</option>';
                    $.each(response.data, function (index, item) {
                        tag += '<option value="' + item.id + '">' + item.ip + "</option>"
                    });
                    $("#select-host").append(tag);
                }
            },
            error: function () {

            }
        });
    });
});