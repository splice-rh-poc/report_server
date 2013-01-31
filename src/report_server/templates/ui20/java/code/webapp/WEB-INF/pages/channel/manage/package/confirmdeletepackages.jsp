<%@ taglib uri="http://rhn.redhat.com/rhn" prefix="rhn" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>
<%@ taglib uri="http://rhn.redhat.com/tags/list" prefix="rl" %>

<html:xhtml/>
<html>
<head>
    <meta name="page-decorator" content="none" />
</head>
<body>

<rhn:toolbar base="h1" img="/img/rhn-icon-packages.gif" imgAlt="overview.jsp.alt"
 helpUrl="/rhn/help/channel-mgmt/en-US/channel-mgmt-Custom_Channel_and_Package_Management-Manage_Software_Packages.jsp">
   <bean:message key="channel.jsp.manage.package.title"/>
</rhn:toolbar>


<h2><bean:message key="channel.jsp.manage.package.subtitle"/></h2>
<bean:message key="channel.jsp.manage.package.remove.message"/>




<rl:listset name="packageSet" legend="system-group">
<rhn:csrf />

<input type="hidden" name="cid" value="${cid}" />

	<rl:list dataset="pageList"
			name="packageList"
			emptykey="package.jsp.emptylistselected"
			alphabarcolumn="nvrea"
			filter="com.redhat.rhn.frontend.taglibs.list.filters.PackageFilter" >


			 <rl:decorator name="ElaborationDecorator"/>

			<rl:decorator name="PageSizeDecorator"/>


                 <rl:column sortable="true"
                                   bound="false"
                           headerkey="download.jsp.package"
                           sortattr="nvrea"
					defaultsort="asc"
					styleclass="first-column"
                           >

                        <a href="/rhn/software/packages/Details.do?pid=${current.id}">${current.nvrea}</a>
                </rl:column>



                 <rl:column sortable="false"
                                   bound="false"
                           headerkey="channel.jsp.manage.package.channels"
                          >
                          <c:if test="${empty current.packageChannels}">
				(<bean:message key="channel.jsp.manage.package.none"/>)
                          </c:if>

                          <c:forEach var="channel" items="${current.packageChannels}">
				${channel}
				<BR>
                          </c:forEach>

                </rl:column>

                 <rl:column sortable="false"
                                   bound="false"
                           headerkey="package.jsp.provider"
                           styleclass="last-column"
                          >
                        ${current.provider}
                </rl:column>

	</rl:list>
	<rl:csv dataset="pageList"
		        name="packageList"
		        exportColumns="id, nvrea, summary, provider" />
	<div align="right">
	  <hr />
		<input type="submit" name="confirm" value="<bean:message key="channel.jsp.manage.package.delete"/>" />
	</div>
		<rhn:submitted/>


</rl:listset>

</body>
</html>
