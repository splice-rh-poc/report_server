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
package com.redhat.rhn.frontend.action.errata.test;

import com.redhat.rhn.domain.errata.Errata;
import com.redhat.rhn.domain.errata.test.ErrataFactoryTest;
import com.redhat.rhn.frontend.action.errata.ListPackagesSetupAction;
import com.redhat.rhn.frontend.struts.RequestContext;
import com.redhat.rhn.frontend.struts.RhnAction;
import com.redhat.rhn.testing.ActionHelper;
import com.redhat.rhn.testing.RhnBaseTestCase;

/**
 * ListPackagesSetupActionTest
 * @version $Rev$
 */
public class ListPackagesSetupActionTest extends RhnBaseTestCase {

    public void testExecute() throws Exception {
        ListPackagesSetupAction action = new ListPackagesSetupAction();
        ActionHelper sah = new ActionHelper();

        sah.setUpAction(action);
        sah.setupClampListBounds();

        //Create a new errata
        Errata e = ErrataFactoryTest.createTestPublishedErrata(
                sah.getUser().getOrg().getId());
        sah.getRequest().setupAddParameter("eid", e.getId().toString());
        sah.getRequest().setupAddParameter("eid", e.getId().toString());
        sah.getRequest().setupAddParameter("view_channel", (String) null);
        sah.getRequest().setupAddParameter(RhnAction.SUBMITTED, Boolean.TRUE.toString());
        sah.executeAction();

        //make sure we got something for page list
        assertNotNull(sah.getRequest().getAttribute(RequestContext.PAGE_LIST));
    }
}
