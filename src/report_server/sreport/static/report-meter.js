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
            url: '/report-server/meter/report/'
        });
        
        var data = {
            contract_number:    $('#contract').val(),
            rhic:               $('#rhic').val()
        };
        
        if ($('#byMonth').val() == ""){
            data.startDate =  $('#startDate').val();
            data.endDate =  $('#endDate').val();
        }
        else{
            data.byMonth = $('#byMonth').val();
        }
        
        
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

    var mylist = []
    for ( i = 0; i < rtn.list.length; i++) {
        for ( j = 0; j < rtn.list[i].length; j++) {
            var row = rtn.list[i][j];
            mylist.push(row);

        }
    }
    var reports = new Reports(mylist);
    var pageable_reports = new PageableReports(mylist);

    var columns = [{
        name : "rhic",
        label : "RHIC:",
        editable : false,
        cell : "string"
    }, {
        name : "product_name",
        label : "Product:",
        editable : false,
        cell : "string"
    }, {
        name : "sla",
        label : "SLA:",
        editable : false,
        cell : "string"
    }, {
        name : "support",
        label : "Support:",
        editable : false,
        cell : "string"
    }, {
        name : "contract_use",
        label : "Contract Use:",
        editable : false,
        cell : "string"
    }, {
        name : "nau",
        label : "Usage:",
        editable : false,
        cell : "string"
    }, {
        name : "compliant",
        label : "Compliant:",
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

        var description = {};
        description["Product"] = model.get('product_name');
        description["SLA"] = model.get('sla');
        description["Support"] = model.get('support');
        description["Facts"] = model.get('facts');
        var filter_args = JSON.parse(model.get('filter_args_dict'));
        createMax(model.get('start'), model.get('end'), description, filter_args);
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
        table.append('<img border=0 src="/static/fail.png") alt="fail" width="100" height="100">');
        pane.append(table);
        pane.append(pageableGrid.render().$el);
        button_run_another_report(pane);
        glossary_report(pane);
    } else {
        console.log('pass')
        result_ui = $('#report_pane > div');
        var table = $('<table width=\"60%\" align=\"right\"></table>');
        table.append('<img border=0 src="/static/pass.jpg") alt="fail" width="100" height="100">');
        pane.append(table);
    }

    

    return rtn.list.length

}


    

function createMax(start, end, description, filter_args) {
    closeDetail();
    closeMax();   
        
    var MaxReport = Backbone.Model.extend({
        url : '/report-server/meter/max_report/'
    });

    var data = {
        "start": start,
        "end": end,
        "description": description,
        "filter_args_dict": filter_args
    };
    
    console.log(data);

    var maxReport = new MaxReport();

    maxReport.save(data, {
        success : function(model, response) {
            console.log('SUCCESS');
            console.log(response);

            $('#max_pane > div').empty();
            var pane = '#max_pane > div';
            
            openMax();
            populateMaxReport(model);
        }
    }); 

}

function populateMaxReport(rtn) {
    //SETUP
    var pane = $('#max_pane');
    pane.empty();
    
    var contract = rtn.get('daily_contract');
    var date = rtn.get('date');
    var description = rtn.get('description');
    var end = rtn.get('end');
    var filter_args = rtn.get('filter_args');
    var list = rtn.get('list');
    var mcu = rtn.get('mcu');
    var mdu = rtn.get('mdu');
    var start = rtn.get('start');
    
    var desc_start = new Date(0);
    var desc_end = new Date(0);
    desc_start.setUTCSeconds(start);
    desc_end.setUTCSeconds(end);
    
    setup_description(pane, desc_start.toDateString().substr(0,10) + ' ----> ' + desc_end.toDateString().substr(0,10), description);
    //SETUP

    //GRAPH
    if (list.length > 0){
        pane.append($('<br></br>'));
        pane.append($('<div id="chartdiv" style="height:400px;width:100%; "></div>'));
        
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
               createDetail( date_to_send, description, filter_args);
              });
    
        glossary_mdu(pane);
        //GRAPH
        
        //BEGIN LIST
        button_show_details(pane);
        var list_view = $('<div id=list_view>');

        var Max = Backbone.Model.extend();
    

        var PageableMaxList = Backbone.PageableCollection.extend({
            model: Max,
            state: {
                pageSize: 25
            },
            mode: "client"
            
        });
        
        
        
        var columns = [{
            name: "date",
            label: "Date",
            cell: "string"
        },{
            name: "mdu",
            label: "MDU",
            cell: "string"
        },{
            name: "mcu",
            label: "MCU",
            cell: "string"
        }];
        
        var ClickableMaxRow = Backgrid.Row.extend({
        events: {
            "click": "onClick"
        },
        onClick: function () {
            Backbone.trigger("maxrowclicked", this.model);
           }
        });
    
        Backbone.on("maxrowclicked", function (model) {
            console.log(model.get('date') + JSON.stringify(description) + JSON.stringify(filter_args));
            createDetail(model.get('date'), description, filter_args);
        });
        
        var mylist = new PageableMaxList(list);
        var pageableGrid = new Backgrid.Grid({
            columns: columns,
            collection: mylist,
            footer: Backgrid.Extension.Paginator,
            row: ClickableMaxRow
        
        });


        
        list_view.append(pageableGrid.render().$el);
        list_view.hide();
        pane.append(list_view);
        
        
        $("button").click(function (){
            list_view.toggle("slow");
            
          })
          
    } 
}

function createDetail(date, description,  filter_args) {
    console.log('in create detail');
    
    var Detail = Backbone.Model.extend({
        url : '/report-server/meter/details/'
    });

    var data = {
        "date": date,
        "description": description,
        "filter_args_dict": filter_args
    };
    
    console.log(data);

    var details = new Detail();

    details.save(data, {
        success : function(model, response) {
            console.log('SUCCESS');
            console.log(response);

            populateDetailReport(model);
            openDetail();

            $('#detail_button').removeClass('disabled');
            $('#detail_button').on("click", openDetail);
        }
    }); 

}

function populateDetailReport(rtn) {
    //setup
    var date = rtn.get('date');
    var description = rtn.get('description');
    var filter_args = rtn.get('filter_args_dict');
    var list = rtn.get('list');

    console.log('in populate Detail Report');
    $('#details').empty();
    $('#instance_details').empty();
    var desc_date = new Date(0);
    desc_date.setUTCSeconds(date);

    var pane = $('#details');
    setup_description(pane, desc_date.toDateString().substr(0, 10), description)
    //setup

    var Detail = Backbone.Model.extend();

    var PageableDetailList = Backbone.PageableCollection.extend({
        model : Detail,
        state : {
            pageSize : 10
        },
        mode : "client"

    });

    var columns = [{
        name : "instance",
        label : "Instance:",
        cell : "string",
        editable: false
    }, {
        name : "count",
        label : "Count:",
        cell : "string",
        editable: false
    }];

    var ClickableDetailRow = Backgrid.Row.extend({
        events : {
            "click" : "onClick"
        },
        onClick : function() {
            Backbone.trigger("detailrowclicked", this.model);
        }
    });

    Backbone.on("detailrowclicked", function(model) {
        console.log(model.get('instance'));
        createInstanceDetail(date, model.get('instance'), filter_args);
    });

    var mylist = new PageableDetailList(list);

    var pageableGrid = new Backgrid.Grid({
        columns : columns,
        collection : mylist,
        footer : Backgrid.Extension.Paginator,
        row : ClickableDetailRow

    });
    pane.append('<br><br>')
    pane.append(pageableGrid.render().$el);

}

function createInstanceDetail(date, instance, filter_args) {
    var data = {
        "date": date,
        "instance": instance,
        "filter_args_dict": filter_args
    };
    console.log(data);
    var InstanceDetail = Backbone.Model.extend({
        url : '/report-server/meter/instance_details/'
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
    
    list = rtn.get('list');
    
    var InstanceCheckin = Backbone.Model.extend();
    
    var PageableInstanceCheckin = Backbone.PageableCollection.extend({
        model : InstanceCheckin,
        state : {
            pageSize : 10
        },
        mode : "client"
    });
    
    var columns = [{
        name : "instance_identifier",
        label : "UUID:",
        cell : "string",
        editable: false
    }, {
        name : "product_name",
        label : "Product:",
        cell : "string",
        editable: false
    },{
        name : "product_name",
        label : "Product:",
        cell : Backgrid.SelectCell.extend({
        optionValues: [["RHEL Server", "rhel_server"],
                       ["RHEL HA", "rhel_ha"],
                       ["RHEL Server for Education", "rhel_edu"],
                       ["JBoss EAP", "jboss_eap"]]
                    })
    }, {
        name : "hour",
        label : "Time:",
        cell : "string",
        editable: false
    }, {
        name : "memtotal",
        label : "Memory:",
        cell : "string",
        editable: false
    }, {
        name : "cpu_sockets",
        label : "Sockets:",
        cell : "string",
        editable: false
    }, {
        name : "environment",
        label : "Domain:",
        cell : "string",
        editable: false
    }];
    
    var mylist = new PageableInstanceCheckin(list);

    var pageableGrid = new Backgrid.Grid({
        columns : columns,
        collection : mylist,
        footer : Backgrid.Extension.Paginator

    });
    pane.append('<br><br>')
    pane.append(pageableGrid.render().$el);
    
    if (!$('#instance_details').is(':visible')) {
        $('#instance_details').show();
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
        data['contract_number'] = "All"
        data['rhic'] = "null"
        data['env'] = "All"
        
        console.log(data);
        var DefaultReport = Backbone.Model.extend({
            url : '/report-server/meter/default_report/'
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








