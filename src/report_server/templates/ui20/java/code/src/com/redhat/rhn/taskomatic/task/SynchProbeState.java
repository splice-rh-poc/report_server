/**
 * Copyright (c) 2009--2011 Red Hat, Inc.
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
package com.redhat.rhn.taskomatic.task;

import com.redhat.rhn.common.db.datasource.CallableMode;
import com.redhat.rhn.common.db.datasource.ModeFactory;

import org.quartz.JobExecutionContext;
import org.quartz.JobExecutionException;

import java.util.Collections;
import java.util.HashMap;

/**
 * Calls the synch probe state proc on a regular basis from Taskomatic
 *
 * @version $Rev $
 */

public class SynchProbeState extends RhnJavaJob {

    /**
     * {@inheritDoc}
     */
    public void execute(JobExecutionContext context)  throws JobExecutionException {
        try {
            if (log.isDebugEnabled()) {
                log.debug("Starting probe state sync");
            }
            CallableMode proc = ModeFactory.getCallableMode(TaskConstants.MODE_NAME,
                    TaskConstants.TASK_QUERY_SYNCHPROBESTATE_PROC);
            proc.execute(Collections.EMPTY_MAP, new HashMap());
            if (log.isDebugEnabled()) {
                log.debug("Probe state sync completed");
            }
        }
        catch (Exception e) {
            log.error("Error during probe state sync", e);
            throw new JobExecutionException(e);
        }
    }

}
