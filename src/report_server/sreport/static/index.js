var first_logged_in = false;
var logged_in = false;
var csrftoken = '';
var page_size = 10; // default value

$(document).ready(function() {
    csrftoken = getCookie('csrftoken');
    setupLoginForm();
    setupLLButtons();
    setupNavButtons();
    setupCreateForm();
    openCreate();
    $('#login-button').click(login);
    $('#logout-button').click(logout);

    // initially hide instance detail section
    $('#instance_details').hide();

    // Disable appropriate nav tabs 
    $('#report_button').addClass('disabled');
    $('#detail_button').addClass('disabled');
    $('#max_button').addClass('disabled');

    $('#report_button').off('click');
    $('#detail_button').off('click');
    $('#max_button').off("click");

    $('#contract').change(function() {
        $('#rhic').val('').trigger('liszt:updated');
    });

    $('#rhic').change(function() {
        $('#contract').val('null').trigger('liszt:updated');
    });

    $("#byMonth").change(function() {
        $("#startDate").val('').trigger('liszt:updated');
        $("#endDate").val('').trigger('liszt:updated');
    });

    $("#startDate").change(function() {
        $("#byMonth").val('').trigger('liszt:updated');
    });

    $("#endDate").change(function() {
        $("#byMonth").val('').trigger('liszt:updated');
    });

    /*
    $("#export").button().click(function() {
      // Have to stop url from changing so disable default event
        event.preventDefault();
            // Build up var
            var data = {}; 
       
            // Date section
            if($.trim($('#byMonth').val()) != "-1") {
                data['byMonth'] = $('#byMonth').val();
            }
            if($.trim($('#startDate').val()) != "") {
                data['startDate'] = $('#startDate').val();
                data['endDate'] = $('#endDate').val();
            }
            if($.trim($('#contract').val()) != "") {
                data['contract_number'] = $('#contract').val();
            }
            if($.trim($('#rhic').val()) != "") {
                data['rhic'] = $('#rhic').val();
            }

            data['env'] = $('#env').val();
           
            $.download('/report-server/ui20/export', data, 'get');

    })
    */
    
});


function login() {
    $('#login-form').dialog('open');
}

function logout() {
    $.ajax({
        url: '/report-server/ui20/logout/',
        type: 'POST',
        contentType: 'application/json',
        data: {},
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }).done(function(data) {
        enableButton($('#login-button'));
        disableButton($('#logout-button'));
        // alter msg
        $('#account-links > span > p').text('You are not logged in.');

        logged_in = false;

        loadContent();
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}

function setupLLButtons() {
    if (first_logged_in) {
        disableButton($('#login-button'));
        logged_in = true;
    } else {
        disableButton($('#logout-button'));
        logged_in = false;
    }
    loadContent();
    $('#login-error').hide();
}

function setupNavButtons() {
    $('#create_button').on("click", openCreate);
    $('#report_button').on("click", openReport);
    $('#detail_button').on("click", openDetail);
    $('#import_button').on("click", openImport);
    $('#max_button').on("click", openMax);
}

function setupCreateForm() {
    $('#report_form').each(function() {
        this.reset();
    });

    $('#startDate').attr('disabled', false);
    $('#endDate').attr('disabled', false);
    $('#rhic').attr('disabled', false);
    $('#contract').attr('disabled', false);
    $("#startDate").attr('disabled', false);
    $("#endDate").attr('disabled', false);
    $("#byMonth").attr('disabled', false);
    $("#env").attr('disabled', false);


    $('#startDate').datepicker();
    $('#endDate').datepicker();

    setupCreateFormButtons();

    $.ajax({
        url: '/report-server/ui20/report_form/',
        type: 'GET',
        contentType: 'application/json',
        data: {},
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }).done(function(data) {
        fill_create_report_form(JSON.parse(data));
        //fill_create_report_rhic_form(JSON.parse(data));
        $('#contract').chosen();
        $('#rhic').chosen();
        $('#byMonth').chosen();
        $('#env').chosen();
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}


function setupCreateFormButtons() {
    var btn = $('#clear');
    var o = $('#original');
    var c = $('#choices');
    // Initially hide the choices
    c.hide();
}

function createReport(event) {
    // Have to stop url from changing so disable default event
    event.preventDefault();

    if (logged_in && validateForm()) {
        // Build up var
        var data = {}; 

        // Date section
        if($.trim($('#byMonth').val()) != "-1") {
            data['byMonth'] = $('#byMonth').val();
        }
        if($.trim($('#startDate').val()) != "") {
            data['startDate'] = $('#startDate').val();
            data['endDate'] = $('#endDate').val();
        }
        if($.trim($('#contract').val()) != "") {
            data['contract_number'] = $('#contract').val();
        }
        if($.trim($('#rhic').val()) != "") {
            data['rhic'] = $('#rhic').val();
        }

        data['env'] = $('#env').val();

        $.ajax({
            url: '/report-server/ui20/report/',
            type: 'POST',
            contentType: 'application/json',
            data: data,
            crossDomain: false,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        }).done(function(data) {
            var rtn = jQuery.parseJSON(data);
            populateReport(rtn);
            openReport();
            // Attach the event handler back on
            $('#report_button').on("click", openReport);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // TODO: Add error handling here
        });
    }
}



function exportReport(event) {
 //Have to stop url from changing so disable default event
	event.preventDefault();
    // Build up var
    var data = {}; 

     // Date section
     if($.trim($('#byMonth').val()) != "-1") {
         data['byMonth'] = $('#byMonth').val();
     }
     if($.trim($('#startDate').val()) != "") {
         data['startDate'] = $('#startDate').val();
         data['endDate'] = $('#endDate').val();
     }
     if($.trim($('#contract').val()) != "") {
         data['contract_number'] = $('#contract').val();
     }
      if($.trim($('#rhic').val()) != "") {
         data['rhic'] = $('#rhic').val();
     }

     data['env'] = $('#env').val();
     
     $.download('/report-server/ui20/export', data, 'get');

 }

$.download = function(url, data, method){
    //url and data options required
    
        //data can be string of parameters or array/object
        data = typeof data == 'string' ? data : jQuery.param(data);
        //split params into form inputs
        var inputs = '';
        jQuery.each(data.split('&'), function(){ 
            var pair = this.split('=');
            inputs+='<input type="hidden" name="'+ pair[0] +'" value="'+ pair[1] +'" />'; 
        });
        //send request
        //alert("url:" + url + "data: " + data);
        var url = '/report-server/ui20/export/';
       //send request
        jQuery('<form action="/report-server/ui20/export/" method="'+ ('get') +'">'+inputs+'</form>')
        .appendTo('body').submit().remove();
        //alert('Please wait while the export is generated')

};

function resetReportForm(event) {
    $('#report_pane > div').empty();
    $('#report_pane > div').append($('<h3>This date range contains no usage data.</h3>'));
    $('#report_pane > div').append($('<br></br>'));
    $('#report_pane > div').append($('<br></br>'));
    $('#details > table').empty();
    $('#instance_details').empty();
    $('#max_details').empty();


    // Disable appropriate nav tabs 
    $('#report_button').addClass('disabled');
    $('#detail_button').addClass('disabled');
    $('#max_button').addClass('disabled');

    $('#report_button').off('click');
    $('#detail_button').off('click');
    $('#max_button').off("click");
}

// There has to be a better way to make the
// next four function generic.

function openCreate() {
    removeActiveNav();
    $('#create_button').addClass('active');

    if (logged_in) {
        $('#create_pane').show();
        $('#report_pane').hide();
        $('#detail_pane').hide();
        $('#max_pane').hide();
        $('#import_pane').hide();

    }
}

function openReport() {
    $('#report_button').removeClass('disabled');
    removeActiveNav();
    $('#report_button').addClass('active');;
    $('#create_pane').hide();
    $('#report_pane').hide();
    $('#detail_pane').hide();
    $('#import_pane').hide();
    $('#max_pane').hide();
    $('#report_pane').show();

}

function openDetail() {
    $('#detail_button').removeClass('disabled');
    removeActiveNav();
    $('#detail_button').addClass('active');
    $('#create_pane').hide();
    $('#report_pane').hide();
    $('#detail_pane').hide();
    $('#import_pane').hide();
    $('#max_pane').hide();
    $('#detail_pane').show();

}

function openMax() {
    $('#max_button').removeClass('disabled');
    removeActiveNav();
    $('#max_button').addClass('active');
    if (logged_in) {
        $('#create_pane').hide();
        $('#report_pane').hide();
        $('#detail_pane').hide();
        $('#max_pane').hide();
        $('#import_pane').hide();
        $('#max_pane').show();
    }
}

function openImport() {
    removeActiveNav();
    $('#import_button').addClass('active');

    if (logged_in) {
        $('#create_pane').hide();
        $('#report_pane').hide();
        $('#detail_pane').hide();
        $('#max_pane').hide();
        $('#import_pane').show();

    }
}

function createDetail(start, end, description,  filter_args) {
    var data = {
        "start": start,
        "end": end,
        "description": description,
        "filter_args_dict": unescape(filter_args)
    };

    $.ajax({
        url: '/report-server/ui20/details/',
        type: 'POST',
        contentType: 'application/json',
        data: data,
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }).done(function(data) {
        var rtn = jQuery.parseJSON(data);
        openDetail();
        populateDetailReport(rtn);
        createMax(start, end, description,  filter_args);
        

        $('#detail_button').removeClass('disabled');
        $('#detail_button').on("click", openDetail);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}



function createMax(start, end, description, filter_args) {
    var data = {
        "start": start,
        "end": end,
        "description": description,
        "filter_args_dict": unescape(filter_args)
    };

    $.ajax({
        url: '/report-server/ui20/max_report/',
        type: 'POST',
        contentType: 'application/json',
        data: data,
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
    }
    }).done(function(data) {
        var rtn = jQuery.parseJSON(data);
        openMax();
        populateMaxReport(rtn);
        openDetail(); //also should not be needed :) jumps back from max to detail
        $('#max_button').on("click", openMax);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}

function createInstanceDetail(start, end, instance, filter_args) {
    var data = {
        "start": start,
        "end": end,
        "instance": instance,
        "filter_args_dict": unescape(filter_args)
    };

    $.ajax({
        url: '/report-server/ui20/instance_details/',
        type: 'POST',
        contentType: 'application/json',
        data: data,
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }).done(function(data) {
        var rtn = jQuery.parseJSON(data);
        populateInstanceDetailReport(rtn);
        openDetail(); // this shouldn't be needed, but no harm in calling it again
        $('#detail_button').on("click", openDetail);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}

function importData() {
    if (logged_in) {
        $('#import_pane > div').empty();
        $('#import_pane > button').empty();
        var status = $('<span class=\'ui-button-text\'>Working on it...</span>');
        $('#import_pane > button').append(status);

        $.ajax({
            url: '/report-server/ui20/import/',
            type: 'POST',
            contentType: 'application/json',
            data: {},
            crossDomain: false,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        }).done(function(data) {
            var rtn = jQuery.parseJSON(data);


            var dt = rtn.time[0];
            if (dt.end < 0){
            var status = $('<span>Import Skipped, import has been executed in the last 45 minutes<span>');
            $('#import_pane > div').append(status);
            }
            else { 
            $('#import_pane > div').empty();
            var status = $('<span>Import Complete!\nStart Time: ' + dt.start + '\nEnd Time: ' + dt.end + '<span>');
            $('#import_pane > div').append(status);
            }
            $('#import_pane > button').empty();
            var status = $('<span class=\'ui-button-text\'>Import Data</span>');
            $('#import_pane > button').append(status);

        }).fail(function(jqXHR) {
            // TODO: Add error handling here
        });
    }
}

// Support functions, shouldn't be called outside of this HTML.

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setupLoginForm() {
    // Login form
    $('#login-form').dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
        "Login": function() {
            var data = {
                "username": $('#username').val(),
                "password": $('#password').val()
            };

            // Login button in form clicked 
            $.ajax({
                url: '/report-server/ui20/login/',
                type: 'POST',
                contentType: 'application/json',
                data: data,
                crossDomain: false,
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
                }).done(function(data) {
                    $('#login-error').hide();
                    $('#login-form').dialog('close');
                    // Gray out "Login" button
                    enableButton($('#logout-button'));
                    disableButton($('#login-button'));
                    // alter msg
                    $('#account-links > span > p').text( data );

                    logged_in = true;

                    loadContent();

                }).fail(function(jqXHR) {
                   $('#login-error').show();
                });
            },
            "Cancel": function() {
                $('#login-error').hide();
                $('#login-form').dialog('close');
            }
        }
    });
}

function fill_create_report_form(data) {
    // Clear outdated elements
    $('#contract').empty();
    $('#rhic').empty();
    $('#env').empty();
    //$('#byMonth').empty();

    // Add defaults
    $('#contract').append($('<option value=null></option>'));
    $('#contract').append($('<option selected value=All>All</option>'));


    // Add remainder elements from data
    jQuery.each(data.contracts, function(index, ele) {
            $('#contract').append($('<option value=' + ele + '>' + ele + '</option>'));
            });	

    $('#rhic').append($('<option selected value=null></option>'));
    jQuery.each(data.list_of_rhics, function(index, ele) {
            $('#rhic').append($('<option value=' + ele[0] + '>' + ele[1] + '</option>'));
            });	

    $('#env').append($('<option value=All>All</option>'));
    jQuery.each(data.environments, function(index, ele) {
            $('#env').append($('<option value=' + ele + '>' + ele + '</option>'));
            });	

    var d = new Date();
    var n = d.getMonth() + 1;
    var month=new Array();
    month[1]="January";
    month[2]="February";
    month[3]="March";
    month[4]="April";
    month[5]="May";
    month[6]="June";
    month[7]="July";
    month[8]="August";
    month[9]="September";
    month[10]="October";
    month[11]="November";
    month[12]="December";
    $('#byMonth').append($('<option selected value=' + n + '>' + month[n] + '</option>'));
}

function disableButton(btn) {
    btn.attr('disabled', true);
    btn.css('opacity', '0.35');
}

function enableButton(btn) {
    btn.removeAttr('disabled');
    btn.css('opacity', '');
}

function loadContent() {
    if (!logged_in) {
        $('#create_pane').hide();
        $('#report_pane').hide();
        $('#detail_pane').hide();
        $('#max_pane').hide();
        $('#import_pane').hide();

        $('#navWrap').hide();
    } else {
        $('#navWrap').show();
        openCreate();
        setupCreateForm();
    }
}

function removeActiveNav() {
    $('#navPrimary > ul > li').each(
            function(index) {
            $(this).removeClass('active');
            }
            );
}


function populateReport(rtn) {
    var pane = $('#report_pane > div');

    // cleanup first
    pane.empty();

    if (rtn.list.length > 0) {
        for (var rhic_index in rtn.list) {
            var rhic = rtn.list[rhic_index];

            var table = $('<table id=basic_report class=\'display\' style=\'display: table\' width=\'100%\'></table>');

            var header = $('<thead></thead>');
            var header_row = $('<tr></tr>');
            header_row.append($('<th>Product:</th>'));
            header_row.append($('<th>SLA:</th>'));
            header_row.append($('<th>Support:</th>'));
            header_row.append($('<th>Facts:</th>'));
            header_row.append($('<th>Contracted Use:</th>'));
            header_row.append($('<th>NAU:</th>'));
            


            header.append(header_row);

            table.append(header);

            var tbody = $('<tbody></tbody>');

            for (var product_index in rhic) {
                var product = rhic[product_index]; 

                // insert something if it's the first item
                if (product_index == 0) {
                    pane.append($('<b>RHIC: ' + product.rhic + ', Contract: ' + product.contract_id + '</b>'));
                }
                var description = 'Product: '+ product.product_name + ', SLA:' + product.sla + ', Support: ' + product.support + ' Facts: ' + product.facts;
                var row = $('<tr onclick="createDetail(\'' + product.start + '\',\'' + product.end + '\',\'' + description + '\', \'' + escape(new String(product.filter_args_dict))
                        +  '\') "></tr>');
                row.append($('<td>' + product.product_name + '</td>'));
                row.append($('<td>' + product.sla + '</td>'));
                row.append($('<td>' + product.support + '</td>'));
                row.append($('<td>' + product.facts + '</td>'));
                row.append($('<td>' + product.contract_use + '</td>'));
                row.append($('<td>' + product.checkins + '</td>'));
                
                tbody.append(row);

            }

            table.append(tbody);

            pane.append(table);

            pane.append($('<br></br>'));


        }
    }


}






function populateMaxReport(rtn) {
    var pane = $('#max_pane');
    
    // cleanup first
    pane.empty();
    var header = $('<b> ' +  rtn.description + '</b>' );
    $('#max_pane').append(header);

    if (rtn.list.length > 0) {
       

        pane.append($('<br></br>'));
        pane.append($('<div id="chartdiv" style="height:400px;width:100%; "></div>'));
        var mdu = rtn.mdu;
        var mcu = rtn.mcu;
        var contract = rtn.daily_contract
        var plot1 = $.jqplot('chartdiv', [mdu, mcu, contract],
            {
                title:'MDU vs MCU',
                axesDefaults: {
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                axes: {
                    xaxis:{
                        label: "Date Range",
                        pad: 0
                    },
                    yaxis:{
                        label: "Number of Resources",
                        pad: 1.2
                    }
                },
                legend: {
                	show: true,
                	location: 'e'
                },
                series:[
                    {
                    	label: 'MDU',
                        lineWidth:2,
                        markerOptions: { style:'dimaond' } 
                    },
                    {
                    	label: 'MCU',
                        markerOptions: { sytle:'circle'}
                    },
                    {
                    	label: 'Contracted Use',
                    	lineWidth:5,
                    	color: '#FF0000',
                        markerOptions: { style:"filledSquare", size:10 }
                    }
                ]
                
            });
        pane.append('<h3>Glossary:</h3>');
        pane.append('<b>Maximum Daily Usage (MDU)</b><br>');
        pane.append('<b>Maximum Concurrent Usage (MCU)</b><br>');
        pane.append('<b>Contracted Use: This is the number of concurrent entitlements purchased in the contract</b>');
        
        pane.append('<br><br>')
        pane.append('<h3>Details:</h3>');
        var mydata = rtn.list;

        var table = $('<table id=\'max_data\' class=\'display\' style=\'display: table\' width=\'100%\'></table>');

        var header = ($('<tr></tr>'));
        header.append($('<th>Day:</th>'));
        header.append($('<th>Maximum Daily Usage:</th>'));
        header.append($('<th>Maximum Concurrent Usage:</th>'));


        table.append(header);

        var tbody = $('<tbody></tbody>');

        for (var instance_index=0; instance_index <  rtn.list.length; instance_index++) {
            var instance = rtn.list[instance_index];

            var row = $('<tr></tr>');
            row.append($('<td>' + instance['date'] + '</td>'));
            row.append($('<td>' + instance['mdu'] + '</td>'));
            row.append($('<td>' + instance['mcu'] + '</td>'));

            tbody.append(row);
        }

        table.append(tbody);

        pane.append(table);
    } else {
        pane.append($('<h3>This date range contains no usage data.</h3>'));
        pane.append($('<br></br>'));
        pane.append($('<br></br>'));
    }
}

function populateDetailReport(rtn) {
    //var pane = $('#details > table');

    // cleanup
    $('#details').empty();
    $('#instance_details').empty();
    var header = $('<b> ' +  rtn.description + '</b>' );
    var detail_table = $('<table style="width: 100%; margin-bottom: 0;"></table>');
    $('#details').append(header);
    $('#details').append(detail_table);

    var reportDetailTableData = [];

    detail_table = detail_table.dataTable({
            "bAutoWidth": true,
            "bJQueryUI": true,
            "aoColumns": [
            {"sTitle": "Count"},
            {"sTitle": "UUID"},
            {"sTitle": "Number of Checkins"}
            ],


    });

    for (var instance_index=0; instance_index < rtn.list.length; instance_index++) {
        var instance = rtn.list[instance_index];

        var i = instance_index + 1;

        detail_table.fnAddData([i, instance.instance, instance.count]);
    }

    // attach event
    detail_table.children('tbody').find('tr').each(function() {
            $(this).click(function() {
                $(this).siblings().each(function() {
                    $(this).removeClass('highlighted');
                    });
                $(this).addClass('highlighted');
                var instance = $($(this).children('td')[1]).text();
                createInstanceDetail(rtn.start, rtn.end, instance, escape(new String(rtn.this_filter)));
                });
            });


}

function populateInstanceDetailReport(rtn) {
    // cleanup
    $('#instance_details').empty();
    var header = $('<b>Number of Checkins</b>');
    var table = $('<table style="width: 100%; margin-bottom: 0;"></table>');
    $('#instance_details').append(header);
    $('#instance_details').append(table);

    var pane = $('#instance_details > table');

    var instanceDetailTableData = [];

    instance_table = pane.dataTable({
            "bAutoWidth": false,
            "bJQueryUI": true,
            "aoColumns": [
            {"sTitle": "Count"},
            {"sTitle": "UUID"},
            {"sTitle": "Product"},
            {"sTitle": "Time"},
            {"sTitle": "Products"},
            {"sTitle": "Memory"},
            {"sTitle": "CPU Sockets"},
            {"sTitle": "Reporting Domain"},
            ],

            
    });

    for (var instance_index=0; instance_index <  rtn.list.length; instance_index++) {
        var instance = rtn.list[instance_index];

        var i = instance_index + 1;

        //instanceDetailTableData.push([i, instance.instance_identifier, instance.product_name, instance.hour, instance.product, instance.memtotal, instance.cpu_sockets, instance.environment]);
        instance_table.fnAddData([i, instance.instance_identifier, instance.product_name, instance.hour, instance.product, instance.memtotal, instance.cpu_sockets, instance.environment]);

    }

    // if currently hidden, turn it on
    if (!$('#instance_details').is(':visible')) {
        $('#instance_details').show();
    }
}

function validateForm() {
    var rtn = true;

    $('#form_error').empty();

    if ($('#byMonth').val() > 0 || ($('#startDate').val() && $('#endDate').val())) {
        // pass
    } else {
        $('#form_error').append($('<b>Please enter a valid date range or select a month.</b>'));
        $('#form_error').append($('<br></br>'));
        rtn = false;
    }

    if ($('#contract').attr('disabled') && $('#rhic').attr('disabled')) {
        $('#form_error').append($('<b>Please select a Contract or RHIC.</b>'));
        $('#form_error').append($('<br></br>'));
        rtn = false;
    } else {
        // pass
    }
    return rtn;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
