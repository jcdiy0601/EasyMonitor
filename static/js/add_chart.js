$(function () {
    var templateID = $("select[name='templates_id']").val();
    $.ajax({
        url: "get_application.html",
        type: "POST",
        dataType: "JSON",
        traditional: true,
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        data: {"template_id": templateID},
        success: function (response) {
            if (response.status) {
                $.each(response.data, function (index, item) {
                    if (index === 0) {
                        applicationID = item.id;
                        var tag = '<option selected="selected" value="' + item.id + '">' + item.name + "</option>";
                    } else {
                        var tag = '<option value="' + item.id + '">' + item.name + "</option>";
                    }
                    $("select[name='applications_id']").append(tag);
                });
                $.ajax({
                        url: "get_item.html",
                        type: "POST",
                        dataType: "JSON",
                        traditional: true,
                        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                        data: {"application_id": applicationID},
                        success: function (response) {
                            if (response.status) {
                                $("select[name='item_id']").empty();
                                $.each(response.data, function (index, item) {
                                    var tag = '<option value="' + item.id + '">' + item.name + " " + item.key + "</option>";
                                    $("select[name='item_id']").append(tag);
                                });
                            }
                        },
                        error: function () {

                        }
                    }
                );
            }
        },
        error: function () {

        }
    });
});

$(function () {
    $("select[name='templates_id']").on("change", function () {
        var templateID = $("select[name='templates_id']").val();
        $("select[name='applications_id']").empty();
        $.ajax({
            url: "get_application.html",
            type: "POST",
            dataType: "JSON",
            traditional: true,
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"template_id": templateID},
            success: function (response) {
                if (response.status) {
                    console.log(111);
                    console.log(response.data);
                    if (response.data.length === 0) {
                        console.log(222);
                        $.each(response.data, function (index, item) {
                            if (index === 0) {
                                applicationID = item.id;
                                var tag = '<option selected="selected" value="' + item.id + '">' + item.name + "</option>";
                            } else {
                                var tag = '<option value="' + item.id + '">' + item.name + "</option>";
                            }
                            $("select[name='applications_id']").append(tag);
                        });
                        $.ajax({
                                url: "get_item.html",
                                type: "POST",
                                dataType: "JSON",
                                traditional: true,
                                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                                data: {"application_id": applicationID},
                                success: function (response) {
                                    if (response.status) {
                                        $("select[name='item_id']").empty();
                                        $.each(response.data, function (index, item) {
                                            var tag = '<option value="' + item.id + '">' + item.name + " " + item.key + "</option>";
                                            $("select[name='item_id']").append(tag);
                                        });
                                    }
                                },
                                error: function () {

                                }
                            }
                        );
                    } else {
                        console.log(333);
                        $("select[name='item_id']").empty();
                        return false;
                    }

                }
            },
            error: function () {

            }
        });
    })
});