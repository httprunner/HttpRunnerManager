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
    data = $(id).serializeJSON();
    url = '/api/add_project/';
    if (id === '#add_module') {
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
    } else if (id.indexOf('un_pro') > -1) {
        url = '/api/project_list/1/';
        data = {
            "status": 0,
            "name": id.substring(6, id.length)
        };
    } else if (id.indexOf('in_pro') > -1) {
        url = '/api/project_list/1/';
        data = {
            "status": 1,
            "name": id.substring(6, id.length)
        };
    } else if (id.indexOf('un_mod') > -1) {
        url = '/api/module_list/1/';
        data = {
            "status": 0,
            "name": id.substring(6, id.length)
        };
    } else if (id.indexOf('in_mod') > -1) {
        url = '/api/module_list/1/';
        data = {
            "status": 1,
            "name": id.substring(6, id.length)
        };
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


function case_ajax() {
    var url = $("#url").serializeJSON();
    var method = $("#method").serializeJSON();
    var dataType = $("#DataType").serializeJSON();
    var caseInfo = $("#form_message").serializeJSON();
    var variables = $("#form_variables").serializeJSON();
    var request_data = $("#form_request_data").serializeJSON();
    var headers = $("#form_request_headers").serializeJSON();
    var extract = $("#form_extract").serializeJSON();
    var validate = $("#form_validate").serializeJSON();
    var test = {
        "test": {
            "name": caseInfo,
            "variables": variables,
            "setUp": {},
            "request": {
                "url": url.url,
                "method": method.method,
                "headers": headers,
                "type": dataType.DataType,
                "request_data": request_data
            },
            "tearDown": {},
            "extract": extract,
            "validate": validate

        }
    };

    $.ajax({
        type: 'post',
        url: '/api/add_case/',
        data: JSON.stringify(test),
        contentType: "application/json",
        success: function (data) {
            myAlert(data)
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}

function config_ajax() {
    var url = $("#config_url").serializeJSON();
    var dataType = $("#config_data_type").serializeJSON();
    var caseInfo = $("#form_config").serializeJSON();
    var variables = $("#config_variables").serializeJSON();
    var request_data = $("#config_request_data").serializeJSON();
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

    $.ajax({
        type: 'post',
        url: '/api/add_config/',
        data: JSON.stringify(config),
        contentType: "application/json",
        success: function (data) {
            myAlert(data)
        },
        error: function () {
            myAlert('Sorry，服务器可能开小差啦, 请重试!');
        }
    });
}

/*alert 弹出*/
function myAlert(data) {
    $('#my-alert_print').text(data);
    $('#my-alert').modal({
        relatedTarget: this
    });
}

