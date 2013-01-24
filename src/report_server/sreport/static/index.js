var first_logged_in = false;
var logged_in = false;
var is_admin = true;
var csrftoken = '';
var page_size = 10; // default value

$(document).ready(function() {
    csrftoken = getCookie('csrftoken');
    
    $("#spinner").bind("ajaxSend", function() {
		$(this).show();
		
	}).bind("ajaxStop", function() {
		$(this).hide();
	}).bind("ajaxError", function() {
		$(this).hide();
	});
    
    setupLoginForm();
    setupLLButtons();
    //setupNavButtons(); // obsolete?
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
        //$('#contract').val('null').trigger('liszt:updated');
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

    if (!first_logged_in || !is_admin) {
        $('#import_button').addClass('disabled');
        $('#import_button').off("click");
    }

    $("#contract").button().change(function () {
        updateListOfRHICS();
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

        // Disable appropriate nav tabs 
        $('#report_button').addClass('disabled');
        $('#detail_button').addClass('disabled');
        $('#max_button').addClass('disabled');
        $('#import_button').addClass('disabled');

        $('#report_button').off('click');
        $('#detail_button').off('click');
        $('#max_button').off("click");
        $('#import_button').off("click");

        $('#contract').change(function() {
            $('#rhic').val('').trigger('liszt:updated');
        });

        $('#rhic').change(function() {
            $('#contract').val('').trigger('liszt:updated');
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

function form_filter_link_show(){
	document.getElementById("filter_toggle").style.display = "block";
	document.getElementById("default-report-submit").style.display = "block";
	toggle_report_form()
}

function form_filter_link_hide(){
	document.getElementById("filter_toggle").style.display = "none";
	//document.getElementById("default-report-submit").style.display = "none";
	toggle_report_form()
}

function toggle_report_form() {
    $('#default_report_results').empty();
    $('#default_report_results_ui').empty();
    
    //var but = document.getElementById("default-report-submit")
    var ele = document.getElementById("create_pane");
    var report = document.getElementById("report_form");
    var text = document.getElementById("filter_toggle");
    var default_report_button = document.getElementById("default-report-submit");
    
    //DEFAULT, just show create_report
    if(ele.style.display == "block") {
        ele.style.display = "none";
        report.style.display = "none";
        text.innerHTML = "show advanced filter";
        default_report_button.style.display = "block";
    }
    //show report filter options
    else {
        ele.style.display = "block";
        report.style.display = "block";
        text.innerHTML = "hide advanced filter";
        default_report_button.style.display = "none";
    }
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

function updateListOfRHICS() {

    // Have to stop url from changing so disable default event
    event.preventDefault();
    $('#rhic').attr('disabled', false);

    // validating the form is no longer required
    //if (logged_in && validateForm()) {
    if (logged_in) {
        // Build up var
        var data = {};
        data['contract_number'] = $('#contract').val();

    $.ajax({
        url: '/report-server/ui20/report_form_rhics/',
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
            change_rhic_form(JSON.parse(data));
            $('#rhic').chosen();
            $('#rhic').trigger("liszt:updated");

        }).fail(function(jqXHR) {
            // TODO: Add error handling here
        });
    }
}


function setupCreateFormButtons() {
    var btn = $('#clear');
    var o = $('#original');
    var c = $('#choices');
    // Initially hide the choices
    c.hide();
}

function createReport(event) {
	form_filter_link_show();

	
    // Have to stop url from changing so disable default event
    event.preventDefault();
    
    // validating the form is no longer required
    //if (logged_in && validateForm()) {
    if (logged_in) {
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
            $('#report_pane > div').empty();
            var pane = '#report_pane > div';
            populateReport(rtn, pane );
            openReport();
            // Attach the event handler back on
            $('#report_button').on("click", openReport);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // TODO: Add error handling here
        });
    }
}

function create_default_report(event){
    document.getElementById("report_form").style.display = "none"
    $('#default_report_results_ui').empty();
    $('#default_report_results').empty();
    
    event.preventDefault();
    var num
    if (logged_in) {
        var data = {};
        var dtoday = Date.today();
        console.log(dtoday);
        //data in mm/dd/yyyy format
        data['startDate'] = (3).months().ago().toString("M/d/yyyy");
        data['endDate'] = Date.today().toString("M/d/yyyy");
        data['contract_number'] = "All"
        data['rhic'] = "null"
        data['env'] = "All"
        
        $.ajax({
            url: '/report-server/ui20/default_report/',
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
            $('#default_report_results').append("<br><br><br><br><br><br><br><br><br>")
            num = populateReport(rtn, "#default_report_results");
            fact = populateFactComplianceReport(rtn.biz_list, "#default_report_results");  
            
            if (num+fact > 0){
                console.log('fail')
                result_ui = $('#default_report_results_ui');
                var table = $('<table width=\"60%\" align=\"right\"></table>');
                table.append('<img border=0 src="/static/fail.png") alt="fail" width="100" height="100">');
                result_ui.append(table);
            }
            else{
                console.log('pass')
                result_ui = $('#default_report_results_ui');
                var table = $('<table width=\"60%\" align=\"right\"></table>');
                table.append('<img border=0 src="/static/pass.jpg") alt="fail" width="100" height="100">');
                result_ui.append(table);
            }
            
            
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
        //var url = '/report-server/ui20/export/';
       //send request
        jQuery('<form action="/report-server/ui20/export/" method="'+ ('get') +'">'+inputs+'</form>')
        .appendTo('body').submit().remove();
        //alert('Please wait while the export is generated')

};




function turnOnAdminFeatures() {
    $('#import_button').removeClass('disabled');
    $('#import_button').on("click", openImport);
}


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
    form_filter_link_show();

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
    form_filter_link_hide();
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
    form_filter_link_hide();
    removeActiveNav();
    $('#detail_button').addClass('active');
    $('#create_pane').hide();
    $('#report_pane').hide();
    $('#detail_pane').hide();
    $('#import_pane').hide();
    $('#max_pane').hide();
    $('#detail_pane').show();

}

function closeDetail() {
    $('#detail_button').addClass('disabled');
    removeActiveNav();
    $('#detail_button').off("click");
    $('#detail_pane').hide();

}

function openMax() {
	form_filter_link_hide();
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

function closeMax() {
    $('#max_button').addClass('disabled');
    removeActiveNav();
    $('#max_button').off("click");
    $('#max_pane').hide();

}

function openImport() {
	form_filter_link_hide();
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



function createDetail(date, description,  filter_args) {
    var data = {
        "date": date,
        "description":  description,
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
        closeDetail();
        populateDetailReport(rtn);
        openDetail();

        $('#detail_button').removeClass('disabled');
        $('#detail_button').on("click", openDetail);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}



function createMax(start, end, description, filter_args) {
    closeDetail();
    closeMax();
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
        populateMaxReport(rtn, filter_args);
        
        $('#max_button').on("click", openMax);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}

function createInstanceDetail(date, instance, filter_args) {
    var data = {
        "date": date,
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

function createQuarantineReport() {
    var data = {};
    $('#admin_report').empty();
    $.ajax({
        url: '/report-server/ui20/quarantine/',
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
        populateQuarantineReport(rtn);
        openImport(); // this shouldn't be needed, but no harm in calling it again
        $('#import_button').on("click", openImport);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}


function createFactComplianceReport() {
    var data = {};
    $('#admin_report').empty();

    $.ajax({
        url: '/report-server/ui20/fact_compliance/',
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
        populateFactComplianceReport(rtn.list, '#admin_report');
        openImport(); // this shouldn't be needed, but no harm in calling it again
        $('#import_button').on("click", openImport);
    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}

function importData() {
    if (logged_in) {
        $('#import_pane > div').empty();
        $('#importData').empty();
        var status = $('<span class=\'ui-button-text\'>Working on import...</span>');
        $('#importData').append(status);

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
            var status = $('<br><span>Import Skipped, import has been executed in the last 45 minutes<span>');
            $('#admin_report').append(status);
            }
            else {
            $('#import_pane > div').empty();
            var status = $('<span>Import Complete!\nStart Time: ' + dt.start + '\nEnd Time: ' + dt.end + '<span>');
            $('#admin_report').append(status);
            }
            $('#importData').empty();
            var button = $('<span class=\'ui-button-text\'>Import Data</span>');
            $('#importData').append(button);
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


function getSession() {
	//var name = 'sessionid';
	var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
       
    }
    alert(cookies)
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
                    var rtn = jQuery.parseJSON(data); // should be more defensive/less hardcode-ness

                    $('#login-error').hide();
                    $('#login-form').dialog('close');

                    // Gray out "Login" button
                    enableButton($('#logout-button'));
                    disableButton($('#login-button'));

                    // Check for admin permission
                    if (rtn.is_admin === true) {
                        $('#import_button').removeClass('disabled');
                        $('#import_button').on("click", openImport);
                    }

                    // alter msg
                    $('#account-links > span > p').text(rtn.username + " account #" + rtn.account);

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

function change_rhic_form(data){
    $('#rhic').empty();
    $('#rhic').append($('<option selected value=null></option>'));
    $('#rhic').append($('<option selected value=All>All</option>'));
    jQuery.each(data.list_of_rhics, function(index, ele) {
        $('#rhic').append($('<option value=' + ele[0] + '>' + ele[1] + '</option>'));
    });
}

function fill_create_report_form(data) {
    // Clear outdated elements
	$('#byMonth').empty();
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

   
    date_0 = Date.today();
    date_1 = (1).months().ago();
    date_2 = (2).months().ago();
    
    $('#byMonth').append($('<option  value=' + '-1' + ' ></option>'));
    $('#byMonth').append($('<option selected value=' + date_0.toString("M") + ',' + date_0.toString("yyyy") +  '>' + date_0.toString("MMM") + ' ' + date_0.toString("yyyy") + '</option>'));
    $('#byMonth').append($('<option selected value=' + date_1.toString("M") + ',' + date_1.toString("yyyy") +  '>' + date_1.toString("MMM") + ' ' + date_1.toString("yyyy") + '</option>'));
    $('#byMonth').append($('<option selected value=' + date_2.toString("M") + ',' + date_2.toString("yyyy") +  '>' + date_2.toString("MMM") + ' ' + date_2.toString("yyyy") + '</option>'));
    
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
    	$('#main-wrap').hide();
        $('#create_pane').hide();
        $('#report_pane').hide();
        $('#detail_pane').hide();
        $('#max_pane').hide();
        $('#import_pane').hide();

        $('#navWrap').hide();
    } else {
    	$('#main-wrap').show();
        $('#navWrap').show();
        openCreate();
        setupCreateForm();
        $('#create_button').on("click", openCreate);
        if (is_admin) {
            $('#import_button').on("click", openImport);
        }
    }
}

function removeActiveNav() {
    $('#navPrimary > ul > li').each(
            function(index) {
            $(this).removeClass('active');
            }
            );
}


function populateReport(rtn, pane) {
    var pane = $(pane);
    var this_div = $('<div this_rhic_table>')

    pane.append('<h3>Date Range: ' + rtn.start.substr(0, 10) + ' ----> ' + rtn.end.substr(0, 10) + '</h3>');
    pane.append('<br><br>');
    
    var show_details = $('<button id=show_details style="float: right" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
    

    if (rtn.list.length > 0) {
        pane.append(show_details); 
    	pane.append('<b>Number of RHIC\'s:  ' + rtn.list.length + '</b> ')
    	pane.append('<br><br>')
    	
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
            header_row.append($('<th>Compliant:</th>'));
            


            header.append(header_row);

            table.append(header);

            var tbody = $('<tbody></tbody>');

            for (var product_index in rhic) {
                var product = rhic[product_index]; 

                // insert something if it's the first item
                if (product_index == 0) {
                    this_div.append($('<b>RHIC: ' + product.rhic + ', Contract: ' + product.contract_id + '</b>'));
                }
                

                var description = 'Product: '+ product.product_name + ', SLA:' + product.sla + ', Support: ' + product.support + ' Facts: ' + product.facts ;
                //json attempt
                //var description = {"Product": product.product_name, "SLA": product.sla , "Support": product.support, "Facts": product.facts };
                //var description = '';
                var row = $('<tr onclick="createMax(\'' + product.start + '\',\'' + product.end + '\',\'' + description + '\', \'' + escape(new String(product.filter_args_dict))
                        +  '\') "></tr>');
                row.append($('<td>' + product.product_name + '</td>'));
                row.append($('<td>' + product.sla + '</td>'));
                row.append($('<td>' + product.support + '</td>'));
                row.append($('<td>' + product.facts + '</td>'));
                row.append($('<td>' + product.contract_use + '</td>'));
                row.append($('<td>' + product.nau + '</td>'));
                
                if(product.compliant){
                	//row.append($('<td bgcolor="#00FF00">' + product.compliant + '</td>'));
                	row.append($('<td bgcolor="#00FF00">Yes</td>'));
                }
                else {
                	//row.append($('<td bgcolor="#FF0000">' + product.compliant + '</td>'));
                	row.append($('<td bgcolor="#FF0000">No</td>'));
                }
                
                
                tbody.append(row);

            }

            table.append(tbody);
			this_div.append(table);
			this_div.append($('<br></br>'))
            pane.append(this_div)
			this_div.hide()
			
        }
    }
    
show_details.click(function (){
		this_div.toggle("slow");
		
	  })
return rtn.list.length
}

function populateQuarantineReport(rtn) {
    var top = $('#admin_report');
    top.empty();
    top.append('<br><br>');
    var header = $('<b>Number of Quarantined Instance Checkins: ' + rtn.list.length + '   </b>');
    if (rtn.list.length > 0) {
    top.append(header);
    var show_details = $('<button id=show_quarantine class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
    top.append(show_details);   
     

	var table = $('<table id=\'quarantine_data\' class=\'display\' style=\'display: table\' width=\'100%\'></table>');
	
	
	var header = ($('<tr></tr>'));
	header.append($('<th>Instance:</th>'));
	header.append($('<th>Splice Server:</th>'));
	header.append($('<th>Product Name:</th>'));
	header.append($("<th>Product ID's:</th>"));
	header.append($('<th>Time:</th>'));


	table.append(header);

	var tbody = $('<tbody></tbody>');

	for (var instance_index=0; instance_index <  rtn.list.length; instance_index++) {
		var instance = rtn.list[instance_index];

		var row = $('<tr></tr>');
		row.append($('<td>' + instance['instance_identifier'] + '</td>'));
		row.append($('<td>' + instance['splice_server'] + '</td>'));
		row.append($('<td>' + instance['product_name'] + '</td>'));
		row.append($('<td>' + instance['product'] + '</td>'));
		row.append($('<td>' + instance['hour'] + '</td>'));

		tbody.append(row);
	}
   
	table.append(tbody);
	table.hide();
	top.append(table);
	
	
	show_details.click(function (){
		$('#quarantine_data').toggle("slow");
		
	  })
	  
} else {
	top.append($('<h3>There is no quarantined data.</h3>'));
	top.append($('<br></br>'));
	top.append($('<br></br>'));
}

}

function populateFactComplianceReport(rtn, pane) {
    var top = $(pane);
    var this_div = $('<div this_fact_table>')
    var show_details = $('<button id=show_details style="float: right" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
    //top.empty();
    top.append('<br><br>');
    var header = $('<b>Number of Instances: ' + rtn.length + '   </b>');
    if (rtn.length > 0) {
      top.append(header);
  	  
  	  
      top.append(show_details); 
      top.append('<br><br>')
  	 
      var mydata = rtn;   
        var table = $('<table id=\'factCompliance_data\' class=\'display\' style=\'display: table\' width=\'100%\'></table>');
        
        
        var header = ($('<tr></tr>'));
        header.append($('<th>Instance:</th>'));
        header.append($('<th>Product Name:</th>'));
        header.append($('<th>Fact: CPU:</th>'));
        header.append($('<th>Fact: CPU Sockets:</th>'));
        header.append($('<th>Fact: Memory:</th>'));
        header.append($('<th>Rules: CPU</th>'));
        header.append($('<th>Rules: CPU Socket</th>'));
        header.append($('<th>Rules: Memory (kb)</th>'));
        header.append($('<th>Violation Summary</th>'));


        table.append(header);
        

        var tbody = $('<tbody></tbody>');

        for (var instance_index=0; instance_index <  rtn.length; instance_index++) {
            var instance = rtn[instance_index][0];
            var rules = rtn[instance_index][1];
            var summary = rtn[instance_index][2];

            var row = $('<tr></tr>');
            row.append($('<td>' + instance['instance_identifier'] + '</td>'));
            row.append($('<td>' + instance['product_name'] + '</td>'));
            row.append($('<td>' + instance['cpu'] + '</td>'));
            row.append($('<td>' + instance['cpu_sockets'] + '</td>'));
            row.append($('<td>' + instance['memtotal'] + '</td>'));
            
            
            if (rules['cpu']['rule']==undefined){
                row.append($('<td></td>'))
            }
            else{
                row.append($('<td>' + rules['cpu']['rule'] + '</td>'));
            }
            
            if (rules['cpu_sockets']['rule']==undefined){
                row.append($('<td></td>'))
            }
            else{
               row.append($('<td>' + rules['cpu_sockets']['rule'] + '</td>')); 
            }
            
            if (rules['memtotal']['rule']==undefined){
                row.append($('<td></td>'))
            }
            else{
                row.append($('<td>' + rules['memtotal']['rule'] + '</td>'));
            }
            
            row.append($('<td>' + summary +  '</td>'));


            tbody.append(row);
        }
       
        table.append(tbody);
        //table.hide();
        this_div.append(table)
        //top.append(table);
        top.append(this_div)
        this_div.hide()
        
        
        //show_compliance.click(function (){
        //    $('#factCompliance_data').toggle("slow");
        //  })
          
    } 
show_details.click(function (){
		this_div.toggle("slow");
		
	  })
return rtn.length
}




function populateMaxReport(rtn) {
    var pane = $('#max_pane');
    
    // cleanup first
    pane.empty();
    
    var desc_start = new Date(0);
    var desc_end = new Date(0);
    desc_start.setUTCSeconds(rtn.start);
    desc_end.setUTCSeconds(rtn.end);
    

    
    pane.append('<h3>Date Range: ' + desc_start.toDateString().substr(0,10) + ' ----> ' + desc_end.toDateString().substr(0,10) + '</h3>');
    pane.append('<br><br>');
    var header = $('<b> ' +  rtn.description + '</b>' );
    $('#max_pane').append(header);

    if (rtn.list.length > 0) {
       

        pane.append($('<br></br>'));
        pane.append($('<div id="chartdiv" style="height:400px;width:100%; "></div>'));
        var date = []; 
        //for (var i=0; i<rtn.date.length; i++){
        //	var this_date = new Date(rtn.date[i]);
        //	date.push(this_date.toISOString());
        //}
        
        var date = rtn.date;
        var mdu = rtn.mdu;
        var mcu = rtn.mcu;
        var contract = rtn.daily_contract;
        var filter_args = rtn.filter_args;
        
        var date_length = date.length;
        
        
        //var plot1 = $.jqplot('chartdiv', [mdu, mcu, contract],
        var plot1 = $.jqplot('chartdiv', [mdu, mcu, contract],
                {
                    title:'MDU vs MCU',
                    axesDefaults: {
                        labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                    },
                    
                    axes: {
                        xaxis:{
                            label: "Date Range",
                            renderer:$.jqplot.DateAxisRenderer, 
                            tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                            tickOptions: {
                              angle: -30,
                              formatString: '%b %e %Y'
                            } 
                        },
                        yaxis:{
                            label: "Number of Resources",
                            pad: 1.3
                        }
                    },
                    highlighter: {
                        show: true,
                        sizeAdjust: 10.5,
                        useAxesFormatters: true
                    },
                    cursor: {
                    	show: true
                    },
                    legend: {
                    	show: true,
                    	location: 'se',
                    	yoffset: 500
                    	
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
        $('#chartdiv').bind('jqplotDataClick', function (ev, seriesIndex, pointIndex, data) { 
        	   //alert("test" + "," + data[0] + "," + data[1]);
        	   var this_date = new Date(data[0]);
        	   var date_to_send = (this_date.getMonth() + 1) + "-" + this_date.getDate() + "-" + this_date.getFullYear();
        	   createDetail( date_to_send, rtn.description,  escape(new String(filter_args)));
        	  });
    
        pane.append('<h3>Glossary:</h3>');
        pane.append('<b>Maximum Daily Usage (MDU)</b><br>');
        pane.append('<b>Maximum Concurrent Usage (MCU)</b><br>');
        pane.append('<b>Contracted Use: This is the number of concurrent entitlements purchased in the contract</b>');
        
        pane.append('<br><br>');
        //pane.append('<h3>Details:</h3>');
        
        //pane.append('<button id=show_details class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
        var show_details = $('<button id=show_details class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
        pane.append(show_details);
        //pane.append('<button id=hide_details class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Hide Details</button>');
        //var hide_details = $('<button id=hide_details class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Hide Details</button>');
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
            var row = $('<tr onclick="createDetail(\'' + instance['date'] + '\',\'' + rtn.description + '\', \'' + escape(new String(filter_args)) +  '\') "></tr>');
            row.append($('<td>' + instance['date'] + '</td>'));
            row.append($('<td>' + instance['mdu'] + '</td>'));
            row.append($('<td>' + instance['mcu'] + '</td>'));

            tbody.append(row);
        }
       
        table.append(tbody);
        table.hide();
        pane.append(table);
        
        
        $("button").click(function (){
            $('#max_data').toggle("slow");
            
          })
          
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
    var desc_date = new Date(0);
    desc_date.setUTCSeconds(rtn.date);
    
    var pane = $('#details');
    
    pane.append('<h3>Date Range: ' + desc_date.toDateString().substr(0,10) + '</h3>');
    pane.append('<br><br>');
    
    
    var header = $('<b> ' +  rtn.description + '</b>' );
    var detail_table = $('<table style="width: 100%; margin-bottom: 0;"></table>');
    pane.append(header);
    pane.append(detail_table);

    var reportDetailTableData = [];

    detail_table = detail_table.dataTable({
            "bAutoWidth": true,
            "bJQueryUI": true,
            "aoColumns": [
            {"sTitle": "MAC-UUID"},
            {"sTitle": "Number of Checkins"}
            ],


    });

    for (var instance_index=0; instance_index < rtn.list.length; instance_index++) {
        var instance = rtn.list[instance_index];

        var i = instance_index + 1;

        detail_table.fnAddData([ instance.instance, instance.count]);
    }

    // attach event
    detail_table.children('tbody').find('tr').each(function() {
            $(this).click(function() {
                $(this).siblings().each(function() {
                    $(this).removeClass('highlighted');
                    });
                $(this).addClass('highlighted');
                var instance = $($(this).children('td')[0]).text();
                createInstanceDetail(rtn.date, instance, escape(new String(rtn.this_filter)));
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
            {"sTitle": "MAC-UUID"},
            {"sTitle": "Product"},
            {"sTitle": "Time"},
            {"sTitle": "Product ID's"},
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

/*
 * Form Validation is no longer required
 * 
function validateForm() {
    var rtn = true;

    $('#form_error').empty();

    if ($('#byMonth').val() || ($('#startDate').val() && $('#endDate').val())) {
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
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
