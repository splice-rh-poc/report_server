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
package com.redhat.rhn.manager.system;

import com.redhat.rhn.common.db.WrappedSQLException;
import com.redhat.rhn.common.db.datasource.CallableMode;
import com.redhat.rhn.common.db.datasource.ModeFactory;
import com.redhat.rhn.common.hibernate.HibernateFactory;
import com.redhat.rhn.domain.org.Org;
import com.redhat.rhn.domain.server.ServerFactory;
import com.redhat.rhn.domain.server.VirtualInstanceFactory;
import com.redhat.rhn.domain.user.User;
import com.redhat.rhn.frontend.dto.ChannelFamilySystemGroup;

import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;


/**
 * VirtualizationEntitlementsService
 * @version $Rev$
 */
public class VirtualizationEntitlementsManager {
    private static final VirtualizationEntitlementsManager INSTANCE =
        new VirtualizationEntitlementsManager();
    /**
     * Initializes the manager.
     */
    private VirtualizationEntitlementsManager() {
    }

    /**
     * @return an instance
     */
    public static VirtualizationEntitlementsManager getInstance() {
        return INSTANCE;
    }

    /**
     * Queries an org for host systems, having the 'Unlimited Virtualization' entitlement,
     * and the guest count for each host.
     *
     * @param org The org to search in
     *
     * @return A set of HostAndGuestView objects
     *
     * @see com.redhat.rhn.domain.server.HostAndGuestCountView
     */
    public List findGuestUnlimitedHostsByOrg(Org org) {
        return ServerFactory.findVirtPlatformHostsByOrg(org);
    }

    /**
     * Queries an org for host systems, having the 'Limited Virtualization' entitlement that
     * have exceeded their guest limit. The guest count for each host is also fetched.
     *
     * @param org The org to search in
     *
     * @return A set of HostAndGuestView objects
     *
     * @see com.redhat.rhn.domain.server.HostAndGuestCountView
     */
    public List findGuestLimitedHostsByOrg(Org org) {
        return ServerFactory.findVirtHostsExceedingGuestLimitByOrg(org);
    }

    /**
     * Queries an org for guest systems whose hosts either do not have any virtualization
     * entitlements or are not registered with RHN.
     *
     * @param org The org to search in
     *
     * @return A set of GuestAndNonVirtHostView objects
     *
     * @see com.redhat.rhn.domain.server.GuestAndNonVirtHostView
     */
    public List findGuestsWithoutHostsByOrg(Org org) {
        List guestsWithoutHosts = new LinkedList();
        guestsWithoutHosts.addAll(VirtualInstanceFactory.getInstance().
                findGuestsWithNonVirtHostByOrg(org));
        guestsWithoutHosts.addAll(VirtualInstanceFactory.getInstance().
                findGuestsWithoutAHostByOrg(org));

        return guestsWithoutHosts;
    }

    /**
     * Returns a list of guests using FVE
     * @param user user for access checks
     * @return a list of ChannelFamilySystemGroup
     */
    public List<ChannelFamilySystemGroup> listFlexGuests(User user) {
        return VirtualInstanceFactory.getInstance().listFlexGuests(user);

    }


    /**
     * Returns a list of eligible guest systems that could be moved to FVE bucket
     * @param user user for access checks
     * @return a list of ChannelFamilySystemGroup
     */
    public List<ChannelFamilySystemGroup> listEligibleFlexGuests(User user) {
        return VirtualInstanceFactory.getInstance().listEligibleFlexGuests(user);

    }

    /**
     * Converts a given server to flex entitlement
     * @param systemId the server id
     * @param channelFamilyId the channel family id
     * @param user the user object
     */
    private void convertToFlex(Long systemId,
            Long channelFamilyId,
            User user) {
        SystemManager.ensureAvailableToUser(user, systemId);
        Map in = new HashMap();
        in.put("sid", systemId);
        in.put("cfid", channelFamilyId);
        CallableMode m = ModeFactory.getCallableMode(
                "Channel_queries", "convert_to_flex");
        m.execute(in, new HashMap());
    }

    /**
     * Converts a a given list of servers to Flex.
     * The conversion is stopped if "not_enough_slots"
     * message shows up from the stored procedure.
     * The return value shows how many systems successfully converted to flex
     * @param systemIds list of system ids
     * @param channelFamilyId the channel family id
     * @param user the user
     * @return the number of successful converts
     */
    public Set<Long> convertToFlex(List<Long> systemIds,
            Long channelFamilyId,
            User user) {
        Set<Long> toRet = new HashSet<Long>();
        for (Long sid : systemIds) {
            try {
                convertToFlex(sid, channelFamilyId, user);
                toRet.add(sid);
            }
            catch (WrappedSQLException sq) {
                String msg = sq.getMessage();
                if (msg != null) {
                    if (msg.contains("not_enough_flex_entitlements") ||
                    msg.contains("server_cannot_convert_to_flex")) {
                        // PG does not like reusing connections that
                        // already signalled a Connection error
                        HibernateFactory.closeSession();
                        continue;
                    }
                }
                throw sq;
            }
        }
        return toRet;

    }
}
