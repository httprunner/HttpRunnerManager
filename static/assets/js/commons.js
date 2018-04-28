/*动态改变模块信息*/
function show_module(module_info) {
    module_info = module_info.split('replaceFlag');
    var a = $("#belong_module_id");
    a.empty();
    for (var i = 0; i < module_info.length; i++) {
        var value = module_info[i];
        a.prepend("<option value='" + value + "' >" + value + "</option>")
    }

}

/*表单信息异步传输*/
function info_ajax(id, url) {
    var data = $(id).serializeJSON();
    if (id === '#form_message') {
        data = {
            "test": {
                "name": data
            }
        }
    }
    else if (id === '#form_config') {
        data = {
            "config": {
                "name": data
            }
        }
    }
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            if (id !== '#form_message' && id !== '#form_config') {
                if (data !== 'ok') {
                    myAlert(data);
                }
                else {
                    window.location.reload();
                }
            }
            else {
                show_module(data)
            }
        }
        ,
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });

}

function update_data_ajax(id, url) {
    var data = $(id).serializeJSON();
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            if (data !== 'ok') {
                myAlert(data);
            }
            else {
                window.location.reload();
            }
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}

function del_data_ajax(id, url) {
    var data = {
        "id": id,
        'mode': 'del'
    };
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            if (data !== 'ok') {
                myAlert(data);
            }
            else {
                window.location.reload();
            }
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}

function case_ajax(type) {
    var url = $("#url").serializeJSON();
    var method = $("#method").serializeJSON();
    var dataType = $("#DataType").serializeJSON();
    var caseInfo = $("#form_message").serializeJSON();
    var variables = $("#form_variables").serializeJSON();
    var request_data = null;
    if (dataType.DataType == 'json') {
        request_data = eval('(' + $('#json-input').val() + ')');
    } else {
        request_data = $("#form_request_data").serializeJSON();
    }
    var headers = $("#form_request_headers").serializeJSON();
    var extract = $("#form_extract").serializeJSON();
    var validate = $("#form_validate").serializeJSON();
    // var setup = $("#form_setup").serializeJSON();
    // var teardown = $("#form_teardown").serializeJSON();
    var test = {
        "test": {
            "name": caseInfo,
            "variables": variables,
            "request": {
                "url": url.url,
                "method": method.method,
                "headers": headers,
                "type": dataType.DataType,
                "request_data": request_data
            },
            "extract": extract,
            "validate": validate

        }
    };
    if (type === 'edit') {
        url = '/api/edit_case/';
    } else {
        url = '/api/add_case/';
    }
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(test),
        contentType: "application/json",
        success: function (data) {
            if (data === 'session invalid') {
                window.location.href = "/api/login/";
            } else {
                myAlert(data)
            }
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}

function config_ajax(type) {
    var dataType = $("#config_data_type").serializeJSON();
    var caseInfo = $("#form_config").serializeJSON();
    var variables = $("#config_variables").serializeJSON();
    var request_data = null;
    if (dataType.DataType === 'json') {
        request_data = eval('(' + $('#json-input').val() + ')');
    } else {
        request_data = $("#config_request_data").serializeJSON();
    }
    var headers = $("#config_request_headers").serializeJSON();
    var config = {
        "config": {
            "name": caseInfo,
            "variables": variables,
            "request": {
                "headers": headers,
                "type": dataType.DataType,
                "request_data": request_data
            }
        }
    };
    if (type === 'edit') {
        url = '/api/edit_config/1/';
    } else {
        url = '/api/add_config/';
    }
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(config),
        contentType: "application/json",
        success: function (data) {
            if (data === 'session invalid') {
                window.location.href = "/api/login";
            } else {
                myAlert(data)
            }
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}

/*提示 弹出*/
function myAlert(data) {
    $('#my-alert_print').text(data);
    $('#my-alert').modal({
        relatedTarget: this
    });
}

function post(url, params) {
    var temp = document.createElement("form");
    temp.action = url;
    temp.method = "post";
    temp.style.display = "none";
    for (var x in params) {
        var opt = document.createElement("input");
        opt.name = x;
        opt.value = params[x];
        temp.appendChild(opt);
    }
    document.body.appendChild(temp);
    temp.submit();
    return temp;
}

function del_row(id) {
    var attribute = id;
    var chkObj = document.getElementsByName(attribute);
    var tabObj = document.getElementById(id);
    for (var k = 0; k < chkObj.length; k++) {
        if (chkObj[k].checked) {
            tabObj.deleteRow(k + 1);
            k = -1;
        }
    }
}


function add_row(id) {
    var tabObj = document.getElementById(id);//获取添加数据的表格
    var rowsNum = tabObj.rows.length;  //获取当前行数
    var style = 'width:100%; border: none';
    var cell_check = "<input type='checkbox' name='" + id + "' style='width:55px' />";
    var cell_key = "<input type='text' name='test[][key]'  value='' style='" + style + "' />";
    var cell_value = "<input type='text' name='test[][value]'  value='' style='" + style + "' />";
    var cell_type = "<select name='test[][type]' class='form-control' style='height: 25px; font-size: 15px; " +
        "padding-top: 0px; padding-left: 0px; border: none'> " +
        "<option>string</option><option>int</option><option>float</option><option>boolean</option></select>";
    var cell_comparator = "<select name='test[][comparator]' class='form-control' style='height: 25px; font-size: 15px; " +
        "padding-top: 0px; padding-left: 0px; border: none'> " +
        "<option>equals</option> <option>contains</option> <option>startswith</option> <option>endswith</option> <option>regex_match</option> <option>type_match</option> <option>contained_by</option> <option>less_than</option> <option>less_than_or_equals</option> <option>greater_than</option> <option>greater_than_or_equals</option> <option>not_equals</option> <option>string_equals</option> <option>length_equals</option> <option>length_greater_than</option> <option>length_greater_than_or_equals</option> <option>length_less_than</option> <option>length_less_than_or_equals</option></select>";

    var myNewRow = tabObj.insertRow(rowsNum);
    var newTdObj0 = myNewRow.insertCell(0);
    var newTdObj1 = myNewRow.insertCell(1);
    var newTdObj2 = myNewRow.insertCell(2);


    newTdObj0.innerHTML = cell_check
    newTdObj1.innerHTML = cell_key;
    if (id === 'variables' || id === 'data') {
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj2.innerHTML = cell_type;
        newTdObj3.innerHTML = cell_value;
    } else if (id === 'validate') {
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj2.innerHTML = cell_comparator;
        newTdObj3.innerHTML = cell_type;
        var newTdObj4 = myNewRow.insertCell(4);
        newTdObj4.innerHTML = cell_value;
    } else {
        newTdObj2.innerHTML = cell_value;
    }
}

