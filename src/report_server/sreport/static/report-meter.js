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
    setupCreateDatesForm();
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


function setupCreateForm(){
    var select_contract = $('#contract');
    var select_rhic = $('#rhic');
    var select_env = $('#env');
    
    select_contract.empty();
    select_rhic.empty();
    select_env.empty();
    
    var FormDatum = Backbone.Model.extend({});

    var FormData = Backbone.Collection.extend({
      model: FormDatum,
      url: '/report-server/meter/report_form/'
    });
    
    var AppView = Backbone.View.extend({
      
      initialize: function() {
        _.bindAll(this, 'render');
        this.collection.bind('reset', this.render);
        this.collection.fetch();
      },
      
      render: function(){

        this.collection.each(function(item) {
            var list = item.get('contracts')
            
            select_contract.append($('<option selected value=All>All</option>'));
            for (i in list){
                select_contract.append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }
            
            select_rhic.append($('<option selected value=All>All</option>'));
            var list = item.get('list_of_rhics')
            for (i in list){
               select_rhic.append($('<option value=' + list[i][0] + '>' + list[i][1] + '</option>'));
            }
            var list = item.get('environments')
            for (i in list){
               select_env.append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }
         
        });
        
        select_contract.chosen();
        select_rhic.chosen();
        select_env.chosen();
      }
      
    });
    
    var appview = new AppView({ collection: new FormData() });

}

function setupCreateDatesForm(){
    date_0 = Date.today();
    date_1 = (1).months().ago();
    date_2 = (2).months().ago();
    
    $('#byMonth').append($('<option  value=' + '-1' + ' ></option>'));
    
    [date_0, date_1, date_2].forEach(function(item){
        $('#byMonth').append($('<option selected value=' + item.toString("M") + ',' + item.toString("yyyy") +  '>' + item.toString("MMM") + ' ' + item.toString("yyyy") + '</option>'));
    });

    $('#startDate').datepicker();
    $('#endDate').datepicker();
    $('#byMonth').chosen();
}


function updateListOfRHICS() {

}



function createReport(event) {
    event.preventDefault();
    form_filter_link_hide(false);
    if (logged_in){
        var CreateReport = Backbone.Model.extend({
            url: '/report-server/meter/report/'
        });
        
        var data = {
            byMonth:            $('#byMonth').val(),
            startDat:           $('#startDate').val(),
            endDate:            $('#endDate').val(),
            contract_number:    $('#contract').val(),
            rhic:               $('#rhic').val()
        };
        
        var createReport = new CreateReport();
        console.log(createReport.toJSON());
        
        createReport.save( data, {
            success: function(model, response){
                console.log('SUCCESS');
                console.log(response);
                
                $('#report_pane > div').empty();
                var pane = '#report_pane > div';
                //populateReportBB(response, pane );
                populateReportBG(response, pane );
                openReport();
            }
        });
        
        }
        
	
}

function populateReportBG(rtn, pane) {
    var pane = $('#report_pane > div');
    var this_div = $('<div this_rhic_table>');
    pane.append('<h3>Date Range: ' + rtn.start.substr(0, 10) + ' ----> ' + rtn.end.substr(0, 10) + '</h3>');
    pane.append('<br><br>');
    var show_details = $('<button id=show_details style="float: right" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
    var Report = {};
    

    
    var Report = Backbone.Model.extend();
    
    var Reports = Backbone.Collection.extend({
        model: Report
        
    })
    
    var PageableReports = Backbone.PageableCollection.extend({
        model: Report,
        state: {
            pageSize: 3
        },
        mode: "client"
        
    })
        
    var mylist = []
    for (i = 0; i < rtn.list.length; i++){
        for (j = 0; j < rtn.list[i].length; j++){
            var row = rtn.list[i][j];
            row.description = [row.product_name, row.sla, row.support, row.facts];
            row.action = [row.start, row.end, row.description, row.filter_args_dict];
            mylist.push(row);
            
        }
    }
    var reports = new Reports(mylist);
    var pageable_reports = new PageableReports(mylist);
            
    var columns = [{
      name: "rhic", 
      label: "RHIC:", 
      editable: false,
      cell: "string"
    }, {
      name: "product_name",
      label: "Product:",
      editable: false,
      cell: "string"
    }, {
      name: "sla",
      label: "SLA:",
      editable: false,
      cell: "string"
    }, {
      name: "support",
      label: "Support:",
      editable: false,
      cell: "string"
    }, {
      name: "contract_use",
      label: "Contract Use:",
      editable: false,
      cell: "string"
    }, {
      name: "nau",
      label: "Usage:",
      editable: false,
      cell: "string"
    }, {
      name: "compliant",
      label: "Compliant:",
      editable: false,
      cell: "string"
    }, {
      name: "action",
      label: "Action:",
      editable: false,
      cell: "string"
      }];
    
    
 
    // w/o paging
    var grid = new Backgrid.Grid({
      columns: columns,
      collection: reports
    })
    
    
    // w/ paging
    var pageableGrid = new Backgrid.Grid({
        columns: columns,
        collection: pageable_reports,
        footer: Backgrid.Extension.Paginator,
        
    });
    
    //pane.append(grid.render().$el);
    pane.append(pageableGrid.render().$el);
    
    show_details.click(function (){
        this_div.toggle("slow");
    })
return rtn.list.length


}


function populateReportBB(rtn, pane) {
    var pane = $('#report_pane > div');
    var this_div = $('<div this_rhic_table>');
    pane.append('<h3>Date Range: ' + rtn.start.substr(0, 10) + ' ----> ' + rtn.end.substr(0, 10) + '</h3>');
    pane.append('<br><br>');
    var show_details = $('<button id=show_details style="float: right" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" >Show Details</button>');
    var Report = {};
    

    
    var Report = Backbone.Model.extend();
    
    var Reports = Backbone.Collection.extend({
        model: Report
        
    })
    
    
        
    var mylist = [];
    id = 0;
    for (i = 0; i < rtn.list.length; i++){
        for (j = 0; j < rtn.list[i].length; j++){
            //unbelievable this needs an id
            var row = rtn.list[i][j];
            row.id = id;
            mylist.push(row);
            id++;
            
        }
    }

    
    var reports = new Reports(mylist);
            
    grid = new bbGrid.View({
        container: pane,
        collection: reports,
        onRowClick: function(){
            var models = this.getSelectedModels();
            if( !_.isEmpty(models)) {
                m = _.first(models);
                var description = 'Product: '+ m.get('product_name') + ', SLA:' + m.get('sla') + ', Support: ' + m.get('support') + ' Facts: ' + m.get('facts') ;
                createMax(m.get('start'), m.get('end'), description, m.get('filter_args_dict'));
            } else {
                console.log('ERROR');
            }
        },

        colModel: [{ title: 'ID', name: 'id', index: true, sorttype: 'number' },
                   { title: 'RHIC:', name: 'rhic' },
                   { title: 'Product:', name: 'product_name'},
                   { title: 'SLA:', name: 'sla'},
                   { title: 'Support:', name: 'support'},
                   { title: 'Contract Use:', name: 'contract_use'},
                   { title: 'NAU:', name: 'nau'},
                   { title: 'Compliant:', name: 'compliant'}
                   
                   ]
    
    });
    pane.append('<br><br><br>');
    //pane.append(grid.render().$el);
    //pane.append(grid.render().$el);
    
    show_details.click(function (){
        this_div.toggle("slow");
    })
return rtn.list.length


}


function createMax(start, end, description, filter_args) {
    console.log(start + end + description + filter_args);
    
}



function create_default_report(event){
   
}

function createDetail(date, description,  filter_args) {
   
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


