/* 
Copyright  2012 Red Hat, Inc.
This software is licensed to you under the GNU General Public
License as published by the Free Software Foundation; either version
2 of the License (GPLv2) or (at your option) any later version.
There is NO WARRANTY for this software, express or implied,
including the implied warranties of MERCHANTABILITY,
NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
have received a copy of GPLv2 along with this software; if not, see
http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
*/

// ********************   LOGIN RELATED *****************************
function hide_pages() {
	document.getElementById("navWrap").style.display = "none";
    document.getElementById("main-wrap").style.display = "none";
}

function show_pages() {
	document.getElementById("navWrap").style.display = "block";
    document.getElementById("main-wrap").style.display = "block";
    openCreate();
}

function login() {
    $('#login-form').dialog('open');
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
                    if (rtn.is_admin == true) {
                        turnOnAdminFeatures(true);
                    }
                    else{
                    	turnOnAdminFeatures(false);
                    }
                    	

                    // alter msg
                    $('#account-links > span > p').text(rtn.username + " account #" + rtn.account);

                    logged_in = true;
                    show_pages();
                    
                    //TESTING
                    //setupCreateFormOLD();
                    setupCreateForm();
                    setupCreateDatesForm();


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
        hide_pages();

        // Disable appropriate nav tabs 
        $('#report_button').addClass('disabled');
        $('#detail_button').addClass('disabled');
        $('#max_button').addClass('disabled');
        $('#import_button').addClass('disabled');

        $('#report_button').off('click');
        $('#detail_button').off('click');
        $('#max_button').off("click");
        $('#import_button').off("click");

    }).fail(function(jqXHR) {
        // TODO: Add error handling here
    });
}

function setupLoginButtons() {
    if (first_logged_in) {
        disableButton($('#login-button'));
        logged_in = true;
        show_pages();
    } else {
        disableButton($('#logout-button'));
        logged_in = false;
        hide_pages();
    }

    $('#login-error').hide();
}

function navButtonDocReady(){
	$('#login-button').click(login);
    $('#logout-button').click(logout);
	$('#instance_details').hide();
    $('#report_button').addClass('disabled');
    $('#detail_button').addClass('disabled');
    $('#max_button').addClass('disabled');
    $('#import_button').addClass('disabled');

    $('#report_button').off('click');
    $('#detail_button').off('click');
    $('#max_button').off("click");
    $('#imort_button').off("click");
    
}

// ********************   LOGIN RELATED END *****************************


// ********************   SHOW, HIDE REPORT FORM**************************
function form_filter_link_hide(hide){
    
    //var report_controls = $('#default_report_controls');
    if (hide){
        //document.getElementById("filter_toggle").style.display = "none";
    	document.getElementById("filter_toggle").style.display = "none";
    	document.getElementById("default_report_controls").style.display = "none";
    	
    }
    if (!hide){
        
        document.getElementById("default_report_controls").style.display = "block";
        document.getElementById("filter_toggle").style.display = "block";
        //document.getElementById("default-report-submit").style.display = "block";

    }
}


function toggle_report_form() {
    var text = document.getElementById("filter_toggle");
    console.log(text.innerHTML);
    $('#default_report_controls').empty();

    if (text.innerHTML == "Show Filter Options"){
        filterInitialPopulateOptions();
        text.innerHTML = "Hide Filter Options";
    }
    else{
        text.innerHTML = "Show Filter Options";
        filterInitialPopulate();
    }
}



// ********************   SHOW, HIDE REPORT FORM, END**************************

function removeActiveNav() {
    $('#navPrimary > ul > li').each(
            function(index) {
            $(this).removeClass('active');
            }
    );
}

function disableButton(btn) {
    btn.attr('disabled', true);
    btn.css('opacity', '0.35');
}

function enableButton(btn) {
    btn.removeAttr('disabled');
    btn.css('opacity', '');
}


function openCreateLogin() {
    removeActiveNav();
    form_filter_link_hide(false);
    $('#create_button').addClass('active');

    if (logged_in) {
        $('#create_pane').show();
        $('#report_pane').hide();
        $('#detail_pane').hide();
        $('#max_pane').hide();
        $('#import_pane').hide();
        
    }
}


function openCreate() {
    removeActiveNav();
    $('#create_button').addClass('active');
    $('#create_button').on("click", openCreate);
    form_filter_link_hide(false);
    $('#create_pane').show();
    $('#report_pane').hide();
    $('#detail_pane').hide();
    $('#max_pane').hide();
    $('#import_pane').hide();

}



function closeCreate() {
    $('#create_button').addClass('disabled');
    removeActiveNav();
    $('#create_button').off("click");
    $('#create_button').hide();
}

function openReport() {
    $('#report_button').removeClass('disabled');
    $('#report_button').on("click", openReport);
    form_filter_link_hide(true);
    removeActiveNav();
    $('#report_button').addClass('active');
    $('#create_pane').hide();
    $('#report_pane').hide();
    $('#detail_pane').hide();
    $('#import_pane').hide();
    $('#max_pane').hide();
    $('#report_pane').show();
}


function closeReport() {
    $('#report_button').addClass('disabled');
    removeActiveNav();
    $('#report_button').off("click");
    $('#report_button').hide();
}

function openDetail() {
    $('#detail_button').removeClass('disabled');
    $('#detail_button').on("click", openDetail);
    form_filter_link_hide(true);
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
    form_filter_link_hide(true);
    $('#max_button').on("click", openMax);
    $('#max_button').removeClass('disabled');
    removeActiveNav();
    $('#max_button').addClass('active');

    $('#create_pane').hide();
    $('#report_pane').hide();
    $('#detail_pane').hide();
    $('#max_pane').hide();
    $('#import_pane').hide();
    $('#max_pane').show();

}


function closeMax() {
    $('#max_button').addClass('disabled');
    removeActiveNav();
    $('#max_button').off("click");
    $('#max_pane').hide();
}

function openImport() {
	form_filter_link_hide(true);
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

function turnOnAdminFeatures(state) {
	if (state){
	    $('#import_button').removeClass('disabled');
	    $('#import_button').on("click", openImport);
	  }
	else{
		$('#import_button').addClass('disabled');
	  }
	
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

function setupReportForm(){
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
}

function setup_description(pane, date, desc){
    pane.append('<h3>Date Range: ' + date + '</h3>');
    if (desc){
        pane.append('<b>' + desc.Product + ", " + desc.SLA + ", " + desc.Support + ", " + desc.Facts + '</b>');
    }
}

function glossary_mdu(pane){
    pane.append('<h3>Glossary:</h3>');
    pane.append('<b>Maximum Daily Usage (MDU)</b><br>');
    pane.append('<b>Maximum Concurrent Usage (MCU)</b><br>');
    pane.append('<b>Contracted Use: This is the number of concurrent entitlements purchased in the contract</b>');
    pane.append('<br><br>'); 
}

function glossary_report(pane){
    pane.append('<br><br><br><br><br><br>');
    pane.append('<table width="100%"><tbody>');
    pane.append('<tr><td><h3>Glossary:</h3></td></tr>');
    pane.append('<tr><td width="20%"><b>SLA :</td><td><b>Service level agreement as defined in the customers contract</td></tr><');
    pane.append('<tr><td width="20%"><b>Support :</td><td><b>Support parameters as defined in the customers contract</td></tr>');
    pane.append('<tr><td width="20%"><b>Facts :</td><td><b>Characteristics of both hardware and software of the resource</td></tr>');
    pane.append('<tr><td width="20%"><b>Contracted Use:</td><td><b>This is the number of concurrent entitlements purchased in the contract</td></tr>');
    pane.append('<tr><td width="20%"><b>NAU :</td><td><b>Net Aggregate Usage, is the number of concurrent entitlements actually being consumed</td></tr>');
}


function button_show_details(pane){
        var show_details = $('<button id=show_details class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
        pane.append(show_details);
        pane.append('<br><br>');
}

function button_details(pane, id,  btn_txt){
        var details = $('<button id=' + id + ' class="show-detail-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >' + btn_txt + '</button>');
        pane.append(details);
        pane.append('<br><br>');
}

function filter_button(pane, id,  btn_txt){
        var details = $('<button id=' + id + ' class="filter-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >' + btn_txt + '</button>');
        pane.append(details);
}




