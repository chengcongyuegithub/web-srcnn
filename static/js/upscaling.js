$(document).ready(function () {
    $("#content").on('click', '#upscaling', function () {
        if ($("#upscalingMenu").length > 0) {
            return;
        }
        var times = "<select id=\"upscalingMenu\"> \n" +
            "<option value=\"1\">1x</option> \n" +
            "<option value=\"2\">2x</option> \n" +
            "<option value=\"3\">3x</option> \n" +
            "</select> "
        $('#times').append(times)
    })
    $("#content").on('click', '#upscalingMenu', function () {
        var times = $("#upscalingMenu option:selected").val();
        if (parseInt(times) == 1) {
            return;
        }
        var picname = $("#picname").val();
        $.ajax({
            url: '/upscaling',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                "times": times,
                "picname": picname
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                if (res['code'] == '200') {
                    var picContent = "<div><p>图片名称:" + res['name'] + "</p>\n" +
                        "<p>图片如下所示:</p><div id='" + res['id'] + "_" + res['action'] + "' class=\"imgDiv\">" +
                        "<img src='" + res['url'] + "'/><span class=\"delete\" >+</span></div>\n" +
                        "<h1>上面的图片是" + res['action'] + "的图片</h1></div>";
                    $("#content").append(picContent)
                } else {
                    alert('图片已经处理过了,请选择其他的操作')
                }
            }
        })
    });
})