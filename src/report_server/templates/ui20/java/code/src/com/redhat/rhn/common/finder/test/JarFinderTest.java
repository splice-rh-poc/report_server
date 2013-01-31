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

package com.redhat.rhn.common.finder.test;
import com.redhat.rhn.common.finder.Finder;
import com.redhat.rhn.common.finder.FinderFactory;
import com.redhat.rhn.testing.RhnBaseTestCase;

import java.util.List;

public class JarFinderTest extends RhnBaseTestCase {

    public void testGetFinder() throws Exception {
        Finder f = FinderFactory.getFinder("redstone.xmlrpc");
        assertNotNull(f);
    }

    public void testFindFiles() throws Exception {
        Finder f = FinderFactory.getFinder("redstone.xmlrpc");
        assertNotNull(f);

        List result = f.find(".class");
        assertEquals(28, result.size());
    }

    public void testFindFilesSubDir() throws Exception {
        Finder f = FinderFactory.getFinder("redstone.xmlrpc");
        assertNotNull(f);

        List result = f.find("");
        assertEquals(29, result.size());
    }

    public void testFindFilesExcluding() throws Exception {
        Finder f = FinderFactory.getFinder("redstone.xmlrpc");
        assertNotNull(f);

        String[] sarr = {"End"};

        List result = f.findExcluding(sarr, "class");
        assertEquals(28, result.size());
    }
}


