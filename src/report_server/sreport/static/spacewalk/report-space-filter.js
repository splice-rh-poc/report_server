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

  function createFilter(){
    var pane = $('#default_report_controls');
    pane.empty();

    
    
    var FormDatum = Backbone.Model.extend({});

    var FormData = Backbone.Collection.extend({
      model: FormDatum,
      url: '/report-server/space/report_form/',
    });
    
    var AppView = Backbone.View.extend({
      template: _.template($("#create-filter-form").html()),
      el: pane,
      
      initialize: function() {
        _.bindAll(this, 'render');
        this.collection.bind('reset', this.render);
        this.collection.fetch();
        //$(this.el).append(this.template( { list: this.collection.models } ));
        
      },
      
      render: function(){
        //init select boxes
        /* using variables for the elements is not working atm
        var filter_name = $('#filter_name');
        var select_status = $('#status');
        var select_rhic = $('#rhic');
        var select_env = $('#env');
        var select_org = $('#org');
        var select_sys_host = $('#sys_host');
        var select_sys_id = $('#sys_id');
        */

        $('#filter_name').empty();
        $('#status').empty();
        $('#rhic').empty();
        $('#environment').empty();
        $('#organization').empty();
        $('#sys_host').empty();
        $('#sys_id').empty();

        console.log(this.collection);
        $(this.el).append(this.template( { list: this.collection.models } ));

        //SETUP DATES:
        date_2 = Date.today();
        date_1 = (1).months().ago();
        date_0 = (2).months().ago();
        
        $('#by_month').append($('<option  value></option>'));
        
        [date_0, date_1, date_2].forEach(function(item){
            $('#by_month').append($('<option selected value=' + item.toString("M") + ',' + item.toString("yyyy") +  '>' + item.toString("MMM") + ' ' + item.toString("yyyy") + '</option>'));
        });

        
        //SETUP Splice Report Filter Data
        this.collection.each(function(item) {
            var list = item.get('status')
            
            $('#status').append($('<option selected value=Failed>Failed</option>'));
            $('#status').append($('<option selected value=Inactive>Inactive</option>'));
            $('#status').append($('<option selected value=All>All</option>'));
            for (i in list){
                name = list[i].charAt(0).toUpperCase() + list[i].slice(1);
                $('#status').append($('<option value=' + list[i] + '>' + name + '</option>'));
            }
            
            var list = item.get('environments')
            $('#environment').append($('<option selected value=All>All</option>'));
            for (i in list){
               $('#environment').append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }

            var list = item.get('organizations')
            $('#organization').append($('<option selected value=All>All</option>'));
            for (i in list){
               $('#organization').append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }

            var list = item.get('sys_host')
            $('#sys_host').append($('<option selected value=All>All</option>'));
            for (i in list){
               $('#sys_host').append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }

            var list = item.get('sys_id')
            $('#sys_id').append($('<option selected value=All>All</option>'));
            for (i in list){
               $('#sys_id').append($('<option value=' + list[i] + '>' + list[i] + '</option>'));
            }
         
        });
        

        $('#start_date').datepicker();
        $('#end_date').datepicker();
        $('#by_month').chosen();
        $('#status').chosen();
        $('#environment').chosen();
        $('#organization').chosen();
        $('#sys_host').chosen({ max_choices: 1 });
        $('#sys_id').chosen({ max_choices: 5 });
      }
      
    });
    
    var appview = new AppView({ collection: new FormData() });

}


function filterSave(event){
    event.preventDefault();

    var pane = $('#default_report_controls');

    var CreateFilter = Backbone.Model.extend({
            urlRoot: '/report-server/api/v1/filter/'
    });
        
    
    var data = {
            filter_name: $('#filter_name').val(),
            filter_description: $('#filter_description').val(),
            status: $('#status').val(),
            environment:    $('#environment').val(),
            organization:    $('#organization').val()
    };

    if ($('#by_month').val() == ""){
            data.start_date =  $('#start_date').val();
            data.end_date =  $('#end_date').val();
    }
    else{
        data.byMonth = $('#by_month').val();
    }

    if ( !!$('#id').val() ){
        data.id = $('#id').val();
        data.start_date =  $('#start_date').val();
        data.end_date =  $('#end_date').val();
    }
    console.log(data);
    var createFilter = new CreateFilter();
    createFilter.save( data, {
        success: function(model, response){
            console.log('SUCCESS');
            console.log(response);
            filterInitialPopulate(response);
            toggle_report_form();
      
        },
        error: function(model, response){
            console.log(response);
        }
    });

}

function filterInitialPopulate(){

    var pane = $('#default_report_controls');

    var Filter = Backbone.Model.extend({
        url: "/report-server/api/v1/filter/",
    });

    var Filters = Backbone.Collection.extend({
       url: "/report-server/api/v1/filter/", 
    })

    var filters = new Filters();

  

    filters.fetch({
        success: function(model, response){
            filterPopulate(response);
      
        }
    });

}

function filterInitialPopulateOptions(){

    var pane = $('#default_report_controls');

    var CreateFilter = Backbone.Model.extend({
        urlRoot: "/report-server/api/v1/filter/"
    });

    var createFilter = new CreateFilter();
    createFilter.fetch({
        success: function(model, response){
            filterPopulateOptions(response);
        }
    });

}

function filterPopulate(response){

    var pane = $('#default_report_controls');
    pane.empty();

    var Filter = Backbone.Model.extend({
        url: "/report-server/api/v1/filter/",
    });

    var Filters = Backbone.PageableCollection.extend({
        
        model : Filter,
        url: "/report-server/api/v1/filter/",
        state : {
            pageSize : 5
        },
        mode: "client"
    });

    

    var redhat_default = new Filter({
      by_month: null,
      end_date: "3/31/2013",
      environment: "All",
      filter_description: "This is report sent to Red Hat",
      filter_name: "Red Hat Default Report",
      organization: null,
      owner: null,
      start_date: "3/1/2013",
      end_date: "3/31/2013",
      status: "All",
      sys_host: null,
      id: 0,
      
    });

    /*
    Create the default Red Hat Report Here and only here..
    So it can not be deleted or removed from the database
    Adding the default report first ensures it is always the first in the list
    */
    var filters = new Filters([redhat_default]);
    var load = response.objects;
    load.forEach(function(item){
        filters.push(item);
    });

    console.log('WES HERE 2');
    console.log(response.objects);


    var columns = [{
        name : "filter_name",
        label : "Filter Name:",
        editable : false,
        cell : "string"
    },
    {  
        name : "filter_description",
        label : "Filter Description:",
        editable : false,
        cell : "string"
    },{
        name : "start_date",
        label : "Start Date:",
        editable : false,
        cell : "string"
    },{
        name : "end_date",
        label : "End Date:",
        editable : false,
        cell : "string"
    }];

    var ClickableRow = Backgrid.Row.extend({
        events : {
            "click" : "onClick"
        },
        onClick : function() {
            Backbone.trigger("goToReport", this.model);
        }
    });

    Backbone.on("goToReport", function(model) {
        console.log('in row click');
        createReportFromSavedFilter(model);
        
    });

    var grid = new Backgrid.Grid({
        columns : columns,
        collection : filters,
        row: ClickableRow,
        footer : Backgrid.Extension.Paginator,
    });

    var clientSideFilter = new Backgrid.Extension.ClientSideFilter({
        collection: filters,
        placeholder: "Search for filters",
        fields: {
          filter_name: 10,
          filter_description: 5
        },
        
        ref: "id",
        wait: 150
    });

    pane.append(clientSideFilter.render().$el);
    pane.append(grid.render().$el);
   
    
}



function filterPopulateOptions(response){

    var pane = $('#default_report_controls');
    var create_pane = $('#create_pane');
    create_pane.empty();
    pane.empty();
    var Filter = Backbone.Model.extend({
        urlRoot: "/report-server/api/v1/filter/",

    });

    var Filters = Backbone.PageableCollection.extend({
        model : Filter,
        urlRoot: "/report-server/api/v1/filter/",
        state : {
            pageSize : 5
        },
        mode: "client"
    });

    var filters = new Filters(response.objects);
   

    var columns = [{
        name : "filter_name",
        label : "Filter Name:",
        editable : false,
        cell : "string"
    },
    {  
        name : "filter_description",
        label : "Filter Description:",
        editable : false,
        cell : "string"
    },{
        name : "start_date",
        label : "Start Date:",
        editable : false,
        cell : "string"
    },{
        name : "end_date",
        label : "End Date:",
        editable : false,
        cell : "string"
    }];



    Backbone.on("goToReport", function(model) {
        console.log('in row click');
        createReportFromSavedFilter(model);
        
    });

    var grid = new Backgrid.Grid({
        initialize: function(){
            this.collection.bind("destroy", this.removeModel);
        },
        //columns: columns,
        columns: [{
    
            // name is a required parameter, but you don't really want one on a select all column
            name: "Select All",
            
            // Backgrid.Extension.SelectRowCell lets you select individual rows
            cell: "select-row",
            
            // Backgrid.Extension.SelectAllHeaderCell lets you select all the row on a page
            headerCell: "select-all",
            
          }].concat(columns),

        collection : filters,
        footer : Backgrid.Extension.Paginator,
        
    })

    //CREATE FILTER
    var clientSideFilter = new Backgrid.Extension.ClientSideFilter({
        collection: filters,
        placeholder: "Search for filters",
        fields: {
          filter_name: 10,
          filter_description: 5
        },
        
        ref: "id",
        wait: 150
    });

    //RENDER THE FILTER AND TABLE
    pane.append(clientSideFilter.render().$el);
    pane.append(grid.render().$el);


    filter_button(pane, "create_filter_button", " Create ");
    filter_button(pane, "delete_filter_button", " Delete ");
    filter_button(pane, "edit_filter_button", " Edit ");
    filter_button(pane, "export_filter_button", " Export ");


    $("#create_filter_button").click(function (){
        createFilter();
            
    })

    $("#delete_filter_button").click(function (){
        var selected = [];
        selected = grid.getSelectedModels(); // This is an array of models
        console.log("delete" + selected);
        for (i in selected){
                var remove=confirm("Delete filter with name " + selected[i].attributes.filter_name);
                if (remove == true){
                    filters.sync("delete", selected[i]);
                    grid.removeRow(selected[i], filters);
                    filters.remove(selected[i]);
                }
                else{
                    console.log('delete filter canceled');
                }

                //grid.removeRow(selected[i], filters);
                // THERE IS A BUG HERE W/ grid.getSelected   
            }
        setTimeout(filterInitialPopulateOptions(),4000);


    })

    $("#edit_filter_button").click(function (){
        var selected = grid.getSelectedModels(); // This is an array of models
        if (selected.length > 1) {
            alert("Please only select one filter to edit..");
        }
        else{
            var pane = $('#default_report_controls');
            pane.empty();
            var template = _.template($('#create-filter-form').html());
            console.log(JSON.stringify(selected[0].attributes));
            var attr = selected[0].attributes;
            pane.html(template({}));

            $('#status').append($('<option value=' + attr.status + '>' + attr.status + '</option>'));
            $('#environment').append($('<option value=' + attr.environment + '>' + attr.environment + '</option>'));
            $('#organization').append($('<option value=' + "All" + '>' + "All" + '</option>'));
            $('#sys_host').append($('<option value=' + "All" + '>' + "All" + '</option>'));
            $('#sys_id').append($('<option value=' + "All" + '>' + "All" + '</option>'));
            $('#filter_name')[0].value = attr.filter_name;
            $('#filter_description')[0].value = attr.filter_description;
            $('#id')[0].value = attr.id;

            //SETUP DATES:
            date_2 = Date.today();
            date_1 = (1).months().ago();
            date_0 = (2).months().ago();
            
            $('#by_month').append($('<option  value></option>'));
            
            [date_0, date_1, date_2].forEach(function(item){
                $('#by_month').append($('<option selected value=' + item.toString("M") + ',' + item.toString("yyyy") +  '>' + item.toString("MMM") + ' ' + item.toString("yyyy") + '</option>'));
            });


            $('#start_date').datepicker();
            $('#start_date').datepicker("setDate", attr.start_date);
            $('#end_date').datepicker();
            $('#end_date').datepicker("setDate", attr.end_date);
            $('#by_month').chosen();
            $('#status').chosen();
            $('#environment').chosen();
            $('#organization').chosen();
            $('#sys_host').chosen({ max_choices: 1 });
            $('#sys_id').chosen({ max_choices: 5 });

        }
            
    })

    $("#export_filter_button").click(function (){
            var selected = grid.getSelectedModels(); // This is an array of models
            if (selected.length > 1) {
                alert("Please only select one filter to export..");
            }
            
    })


}



function createReportFromSavedFilter(filter) {
    form_filter_link_hide(false);
    if (logged_in){
        var CreateReport = Backbone.Model.extend({
            url: '/report-server/space/report/'
        });
        var filter = filter.attributes;
        console.log(filter);
        
        var data = {
            status:  filter.status,
            env:    filter.environment,
            org:    filter.environment,
            startDate: filter.start_date,
            endDate: filter.end_date
        };
        
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
