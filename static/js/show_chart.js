$(function () {
    var selectTag = $("#select-host").children().clone();
    // 选择主机组

    $("#select-host-group").on("change", function () {
        var hostGroupID = $("#select-host-group").val();
        if (hostGroupID === '0') {
            $("#select-host").empty();
            $("#select-host").append(selectTag);
            $("#select-host").val("0");
            $("#select-chart").empty();
            $("#select-chart").append('<option value="0">所有</option>');
            return false;
        } else {
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
                        $("#select-chart").empty();
                        $("#select-chart").append('<option value="0">所有</option>');
                    }
                },
                error: function () {

                }
            });
        }
    });

    // 选择主机
    $("#select-host").on("change", function () {
        var hostGroupID = $("#select-host-group").val();
        var hostID = $("#select-host").val();
        if (hostID === '0') {
            $("#select-chart").empty();
            $("#select-chart").append('<option value="0">所有</option>');
            return false;
        } else {
            $.ajax({
                url: "select_host_for_show_chart.html",
                type: "POST",
                dataType: "JSON",
                traditional: true,
                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                data: {"host_id": hostID, 'host_group_id': hostGroupID},
                success: function (response) {
                    if (response.status) {
                        $("#select-chart").empty();
                        var tag = '<option value="0">所有</option>';
                        $.each(response.data, function (index, item) {
                            tag += '<option value="' + item.id + '">' + item.name + "</option>";
                        });
                        $("#select-chart").append(tag);
                    }
                },
                error: function () {

                }
            });
        }
    });

    // 选择图
    $("#select-chart").on("change", function () {
        // 恢复默认5分钟按钮
        $("button[search-time='300']").removeClass("btn-default").siblings().addClass("btn-default");
        // 获取并渲染数据
        var chartID = $("#select-chart").val();
        var chartName = $("#select-chart").find("option:selected").text();
        var searchTime = parseInt($("button[search-time='300']").attr("search-time"));
        var hostID = $("#select-host").val();
        if (chartID === '0') {
            return false;
        } else {
            $.ajax({
                url: "select_chart_for_show_chart.html",
                type: "POST",
                dataType: "JSON",
                traditional: true,
                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                data: {
                    "chart_id": chartID,
                    "search_time": searchTime,
                    "host_id": hostID,
                    "chart_name": chartName
                },
                success: function (response) {
                    if (response.status) {
                        Highcharts.setOptions({
                            global: {
                                useUTC: false
                            }
                        });
                        var chartType = response.data.chart_type;
                        var chartTitle = response.data.chart_name;
                        var dataUnit = response.data.chart_data_unit;
                        if (chartType === 'line') {
                            $("#show-chart").highcharts({
                                chart: {
                                    type: chartType,
                                    events: {
                                        load: function () {
                                            var chart = this;
                                            $.each(response.data.chart_data, function (index, item) {
                                                chart.addSeries(
                                                    {name: item.name, data: item.data}
                                                );
                                            });

                                        }
                                    }
                                },
                                title: {
                                    text: chartTitle
                                },
                                xAxis: {
                                    type: "datetime",
                                    dateTimeLabelFormats: {
                                        millisecond: '%H:%M:%S',
                                        second: '%H:%M:%S',
                                        minute: '%H:%M:%S',
                                        hour: '%H:%M:%S',
                                        day: '%Y-%m-%d',
                                        month: '%Y-%m-%d',
                                        year: '%Y-%m-%d'
                                    },
                                    maxZoom: searchTime * 1000,
                                    tickPixelInterval: 120
                                },
                                yAxis: {
                                    title: {
                                        text: null
                                    },
                                    labels: {
                                        formatter: function () {
                                            return this.value + dataUnit;
                                        }
                                    }
                                },
                                tooltip: {
                                    formatter: function () {
                                        return '<b>' + this.series.name + '</b><br/>' +
                                            Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                            Highcharts.numberFormat(this.y, 2);
                                    }
                                },
                                series: [],
                                credits: {
                                    enabled: false // 禁用版权信息
                                }
                            });
                        } else if (chartType === 'area') {
                            $("#show-chart").highcharts({
                                chart: {
                                    type: chartType,
                                    events: {
                                        load: function () {
                                            var chart = this;
                                            $.each(response.data.chart_data, function (index, item) {
                                                chart.addSeries(
                                                    {name: item.name, data: item.data}
                                                );
                                            });

                                        }
                                    }
                                },
                                title: {
                                    text: chartTitle
                                },
                                xAxis: {
                                    type: "datetime",
                                    dateTimeLabelFormats: {
                                        millisecond: '%H:%M:%S',
                                        second: '%H:%M:%S',
                                        minute: '%H:%M:%S',
                                        hour: '%H:%M:%S',
                                        day: '%Y-%m-%d',
                                        month: '%Y-%m-%d',
                                        year: '%Y-%m-%d'
                                    },
                                    maxZoom: searchTime * 1000,
                                    tickPixelInterval: 120
                                },
                                yAxis: {
                                    title: {
                                        text: null
                                    },
                                    labels: {
                                        formatter: function () {
                                            return this.value + dataUnit;
                                        }
                                    }
                                },
                                tooltip: {
                                    formatter: function () {
                                        return '<b>' + this.series.name + '</b><br/>' +
                                            Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                            Highcharts.numberFormat(this.y, 2);
                                    }
                                },
                                series: [],
                                credits: {
                                    enabled: false // 禁用版权信息
                                }
                            });
                        }
                    }
                },
                error: function () {

                }
            });
        }
    });

    // 点击button按钮选择时间段
    $("button").click(function () {
        // 修改按钮样式
        $(this).removeClass("btn-default").siblings().addClass("btn-default");
        // 获取并渲染数据
        var chartID = $("#select-chart").val();
        var chartName = $("#select-chart").find("option:selected").text();
        var searchTime = parseInt($(this).attr("search-time"));
        var hostID = $("#select-host").val();
        if (chartID === '0') {
            return false;
        } else {
            $.ajax({
                url: "select_chart_for_show_chart.html",
                type: "POST",
                dataType: "JSON",
                traditional: true,
                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                data: {
                    "chart_id": chartID,
                    "search_time": searchTime,
                    "host_id": hostID,
                    "chart_name": chartName
                },
                success: function (response) {
                    if (response.status) {
                        Highcharts.setOptions({
                            global: {
                                useUTC: false
                            }
                        });
                        var chartType = response.data.chart_type;
                        var chartTitle = response.data.chart_name;
                        var dataUnit = response.data.chart_data_unit;
                        if (chartType === 'line') {
                            $("#show-chart").highcharts({
                                chart: {
                                    type: chartType,
                                    events: {
                                        load: function () {
                                            var chart = this;
                                            $.each(response.data.chart_data, function (index, item) {
                                                chart.addSeries(
                                                    {name: item.name, data: item.data}
                                                );
                                            });

                                        }
                                    }
                                },
                                title: {
                                    text: chartTitle
                                },
                                xAxis: {
                                    type: "datetime",
                                    dateTimeLabelFormats: {
                                        millisecond: '%H:%M:%S',
                                        second: '%H:%M:%S',
                                        minute: '%H:%M:%S',
                                        hour: '%H:%M:%S',
                                        day: '%Y-%m-%d',
                                        month: '%Y-%m-%d',
                                        year: '%Y-%m-%d'
                                    },
                                    maxZoom: searchTime * 1000,
                                    tickPixelInterval: 120
                                },
                                yAxis: {
                                    title: {
                                        text: null
                                    },
                                    labels: {
                                        formatter: function () {
                                            return this.value + dataUnit;
                                        }
                                    }
                                },
                                tooltip: {
                                    formatter: function () {
                                        return '<b>' + this.series.name + '</b><br/>' +
                                            Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                            Highcharts.numberFormat(this.y, 2);
                                    }
                                },
                                series: [],
                                credits: {
                                    enabled: false // 禁用版权信息
                                }
                            });
                        } else if (chartType === 'area') {
                            $("#show-chart").highcharts({
                                chart: {
                                    type: chartType,
                                    events: {
                                        load: function () {
                                            var chart = this;
                                            $.each(response.data.chart_data, function (index, item) {
                                                chart.addSeries(
                                                    {name: item.name, data: item.data}
                                                );
                                            });

                                        }
                                    }
                                },
                                title: {
                                    text: chartTitle
                                },
                                xAxis: {
                                    type: "datetime",
                                    dateTimeLabelFormats: {
                                        millisecond: '%H:%M:%S',
                                        second: '%H:%M:%S',
                                        minute: '%H:%M:%S',
                                        hour: '%H:%M:%S',
                                        day: '%Y-%m-%d',
                                        month: '%Y-%m-%d',
                                        year: '%Y-%m-%d'
                                    },
                                    maxZoom: searchTime * 1000,
                                    tickPixelInterval: 120
                                },
                                yAxis: {
                                    title: {
                                        text: null
                                    },
                                    labels: {
                                        formatter: function () {
                                            return this.value + dataUnit;
                                        }
                                    }
                                },
                                tooltip: {
                                    formatter: function () {
                                        return '<b>' + this.series.name + '</b><br/>' +
                                            Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                            Highcharts.numberFormat(this.y, 2);
                                    }
                                },
                                series: [],
                                credits: {
                                    enabled: false // 禁用版权信息
                                }
                            });
                        }
                    }
                },
                error: function () {

                }
            });
        }
    });
});