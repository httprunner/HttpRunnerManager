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
function info_ajax(id) {
    var data = $(id).serializeJSON();
    var url;
    if (id === '#add_project') {
        url = '/api/add_project/';
    } else if (id === '#add_module') {
        url = '/api/add_module/';
    } else if (id === '#list_pro') {
        url = '/api/project_list/1/';
    } else if (id === '#list_module') {
        url = '/api/module_list/1/';
    } else if (id === '#form_message') {
        url = '/api/add_case/';
        data = {
            "test": {
                "name": data
            }
        }
    } else if (id === '#form_config') {
        url = '/api/add_config/';
        data = {
            "config": {
                "name": data
            }
        }
    } else {
        data = {
            "status": 0,
            "name": id.substring(6, id.length)
        };
        if (id.indexOf('un_pro') > -1) {
            url = '/api/project_list/1/';
        } else if (id.indexOf('un_mod') > -1) {
            url = '/api/module_list/1/';
        } else if (id.indexOf('un_tec') > -1) {
            url = '/api/test_list/1/';
        } else {
            data = {
                "status": 1,
                "name": id.substring(6, id.length)
            };
            if (id.indexOf('in_pro') > -1) {
                url = '/api/project_list/1/';
            } else if (id.indexOf('in_mod') > -1) {
                url = '/api/module_list/1/';
            } else if (id.indexOf('in_tec') > -1) {
                url = '/api/test_list/1/';
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
                myAlert(data);
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
    var setup = $("#form_setup").serializeJSON();
    var teardown = $("#form_teardown").serializeJSON();
    var test = {
        "test": {
            "name": caseInfo,
            "variables": variables,
            "setup": setup,
            "request": {
                "url": url.url,
                "method": method.method,
                "headers": headers,
                "type": dataType.DataType,
                "request_data": request_data
            },
            "teardown": teardown,
            "extract": extract,
            "validate": validate

        }
    };
    if (type === 'edit') {
        url = '/api/edit_case/1/';
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

function config_ajax(type) {
    var url = $("#config_url").serializeJSON();
    var dataType = $("#config_data_type").serializeJSON();
    var caseInfo = $("#form_config").serializeJSON();
    var variables = $("#config_variables").serializeJSON();
    var request_data = null;
    if (dataType.DataType == 'json') {
        request_data = eval('(' + $('#json-input').val() + ')');
    } else {
        request_data = $("#form_request_data").serializeJSON();
    }
    var headers = $("#config_request_headers").serializeJSON();
    var config = {
        "config": {
            "name": caseInfo,
            "variables": variables,
            "request": {
                "base_url": url.url,
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

index = 100;//全局变量很重要！！

function add_row(id) {
    var tabObj = document.getElementById(id);//获取添加数据的表格
    var rowsNum = tabObj.rows.length;  //获取当前行数
    var attribute = id;
    var style = 'width:100%; border: none';
    var cellHtml1 = "<input type='text' name='cell1_key" + id + index + "'  value='' style='" + style + "' />";
    var cellHtml2 = "<input type='text' name='cell2_value" + id + index + "' value='' style='" + style + "' />";
    var cellHtml3 = "<input type='text' name='cell3_value" + id + index + "' value='' style='" + style + "' />";

    var cellDataType = "<select name='cell_data_type" + id + index + "' class='form-control' style='height: 25px; font-size: 15px; " +
        "padding-top: 0px; padding-left: 0px; border: none'> " +
        "<option>string</option><option>int</option><option>float</option><option>boolean</option></select>";

    var myNewRow = tabObj.insertRow(rowsNum);
    var newTdObj0 = myNewRow.insertCell(0);
    var newTdObj1 = myNewRow.insertCell(1);
    var newTdObj2 = myNewRow.insertCell(2);


    newTdObj0.innerHTML = "<input type='checkbox' name='" + attribute + "' id='chkArr_" + index + "' style='width:55px' />";
    newTdObj1.innerHTML = cellHtml1;
    if (id === 'variables' || id === 'data') {
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj2.innerHTML = cellDataType;
        newTdObj3.innerHTML = cellHtml3;
    } else if (id === 'validate') {
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj2.innerHTML = "<select name='cell_2comparator" + id + index + "' class='form-control' style='height: 25px; font-size: 15px; " +
            "padding-top: 0px; padding-left: 0px; border: none'> " +
            "<option>equals</option> <option>contains</option> <option>startswith</option> <option>endswith</option> <option>regex_match</option> <option>type_match</option> <option>contained_by</option> <option>less_than</option> <option>less_than_or_equals</option> <option>greater_than</option> <option>greater_than_or_equals</option> <option>not_equals</option> <option>string_equals</option> <option>length_equals</option> <option>length_greater_than</option> <option>length_greater_than_or_equals</option> <option>length_less_than</option> <option>length_less_than_or_equals</option></select>";

        newTdObj3.innerHTML = cellDataType;
        var newTdObj4 = myNewRow.insertCell(4);
        newTdObj4.innerHTML = cellHtml3;
    } else {
        newTdObj2.innerHTML = cellHtml2;
    }
    index++;
}



