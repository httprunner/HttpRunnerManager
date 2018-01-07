function addNewRow(id) {
    var tabObj = document.getElementById(id);//获取添加数据的表格
    var rowsNum = tabObj.rows.length;  //获取当前行数
    var attribute = 'variables';
    if (id === 'data') {
        attribute = 'data';
    } else if (id === 'header') {
        attribute = 'header';
    } else if (id === 'extract') {
        attribute = 'extract';
    } else if (id === 'validate') {
        attribute = 'validate';
    }
    var cellHtml1 = "<input type='text' name='cell1_key" + id + rowsNum + "' id='nodename " + rowsNum + "' value='' style='width:100%; border: none' />";
    var cellHtml2 = "<input type='text' name='cell2_value" + id + rowsNum + "' id='nodename " + rowsNum + "' value='' style='width:100%; border: none' />";
    var cellHtml3 = "<input type='text' name='cell3_value" + id + rowsNum + "' id='nodename " + rowsNum + "' value='' style='width:100%; border: none' />";
    var myNewRow = tabObj.insertRow(rowsNum);
    var newTdObj0 = myNewRow.insertCell(0);
    var newTdObj1 = myNewRow.insertCell(1);
    var newTdObj2 = myNewRow.insertCell(2);
    newTdObj0.innerHTML = "<input type='checkbox' name='" + attribute + "' id='chkArr_" + rowsNum + "' style='width:55px' />";
    newTdObj1.innerHTML = cellHtml1;
    if (id !== 'validate') {
        newTdObj2.innerHTML = cellHtml2;
    } else {
        newTdObj2.innerHTML = "<select name='cell_2comparator" + id + rowsNum + "' class='form-control' style='height: 25px; font-size: 15px; " +
            "padding-top: 0px; padding-left: 0px; border: none'> " +
            "<option>eq</option> <option>contains</option> " +
            "<option>lg</option> <option>gt</option> </select>";
        var newTdObj3 = myNewRow.insertCell(3);
        newTdObj3.innerHTML = cellHtml3;
    }

}

/*表格删除行*/
function removeRow(id) {
    var attribute = 'variables';
    if (id === 'data') {
        attribute = 'data';
    } else if (id === 'header') {
        attribute = 'header';
    } else if (id === 'extract') {
        attribute = 'extract';
    } else if (id === 'validate') {
        attribute = 'validate';
    }
    var chkObj = document.getElementsByName(attribute);
    var tabObj = document.getElementById(id);
    for (var k = 0; k < chkObj.length; k++) {
        if (chkObj[k].checked) {
            tabObj.deleteRow(k + 1);
            k = -1;
        }
    }
}

/*动态改变模块信息*/
function show_module(module_info) {
    module_info = module_info.split('replaceFlag');
    var a =  $("#belong_module_id");
    a.empty();
    for(var i = 0; i < module_info.length; i++) {
        var value = module_info[i];
        a.prepend("<option value='"+value+"' >"+value+"</option>")
    }

}

/*表单信息异步传输*/
function info_ajax(id) {
    data = $(id).serializeJSON();
    url = '/api/add_project/';
    if (id === '#add_module') {
        url = '/api/add_module/';
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
    }

    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            if (id !== '#form_message' && id !=='#form_config') {
                alert(data)
            } else {
                show_module(data)
            }
        },
        error: function () {
            alert('系统繁忙，请稍候重试')
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
            alert(data)
        },
        error: function () {
            alert('系统繁忙，请稍候重试')
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
            alert(data)
        },
        error: function () {
            alert('系统繁忙，请稍候重试')
        }
    });
}

