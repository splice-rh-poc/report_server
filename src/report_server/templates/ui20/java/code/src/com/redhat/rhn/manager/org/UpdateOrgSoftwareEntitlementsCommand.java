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
package com.redhat.rhn.manager.org;

import com.redhat.rhn.common.conf.ConfigDefaults;
import com.redhat.rhn.common.db.datasource.CallableMode;
import com.redhat.rhn.common.db.datasource.ModeFactory;
import com.redhat.rhn.common.validator.ValidatorError;
import com.redhat.rhn.domain.channel.ChannelFamily;
import com.redhat.rhn.domain.channel.ChannelFamilyFactory;
import com.redhat.rhn.domain.org.Org;
import com.redhat.rhn.domain.org.OrgFactory;

import java.util.HashMap;
import java.util.Map;


/**
 * UpdateOrgSystemEntitlements - This Command updates the total number of entitlements
 * in the Org passed in to the proposed new total.  It will either grab entitlements from
 * the default org or give them back if its a decreace from the previous value.
 * @version $Rev$
 */
public class UpdateOrgSoftwareEntitlementsCommand {

    private Org org;
    private Long newTotal;
    private Long newFlexTotal;
    private ChannelFamily channelFamily;

    /**
     * Constructor
     * @param channelFamilyLabel label of entitlement to update
     * @param orgIn to update totals for
     * @param newTotalIn This is the *proposed* new total for the org you are passing in.
     * @param newFlexTotalIn This is the *proposed* new flex total
     *                                               for the org you are passing in.
     */
    public UpdateOrgSoftwareEntitlementsCommand(String channelFamilyLabel,
            Org orgIn, Long newTotalIn, Long newFlexTotalIn) {
        if (orgIn.getId().equals(OrgFactory.getSatelliteOrg().getId())) {
            throw new IllegalArgumentException("Cant update the default org");
        }
        this.org = orgIn;
        this.channelFamily = ChannelFamilyFactory.lookupByLabel(channelFamilyLabel,
                OrgFactory.getSatelliteOrg());
        if (this.channelFamily == null) {
            throw new IllegalArgumentException("ChannelFamily not found: [" +
                    channelFamilyLabel + "]");
        }
        // if set to null, keep currently used value
        if (newTotalIn == null) {
            this.newTotal = this.channelFamily.getMaxMembers(org);
        }
        else {
            this.newTotal = newTotalIn;
        }
        if (newFlexTotalIn == null) {
            this.newFlexTotal = this.channelFamily.getMaxFlex(org);
        }
        else {
            this.newFlexTotal = newFlexTotalIn;
        }
    }

    /**
     *
     * @return if we should force unentitlement if
     * current members is greater then proposed entitlement count
     */
    private boolean forceUnentitlement(Long orgCur, Long orgProposedMax) {
        boolean retval = true;
        if (orgCur == null) {
            orgCur = 0L;
        }

        if (orgCur > orgProposedMax && !ConfigDefaults.get().forceUnentitlement()) {
            retval = false;
        }
        return retval;
    }

    /**
     * Update the entitlements in the DB.
     * @return ValidatorError if there were any problems with the proposed total
     */
    public ValidatorError store() {
        ValidatorError err = null;
        err = storeRegular();
        if (err == null) {
            return storeFlex();
        }
        return err;
    }

    private ValidatorError storeRegular() {
        // Check available entitlements
        Org satOrg = OrgFactory.getSatelliteOrg();
        return store(channelFamily.getMaxMembers(satOrg),
                        channelFamily.getMaxMembers(org),
                        channelFamily.getCurrentMembers(satOrg),
                        channelFamily.getCurrentMembers(org),
                        newTotal, false);
    }

    private ValidatorError storeFlex() {
        // Check available entitlements
        Org satOrg = OrgFactory.getSatelliteOrg();
        return store(channelFamily.getMaxFlex(satOrg),
                        channelFamily.getMaxFlex(org),
                        channelFamily.getCurrentFlex(satOrg),
                        channelFamily.getCurrentFlex(org),
                        newFlexTotal, true);
    }

    private  ValidatorError store(Long satMax, Long orgMax,
                                                Long satCurrent, Long orgCurrent,
                                                Long proposed, boolean isFlex) {
        if (orgMax == null) {
            orgMax = 0L;
        }
        // No sense making the call if its the same.
        if (proposed == null || proposed.compareTo(orgMax) == 0) {
            return null;
        }

        Long avail = 0L;
        if (satMax != null) {
            avail = satMax - satCurrent + orgMax;
        }

        if (proposed < 0 || avail < proposed) {
            String key = isFlex ? "org.entitlements.software.not_in_range.flex" :
                            "org.entitlements.software.not_in_range";

            return new ValidatorError(key, this.org.getName(),
                            this.channelFamily.getName(), 0, avail);
        }

        // Proposed cannot be lower than current members
        if (!forceUnentitlement(orgCurrent, proposed)) {
           return new ValidatorError(
                   "org.entitlements.software.proposedwarning",
                   this.channelFamily.getName(),
                   this.org.getName()
                   );
        }


        Long toOrgId;
        Long fromOrgId;
        long actualDiff;
        // If we are decreasing the # of entitlements
        // we give back to the default org.
        if (orgMax.longValue() > proposed) {
            fromOrgId = this.org.getId();
            toOrgId = OrgFactory.getSatelliteOrg().getId();
            actualDiff = orgMax.longValue() - proposed;
        }
        else {
            toOrgId = this.org.getId();
            fromOrgId = OrgFactory.getSatelliteOrg().getId();
            actualDiff = proposed - orgMax.longValue();
        }

        Map in = new HashMap();
        // "group_label, from_org_id, to_org_id, quantity"
        in.put("channel_family_label", channelFamily.getLabel());
        in.put("from_org_id", fromOrgId);
        in.put("to_org_id", toOrgId);
        if (isFlex) {
            in.put("quantity", 0);
            in.put("flex_quantity", actualDiff);

        }
        else {
            in.put("quantity", actualDiff);
            in.put("flex_quantity", 0);

        }
        CallableMode m = ModeFactory.getCallableMode(
                "Org_queries", "assign_software_entitlements");
        m.execute(in, new HashMap());
        return null;
    }
}
