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
  <%
  Cookie[] cookies = request.getCookies();
  if(cookies != null){
     for(int i = 0; i < cookies .length;i++){
            Cookie c = cookies [i];
            //out.println(c.getName());
            if (c.getName().equals ("pxt-session-cookie")){
                Cookie report_session = new Cookie ("report-session", c.getValue());
                report_session.setPath("/");
                response.addCookie(report_session);

            }
      }
                                                                            
   }

   %>


   <form id="report_pop">
    <input type="button" value="Open Red Hat Reports" onClick="window.open ('https://${contents}/report-server/ui20/','window','width=800,height=800')"></form>

 </body>
</html>
