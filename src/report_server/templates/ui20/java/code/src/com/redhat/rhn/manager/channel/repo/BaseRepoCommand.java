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
package com.redhat.rhn.manager.channel.repo;

import com.redhat.rhn.domain.channel.ChannelFactory;
import com.redhat.rhn.domain.channel.ContentSource;
import com.redhat.rhn.domain.org.Org;
import com.redhat.rhn.frontend.xmlrpc.channel.repo.InvalidRepoLabelException;
import com.redhat.rhn.frontend.xmlrpc.channel.repo.InvalidRepoUrlException;

/**
 * CreateRepoCommand - Command to create a repo
 * @version $Rev: 119601 $
 */
public class BaseRepoCommand {

    protected ContentSource repo;

    private String label;
    private String url;
    private Org org;
    /**
     * Constructor
     */
    BaseRepoCommand() {
    }

    /**
     *
     * @return Org of repo
     */
    public Org getOrg() {
        return org;
    }

    /**
     *
     * @param orgIn to set for repo
     */
    public void setOrg(Org orgIn) {
        this.org = orgIn;
    }

    /**
     *
     * @return label for repo
     */
    public String getLabel() {
        return label;
    }

    /**
     *
     * @param labelIn to set for repo
     */
    public void setLabel(String labelIn) {
        this.label = labelIn;
    }

    /**
     *
     * @return url for repo
     */
    public String getUrl() {
        return url;
    }

    /**
     *
     * @param urlIn to set for repo
     */
    public void setUrl(String urlIn) {
        this.url = urlIn;
    }

    /**
     * Check for errors and store Org to db.
     * @throws InvalidRepoUrlException in case repo wih given url already exists
     * in the org
     * @throws InvalidRepoLabelException in case repo witch given label already exists
     * in the org
     */
    public void store() throws InvalidRepoUrlException, InvalidRepoLabelException {
        repo.setOrg(org);
        repo.setType(ChannelFactory.CONTENT_SOURCE_TYPE_YUM);

        if (!this.label.equals(repo.getLabel())) {
            if (ChannelFactory.lookupContentSourceByOrgAndLabel(org, label) != null) {
                throw new InvalidRepoLabelException(label);
            }
            repo.setLabel(this.label);
        }

        if (!this.url.equals(repo.getSourceUrl())) {
            if (!ChannelFactory.lookupContentSourceByOrgAndRepo(org,
                    ChannelFactory.CONTENT_SOURCE_TYPE_YUM, url).isEmpty()) {
                throw new InvalidRepoUrlException(url);
            }
            repo.setSourceUrl(this.url);
        }

        ChannelFactory.save(repo);
    }

    /**
     * Get the repo
     * @return repo
     */
    public ContentSource getRepo() {
        return this.repo;
    }
}
