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
            url: "select_host_group_for_show_chart.html",
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
            $("#select-template").empty();
            $("#select-template").append('<option value="0">所有</option>');
            return false;
        }
        $.ajax({
            url: "select_host_for_show_chart.html",
            type: "POST",
            dataType: "JSON",
            traditional: true,
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"host_id": hostID, 'host_group_id': hostGroupID},
            success: function (response) {
                if (response.status) {
                    $("#select-template").empty();
                    var tag = '<option value="0">所有</option>';
                    $.each(response.data, function (index, item) {
                        tag += '<option value="' + item.id + '">' + item.name + "</option>"
                    });
                    $("#select-template").append(tag);
                }
            },
            error: function () {

            }
        });
    });

    // 选择模板
    $("#select-template").on("change", function () {
        var templateID = $("#select-template").val();
        if (templateID === '0') {
            $("#select-chart").empty();
            $("#select-chart").append('<option value="0">所有</option>');
            return false;
        }
        $.ajax({
            url: "select_template_for_show_chart.html",
            type: "POST",
            dataType: "JSON",
            traditional: true,
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"template_id": templateID},
            success: function (response) {
                if (response.status) {
                    $("#select-chart").empty();
                    var tag = '<option value="0">所有</option>';
                    $.each(response.data, function (index, item) {
                        tag += '<option value="' + item.id + '">' + item.name + "</option>"
                    });
                    $("#select-chart").append(tag);
                }
            },
            error: function () {

            }
        });
    });

    // 选择
    $("#select-chart").on("change", function () {
        var chartID = $("#select-chart").val();
        var searchTime = parseInt($("#search-time-5-minute").attr("search-time"));
        if (chartID === '0') {
            $("#show_chart").empty();
            return false;
        }
        $.ajax({
            url: "select_chart_for_show_chart.html",
            type: "POST",
            dataType: "JSON",
            traditional: true,
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            data: {"chart_id": chartID, "search_time": searchTime},
            success: function (response) {
                if (response.status) {
                    Highcharts.setOptions({
                        global: {
                            useUTC: false
                        }
                    });
                    function activeLastPointToolip(chart) {
                        var points = chart.series[0].points;
                        chart.tooltip.refresh(points[points.length - 1]);
                    }

                    $("#show-chart").highcharts({
                        chart: {
                            type: 'spline',
                            events: {
                                load: function () {
                                    var series = this.series[0],
                                        chart = this;
                                    activeLastPointToolip(chart);
                                    setInterval(function () {
                                        var x = (new Date()).getTime(), // 当前时间
                                            y = Math.random();          // 随机值
                                        series.addPoint([x, y], true, true);
                                        activeLastPointToolip(chart);
                                    }, 1000);
                                }
                            }
                        },
                        title: {
                            text: response.data.chart_name
                        },
                        xAxis: {
                            type: 'datetime',
                            maxZoom: searchTime * 60 * 1000,
                            tickPixelInterval: 100
                        },
                        yAxis: {
                            title: {
                                text: null
                            }
                        },
                        tooltip: {
                            formatter: function () {
                                return '<b>' + this.series.name + '</b><br/>' +
                                    Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                    Highcharts.numberFormat(this.y, 2);
                            }
                        },
                        legend: {
                            enabled: true
                        },
                        series: [{
                            name: '随机数据',
                            data: (function () {
                                // 生成随机值
                                var data = [],
                                    time = (new Date()).getTime(),
                                    i;
                                for (i = -19; i <= 0; i += 1) {
                                    data.push({
                                        x: time + i * 1000,
                                        y: Math.random()
                                    });
                                }
                                return data;
                            }())
                        }]
                    });
                }
            },
            error: function () {

            }
        });
    });
});