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
    
	hide_pages();
    setupLoginForm();
    setupLoginButtons();
    setupCreateForm();
    openCreate();
    navButtonDocReady();
    
    
    

});

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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


function setupCreateFormOLD() {
    setupReportForm();

    $.ajax({
        url: '/report-server/meter/report_form/',
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

function setupCreateForm(){
    var select_contract = $('#contract');
    var select_rhic = $('#rhic');
    var select_env = $('#env');
    
    var Contract = Backbone.Model.extend({});

    var Contracts = Backbone.Collection.extend({
      model: Contract,
      url: '/report-server/meter/report_form/'
    });
    
    var AppView = Backbone.View.extend({
      
      initialize: function() {
        _.bindAll(this, 'render', 'fetchData');
        this.collection.bind('reset', this.render);
        this.collection.fetch();
      },
      
      render: function(){

        this.collection.each(function(item) {
            var list = item.get('contracts')
                for (i in list){
                    select_contract.append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
                }
            var list = item.get('list_of_rhics')
                for (i in list){
                    select_rhic.append($('<option value=' + list[i][1] + '>' + list[i][1] + '</option>'));
                }
            var list = item.get('environments')
                for (i in list){
                    select_env.append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
                }
         
        });
        
        select_contract.chosen();
        select_rhic.chosen();
        select_env.chosen();
      },
      
      fetchData: function() {
        this.collection.fetch();
      }
    });
    
    var appview = new AppView({ collection: new Contracts() });
    
    date_0 = Date.today();
    date_1 = (1).months().ago();
    date_2 = (2).months().ago();
    
    $('#byMonth').append($('<option  value=' + '-1' + ' ></option>'));
    $('#byMonth').append($('<option selected value=' + date_0.toString("M") + ',' + date_0.toString("yyyy") +  '>' + date_0.toString("MMM") + ' ' + date_0.toString("yyyy") + '</option>'));
    $('#byMonth').append($('<option selected value=' + date_1.toString("M") + ',' + date_1.toString("yyyy") +  '>' + date_1.toString("MMM") + ' ' + date_1.toString("yyyy") + '</option>'));
    $('#byMonth').append($('<option selected value=' + date_2.toString("M") + ',' + date_2.toString("yyyy") +  '>' + date_2.toString("MMM") + ' ' + date_2.toString("yyyy") + '</option>'));
    
    $('#startDate').datepicker();
    $('#endDate').datepicker();
    $('#byMonth').chosen();
    
}


function updateListOfRHICS() {

}



function createReport(event) {
	
}

function create_default_report(event){
   
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

function change_rhic_form(data){
    
}


    
function loadContent() {
   
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


