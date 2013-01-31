<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://rhn.redhat.com/rhn" prefix="rhn" %>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>

<html:xhtml/>
<html>

<head>
<script language="javascript" type="text/javascript" src="/editarea/edit_area_full.js"></script>
<script language="javascript" type="text/javascript">
editAreaLoader.init({
        id : "contents"
        ,allow_toggle: true
        ,allow_resize: "both"
        ,display: "later"
        ,toolbar: "search, go_to_line, |, help"
});
</script>
</head>

<body>

   <rhn:require acl="user_role(satellite_admin)"/>

   <div>
     <form action="/rhn/admin/Catalina.do">
       <rhn:csrf />
       <table class="details">
         <tr>
           <th>
             <bean:message key="catalina.jsp.show"/>
           </th>
           <td>
               <textarea name="contents" rows="24" cols="80" id="contents">${contents}</textarea>
           </td>
         </tr>
       </table>
       <rhn:submitted/>
     </form>
   </div>
 </body>
</html>
