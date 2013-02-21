var first_logged_in = false;
var logged_in = false;
var is_admin = true;
var csrftoken = null;
var pxt = null;
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

   

});


function login() {
    $('#login-form').dialog('open');
}

function logout() {
    $.ajax({
        url: '/report-server/meter/logout/',
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

        
        //loadContent();
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
  
}

function updateListOfRHICS() {

}

function setupCreateFormButtons() {
  
}

function createReport(event) {
	
}

function create_default_report(event){
   
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
     
     $.download('/report-server/meter/export', data, 'get');

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
        //var url = '/report-server/meter/export/';
       //send request
        jQuery('<form action="/report-server/meter/export/" method="'+ ('get') +'">'+inputs+'</form>')
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
    //form_filter_link_show();

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
   
}

function createMax(start, end, description, filter_args) {
    
}

function createInstanceDetail(date, instance, filter_args) {
    
}

function createQuarantineReport() {
   
}

function createFactComplianceReport() {
  
}

function importData() {

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
                url: '/report-server/meter/login/',
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
                	console.log("This request failed");
                	console.log(jqXHR);
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
    
}

function fill_create_report_form(data) {

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
   
}

function removeActiveNav() {
    $('#navPrimary > ul > li').each(
            function(index) {
            $(this).removeClass('active');
            }
            );
}


function populateReport(rtn, pane) {

}

function populateQuarantineReport(rtn) {
    
}

function populateFactComplianceReport(rtn, pane) {
  
}

function populateMaxReport(rtn) {
   
}

function populateDetailReport(rtn) {
   
}

function populateInstanceDetailReport(rtn) {
 
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}