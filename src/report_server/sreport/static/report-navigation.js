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
    if (hide){
    	document.getElementById("filter_toggle").style.display = "none";
    	toggle_report_form()
    }
    if (!hide){
        document.getElementById("filter_toggle").style.display = "block";
        document.getElementById("default-report-submit").style.display = "block";
        toggle_report_form()
    }
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
    form_filter_link_hide();
    removeActiveNav();
    $('#report_button').addClass('active');
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



