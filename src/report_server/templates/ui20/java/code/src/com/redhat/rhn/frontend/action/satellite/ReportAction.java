/**
 * Copyright (c) 2009--2012 Red Hat, Inc.
 *
 * This software is licensed to you under the GNU General Public License,
 * version 2 (GPLv2). There is NO WARRANTY for this software, express or
 * implied, including the implied warranties of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
 * along with this software; if not, see
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
 *
 * Red Hat trademarks are not licensed under GPLv2. No permission is
 * granted to use or replicate Red Hat trademarks that are incorporated
 * in this software or its documentation.
 */

package com.redhat.rhn.frontend.action.satellite;

import com.redhat.rhn.common.util.FileUtils;
import com.redhat.rhn.frontend.struts.RequestContext;
import com.redhat.rhn.frontend.struts.RhnAction;
import com.redhat.rhn.frontend.struts.RhnHelper;

import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.net.*;
import java.io.*;


/**
 * @author coec
 * @version $Rev$
 */
public class ReportAction extends RhnAction {
   /** {@inheritDoc} */

   public ActionForward execute(ActionMapping mapping,
                                ActionForm formIn,
                                HttpServletRequest request,
                                HttpServletResponse response) {
       RequestContext ctx = new RequestContext(request);
     
       String spacewalk_external_hostname = "";
       try {	
           URL url = new URL("http://instance-data.ec2.internal/latest/meta-data/public-hostname");
           URLConnection url_con = url.openConnection();
           BufferedReader in = new BufferedReader(new InputStreamReader(url_con.getInputStream()));
           spacewalk_external_hostname = in.readLine();
           in.close();
	
	} catch (IOException ioe) {
           //need to figure out how to raise an exception in spacewalk
           System.out.println(ioe);

       } 


       request.setAttribute("contents", spacewalk_external_hostname);
             

       return mapping.findForward(RhnHelper.DEFAULT_FORWARD);
   }
}
