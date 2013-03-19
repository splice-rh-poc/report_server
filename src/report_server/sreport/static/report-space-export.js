/* 
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
     if($.trim($('#status').val()) != "") {
         data['status'] = $('#status').val();
     }
     

     data['org'] = $('#org').val();
     data['env'] = $('#env').val();
     
     $.download('/report-server/space/export', data, 'get');

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
        jQuery('<form action="/report-server/space/export/" method="'+ ('get') +'">'+inputs+'</form>')
        .appendTo('body').submit().remove();
        //alert('Please wait while the export is generated')

};

