/**
 * Copyright (c) 2009--2010 Red Hat, Inc.
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
package com.redhat.rhn.frontend.action.kickstart;

import com.redhat.rhn.common.db.datasource.DataResult;
import com.redhat.rhn.domain.kickstart.KickstartData;
import com.redhat.rhn.domain.kickstart.KickstartFactory;
import com.redhat.rhn.domain.org.Org;
import com.redhat.rhn.frontend.listview.PageControl;
import com.redhat.rhn.frontend.struts.BaseListAction;
import com.redhat.rhn.frontend.struts.RequestContext;
import com.redhat.rhn.manager.kickstart.KickstartLister;

/**
 * KickstartsSetupAction.
 * @version $Rev: 1 $
 */
public class ScriptsSetupAction extends BaseListAction {

    /**
     *
     * {@inheritDoc}
     */
    protected DataResult getDataResult(RequestContext rctx, PageControl pc) {
        Long ksid = rctx.getRequiredParam(RequestContext.KICKSTART_ID);
        Org org = rctx.getCurrentUser().getOrg();
        return KickstartLister.getInstance().scriptsInKickstart(org, ksid, pc);
    }

    /**
     *
     * {@inheritDoc}
     */
    protected void processRequestAttributes(RequestContext rctx) {
        super.processRequestAttributes(rctx);

        KickstartData ksdata = KickstartFactory
            .lookupKickstartDataByIdAndOrg(rctx.getCurrentUser().getOrg(),
                    rctx.getRequiredParam(RequestContext.KICKSTART_ID));
        rctx.getRequest().setAttribute(RequestContext.KICKSTART, ksdata);
    }

}
