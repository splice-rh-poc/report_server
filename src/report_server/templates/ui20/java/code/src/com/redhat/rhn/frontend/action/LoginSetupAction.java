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
package com.redhat.rhn.frontend.action;

import com.redhat.rhn.common.db.datasource.DataResult;
import com.redhat.rhn.common.db.datasource.ModeFactory;
import com.redhat.rhn.common.db.datasource.SelectMode;
import com.redhat.rhn.frontend.struts.RhnAction;
import com.redhat.rhn.frontend.struts.RhnHelper;
import com.redhat.rhn.manager.acl.AclManager;
import com.redhat.rhn.manager.satellite.CertificateManager;
import com.redhat.rhn.manager.satellite.SystemCommandExecutor;
import com.redhat.rhn.manager.user.UserManager;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.DynaActionForm;

import java.util.HashMap;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * LoginSetupAction
 * @version $Rev$
 */
public class LoginSetupAction extends RhnAction {

    private static Logger log = Logger.getLogger(LoginSetupAction.class);
    public static final String HAS_EXPIRED = "hasExpired";

    /** {@inheritDoc} */
    public ActionForward execute(ActionMapping mapping,
        ActionForm form, HttpServletRequest request,
        HttpServletResponse response) {

        String rpmSchemaVersion = getRpmSchemaVersion("satellite-schema");
        if (rpmSchemaVersion == null) {
            rpmSchemaVersion = getRpmSchemaVersion("spacewalk-schema");
        }

        SelectMode m = ModeFactory.getMode("General_queries", "installed_schema_version");
        DataResult<HashMap> dr = m.execute();
        String installedSchemaVersion = null;
        if (dr.size() > 0) {
            installedSchemaVersion = (String) dr.get(0).get("version");
        }

        if (log.isDebugEnabled()) {
            log.debug("RPM version of schema: " +
                (rpmSchemaVersion == null ? "null" : rpmSchemaVersion));
            log.debug("Version of installed database schema: " +
                (installedSchemaVersion == null ? "null" : installedSchemaVersion));
        }

        if (rpmSchemaVersion != null && installedSchemaVersion != null &&
            !rpmSchemaVersion.equals(installedSchemaVersion)) {
            request.setAttribute("schemaUpgradeRequired", "true");
        }
        else {
            request.setAttribute("schemaUpgradeRequired", "false");
        }

        CertificateManager man = CertificateManager.getInstance();
        if (man.isSatelliteCertExpired()) {
            addMessage(request, "satellite.expired");
            request.setAttribute(HAS_EXPIRED, Boolean.TRUE);
            return mapping.findForward(RhnHelper.DEFAULT_FORWARD);
        }
        else if (man.isSatelliteCertInGracePeriod()) {
            long daysUntilExpiration = man.getDaysLeftBeforeCertExpiration();
            createSuccessMessage(request,
                "satellite.graceperiod",
                String.valueOf(daysUntilExpiration));
        }
        else if (!UserManager.satelliteHasUsers()) {
            return mapping.findForward("needuser");
        }

        if (AclManager.hasAcl("user_authenticated()", request, null)) {
            return mapping.findForward("loggedin");
        }

        // ok handle the case where we're doing the ReLogin page
        String urlBounce = (String) request.getAttribute("url_bounce");
        String requestMethod = (String) request.getAttribute("request_method");

        if (!StringUtils.isEmpty(urlBounce)) {

            if (log.isDebugEnabled()) {
                log.debug("request.getAttribute(url_bounce): " + urlBounce);
            }

            DynaActionForm f = (DynaActionForm)form;
            f.set("url_bounce", urlBounce);
        }

        if (!StringUtils.isEmpty(requestMethod)) {

            if (log.isDebugEnabled()) {
                log.debug("request.getAttribute(request_method): " + requestMethod);
            }

            DynaActionForm f = (DynaActionForm)form;
            f.set("request_method", requestMethod);
        }

        return mapping.findForward(RhnHelper.DEFAULT_FORWARD);
    }

    private String getRpmSchemaVersion(String schemaName) {
        String[] rpmCommand = new String[4];
        rpmCommand[0] = "rpm";
        rpmCommand[1] = "-q";
        rpmCommand[2] = "--qf=%{VERSION}-%{RELEASE}";
        rpmCommand[3] = schemaName;
        SystemCommandExecutor ce = new SystemCommandExecutor();
        return ce.execute(rpmCommand) == 0 ?
            ce.getLastCommandOutput().replace("\n", "") : null;
    }
}
