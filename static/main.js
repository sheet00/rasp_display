var main = {};

main.init = function () {
    main.reload(60);
    main.draw_chart();

    $('.container :not(#news)').on('click', function () {
        $('#graph').toggle();
    })

    main.auto_toggle(15);
};

main.reload = function (wait_second) {
    var second = wait_second * 1000
    setTimeout(function () { window.location.reload(); }, second);
};

main.auto_toggle = async function (switch_second) {
    var second = switch_second * 1000
    //wait
    await main.sleep(second);

    //toggle
    main.loopSleep(10, second, function (i) {
        $('#graph').toggle();
    })
};

main.sleep = function sleep(msec) {
   return new Promise(function(resolve) {
      setTimeout(function() {resolve()}, msec);
   })
}

main.loopSleep = function (_loopLimit, _interval, _mainFunc) {
    var loopLimit = _loopLimit;
    var interval = _interval;
    var mainFunc = _mainFunc;
    var i = 0;
    var loopFunc = function () {
        var result = mainFunc(i);
        if (result === false) {
            // break機能
            return;
        }
        i = i + 1;
        if (i < loopLimit) {
            setTimeout(loopFunc, interval);
        }
    }
    loopFunc();
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
