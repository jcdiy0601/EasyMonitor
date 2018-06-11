$(function () {
    $("input[name='enabled']").click(function () {
        if ($("input[name='enabled']").prop("checked")) {
            $("input[name='enabled']").val("True");
        } else {
            $("input[name='enabled']").val("False");
        }
    });

    $("input[name='recover_notice']").click(function () {
        if ($("input[name='recover_notice']").prop("checked")) {
            $("input[name='recover_notice']").val("True");
        } else {
            $("input[name='recover_notice']").val("False");
        }
    })
});