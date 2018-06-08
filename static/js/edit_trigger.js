$(function () {
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
        var tag = $("#example").clone();
        tag.removeAttr('style');
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

$(function () {
    $("form").submit(function () {
        $("select[name='templates_id']").removeAttr("disabled");
    });
});