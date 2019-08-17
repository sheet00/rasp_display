var main = {};

main.init = function () {
    main.reload(60);
    main.draw_chart();
};

main.reload = function (wait_second) {
    var second = wait_second * 1000
    setTimeout(function () { window.location.reload(); }, second);
};

main.draw_chart = function (data) {
    var temps = $.parseJSON($("#json_temps").text());
    var hums = $.parseJSON($("#json_hums").text());
    var created_at = $.parseJSON($("#json_created_at").text());

    const FONT_SIZE = '20px'
    var myChart = Highcharts.chart('graph', {
        chart: {
            type: 'line'
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: created_at,
            labels: {
                style: {
                    fontSize: FONT_SIZE // x軸の値の文字サイズ
                }
            }
        },
        yAxis: {
            title: { text: '' },
            labels: {
                style: {
                    fontSize: FONT_SIZE // x軸の値の文字サイズ
                }
            }
        },
        plotOptions: {
            series: {
                marker: { enabled: false },
                dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: FONT_SIZE
                    }
                }
            }
        },
        series: [{
            name: 'temp',
            data: temps
        }]
    })
};
