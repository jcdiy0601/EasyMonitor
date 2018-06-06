// 第一次访问渲染默认模板下的应用集选项
$(function () {
    var templateID = $("select[name='templates_id']").val();
    $.ajax({
        url: "select_application.html",
        type: "POST",
        dataType: "JSON",
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        data: {"template_id": templateID},
        success: function (response) {
            if (response.status) {
                var tag = '<option value="" selected="selected">-----</option>';
                $("select[name='applications_id']").append(tag);
                $.each(response.data, function (index, item) {
                    var tag = '<option value="' + item.id + '">' + item.name + "</option>";
                    $("select[name='applications_id']").append(tag);
                })
            }
        },
        error: function () {

        }
    });
    var tag = '<option value="" selected="selected">-----</option>';
    $("select[name='items_id']").append(tag);
});

$(function () {
    // 改变模板
    $("select[name='templates_id']").on("change", function () {
        var templateID = $("select[name='templates_id']").val();
        $("select[name='applications_id']").empty();
        $("select[name='items_id']").empty();
        $("select[name='items_id']").append('<option value="" selected="selected">-----</option>')
        $.ajax({
            url: "select_application.html",
            type: "POST",
            dataType: "JSON",
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"template_id": templateID},
            success: function (response) {
                if (response.status) {
                    var tag = '<option value="" selected="selected">-----</option>';
                    $("select[name='applications_id']").append(tag);
                    $.each(response.data, function (index, item) {
                        var tag = '<option value="' + item.id + '">' + item.name + "</option>";
                        $("select[name='applications_id']").append(tag);
                    })
                }
            },
            error: function () {

            }
        });
    });
    // 改变应用集
    $("select[name='applications_id']").on("change", function () {
        var applicationID = $(this).val();
        var application_select_tag_obj = $(this);
        if (applicationID) {
            application_select_tag_obj.parent().next().children().empty();
            $.ajax({
                url: "select_item.html",
                type: "POST",
                dataType: "JSON",
                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                data: {"application_id": applicationID},
                success: function (response) {
                    if (response.status) {
                        var tag = '<option value="" selected="selected">-----</option>';
                        application_select_tag_obj.parent().next().children().append(tag);
                        $.each(response.data, function (index, item) {
                            var tag = '<option value="' + item.id + '">' + item.name + "</option>";
                            application_select_tag_obj.parent().next().children().append(tag);
                        })
                    }
                },
                error: function () {

                }
            });
        } else {
            application_select_tag_obj.parent().next().children().empty();
            var tag = '<option value="" selected="selected">-----</option>';
            application_select_tag_obj.parent().next().children().append(tag);
        }
    });
});

// 添加新触发器表达式
$(function () {
    $("#add-triggerexpression").click(function () {
        var tag = $("tbody").children().first().clone();
        tag.children().first().next().children().empty().append('<option value="" selected="selected">-----</option>');
        $("tbody").append(tag);
        // 改变应用集
        $("select[name='applications_id']").last().on("change", function () {
            var applicationID = $(this).val();
            var application_select_tag_obj = $(this);
            if (applicationID) {
                application_select_tag_obj.parent().next().children().empty();
                $.ajax({
                    url: "select_item.html",
                    type: "POST",
                    dataType: "JSON",
                    headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                    data: {"application_id": applicationID},
                    success: function (response) {
                        if (response.status) {
                            var tag = '<option value="" selected="selected">-----</option>';
                            application_select_tag_obj.parent().next().children().append(tag);
                            $.each(response.data, function (index, item) {
                                var tag = '<option value="' + item.id + '">' + item.name + "</option>";
                                application_select_tag_obj.parent().next().children().append(tag);
                            })
                        }
                    },
                    error: function () {

                    }
                });
            } else {
                application_select_tag_obj.parent().next().children().empty();
                var tag = '<option value="" selected="selected">-----</option>';
                application_select_tag_obj.parent().next().children().append(tag);
            }
        });
    })
});