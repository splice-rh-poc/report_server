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
    openCreateLogin();
    navButtonDocReady();
    
    
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
    var select_status = $('#status');
    var select_rhic = $('#rhic');
    var select_env = $('#env');
    var select_org = $('#org');

    
    select_status.empty();
    select_rhic.empty();
    select_env.empty();
    select_org.empty();
    
    var FormDatum = Backbone.Model.extend({});

    var FormData = Backbone.Collection.extend({
      model: FormDatum,
      url: '/report-server/space/report_form/'
    });
    
    var AppView = Backbone.View.extend({
      
      initialize: function() {
        _.bindAll(this, 'render');
        this.collection.bind('reset', this.render);
        this.collection.fetch();
      },
      
      render: function(){

        this.collection.each(function(item) {
            var list = item.get('status')
            
            select_status.append($('<option selected value=Failed>Failed</option>'));
            select_status.append($('<option selected value=All>All</option>'));
            for (i in list){
                name = list[i].charAt(0).toUpperCase() + list[i].slice(1);
                select_status.append($('<option value=' + list[i] + '>' + name + '</option>'));
            }
            
            var list = item.get('environments')
            select_env.append($('<option selected value=All>All</option>'));
            for (i in list){
               select_env.append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }

            var list = item.get('organizations')
            select_org.append($('<option selected value=All>All</option>'));
            for (i in list){
               select_org.append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }
         
        });
        
        select_status.chosen();
        select_env.chosen();
        select_org.chosen();
      }
      
    });
    
    var appview = new AppView({ collection: new FormData() });

}

function setupCreateDatesForm(){
    date_2 = Date.today();
    date_1 = (1).months().ago();
    date_0 = (2).months().ago();
    
    $('#byMonth').append($('<option  value></option>'));
    
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
            url: '/report-server/space/report/'
        });
        
        var data = {
            status:    $('#status').val(),
            env:    $('#env').val(),
            org:    $('#org').val()
        };
        
        if ($('#byMonth').val() == ""){
            data.startDate =  $('#startDate').val();
            data.endDate =  $('#endDate').val();
        }
        else{
            data.byMonth = $('#byMonth').val();
        }
        
        console.log(data);
        var createReport = new CreateReport();
        console.log(createReport.toJSON());
        
        createReport.save( data, {
            success: function(model, response){
                console.log('SUCCESS');
                console.log(response);
                
                $('#report_pane > div').empty();
                var pane = '#report_pane > div';
                populateReport(response, pane );
                openReport();
            }
        });
        
        }
        
	
}

function create_default_report(event){
    document.getElementById("report_form").style.display = "none"
    $('#default_report_results_ui').empty();
    $('#default_report_results').empty();
    event.preventDefault();
    
    if (logged_in) {
        var data = {};
        var dtoday = Date.today();
        console.log(dtoday);

        data['startDate'] = (3).months().ago().toString("M/d/yyyy");
        data['endDate'] = Date.today().toString("M/d/yyyy");
        data['env'] = "All"
        data['org'] = "All"
        data['status'] = "All"
        
        console.log(data);
        var DefaultReport = Backbone.Model.extend({
            url : '/report-server/space/report/'
        });
    
        var defaultReport = new DefaultReport();
    
        
        defaultReport.save(data, {
            success : function(model, response) {
                console.log('SUCCESS');
                console.log(response);
                
                $('#report_pane > div').empty();
                var pane = '#report_pane > div';
                var num = populateReport(response, pane );
                openReport();
                
                //$('#default_report_results').append("<br><br><br><br><br><br>");
                //num = populateReport(response, "#default_report_results");
                //fact = populateFactComplianceReport(response.biz_list, "#default_report_results");

            }
        });

        
    }
    
    
   
}


function populateReport(rtn, pane) {
    var pane = $(pane);
    var this_div = $('<div this_rhic_table>');

    setup_description(pane, rtn.start.substr(0, 10) + ' ----> ' + rtn.end.substr(0, 10));
    var Report = {};

    var Report = Backbone.Model.extend();

    var Reports = Backbone.Collection.extend({
        model : Report

    });

    var PageableReports = Backbone.PageableCollection.extend({
        model : Report,
        state : {
            pageSize : 10
        },
        mode : "client"

    });

    var reports = new Reports(rtn.list);
    var pageable_reports = new PageableReports(rtn.list);

    var columns = [{
        name : "systemid",
        label : "System ID:",
        editable : false,
        cell : "string"
    },{
        name : "splice_server",
        label : "Satellite Server:",
        editable : false,
        cell : "string"
    }, {
        name : "organization",
        label : "Organization:",
        editable : false,
        cell : "string"
    }, {
        name : "status",
        label : "Subscription Status:",
        editable : false,
        cell : "string"
    }];

    var ClickableRow = Backgrid.Row.extend({
        events : {
            "click" : "onClick"
        },
        onClick : function() {
            Backbone.trigger("rowclicked", this.model);
        }
    });

    Backbone.on("rowclicked", function(model) {
        console.log('in row click');
        //date, instance, filter_args
        createInstanceDetail(model);

    });

    // w/ paging
    var pageableGrid = new Backgrid.Grid({
        columns : columns,
        collection : pageable_reports,
        footer : Backgrid.Extension.Paginator,
        row : ClickableRow

    });

    fact = 0;

    if (rtn.list.length + fact > 0) {
        console.log('fail')
        var table = $('<table width=\"60%\" align=\"right\"></table>');
        table.append('<img border=0 src="/static/fail.jpg") alt="fail" width="100" height="100">');
        pane.append(table);
        pane.append(pageableGrid.render().$el);
        button_run_another_report(pane);
    } else {
        console.log('pass')
        result_ui = $('#report_pane > div');
        var table = $('<table width=\"60%\" align=\"right\"></table>');
        table.append('<img border=0 src="/static/pass.jpg") alt="fail" width="100" height="100">');
        pane.append(table);
    }

    

    return rtn.list.length

}


    

function createInstanceDetail(model) {
    console.log('in createInstanceDetail')
    date = model.get("date")
    instance = model.get("instance_identifier")
    var data = {
        "date": date,
        "instance": instance,
    };
    console.log(data);
    var InstanceDetail = Backbone.Model.extend({
        url : '/report-server/space/instance_details/'
    });

    var instanceDetails = new InstanceDetail();

    instanceDetails.save(data, {
        success : function(model, response) {
            console.log('SUCCESS');
            console.log(response);

            populateInstanceDetailReport(model);
            openDetail(); // this shouldn't be needed, but no harm in calling it again
            $('#detail_button').on("click", openDetail);
        }
    });
    
}

function populateInstanceDetailReport(rtn) {
    console.log('in pop instc details');
    var pane = $('#instance_details');
    pane.empty();
    
    var facts = rtn.get('facts');
    var product_info = JSON.parse(rtn.get('product_info'))
    var status = rtn.get('status')
    var splice_server = rtn.get('splice_server')
    var system_id = rtn.get('system_id')
    var instance_identifier = rtn.get('instance_identifier')
    var date = rtn.get('date')
    var spacewalk = rtn.get('space_hostname')
    
    var ProductModel = Backbone.Model.extend();

    var ProductCollection = Backbone.Collection.extend({
        model : ProductModel
    });
    
    var CustomSelectCellEditor = Backgrid.SelectCellEditor.extend({
        save: function (e) {
            console.log('in custom save')
            this.model.set(this.column.get("name"), this.formatter.toRaw(this.$el.val()));
            console.log('get value and bind to pool here');
            this.trigger("done");
            console.log("done, successfully saved " + this.formatter.toRaw(this.$el.val()));
        }
    });
    
    /*
     * curl -k -u admin:admin https://localhost:8443/candlepin/owners/admin/pools?consumer=e69871bb-170c-426a-844d-18f26632ffa4
     */
    
    
    var columnsInstance = [{
        name : "product_id",
        label : "Subscription ID:",
        cell : "string",
        editable: false
    },{
        name : "product_name",
        label : "Subscription:",
        cell : "string",
        editable: false
    },{
        name : "product_account",
        label : "Account:",
        cell : "string",
        editable: false
    },{
        name : "product_quantity",
        label : "Number of Consumed:",
        cell : "string",
        editable: false
    }];


    var columnsPool = [{
        name : "pool_uuid",
        label : "Pool UUID:",
        cell : "string",
        editable: false
    },{
        name : "pool_active",
        label : "Pool Active?",
        cell : "string",
        editable: false
    },{
        name : "pool_quantity",
        label : "Available:",
        cell : "string",
        editable: false
    },{
        name : "pool_start",
        label : "Start:",
        cell : "string",
        editable: false
    },{
        name : "pool_end",
        label : "End:",
        cell : "string",
        editable: false
    }];
    
    var myinstance = new ProductCollection(product_info);

    var gridInstance = new Backgrid.Grid({
        columns : columnsInstance,
        collection : myinstance
    });


    var gridPool = new Backgrid.Grid({
        columns : columnsPool,
        collection : myinstance
    });

    pane.append("<a href=https://" + spacewalk + "/rhn/systems/details/Overview.do?sid="+ system_id + ">link to system</a>")
    pane.append('<br>');
    pane.append('<h3>Instance Detail:</h3>');
    pane.append(gridInstance.render().$el);
    pane.append('<br>');
    pane.append('<h3>Pool Detail:</h3>');
    pane.append(gridPool.render().$el);
    pane.append('<br>');
    pane.append('<h3>Provided Products:</h3>');
    

    $.each(product_info, function(key, value){
        $.each(value.pool_provided_products, function( key, value ){
            pane.append("<li>" + value.name  + "</li>")
        });
    });
    
    pane.append('<br>');
    pane.append('<h3>Instance Facts:</h3>');


    var facts = JSON.parse( facts );

    $.each(facts, function( key, value ){
        pane.append("<li>" + key + ": " + value + "</li>")
    });

    if (!$('#instance_details').is(':visible')) {
        $('#instance_details').show();
    }

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








