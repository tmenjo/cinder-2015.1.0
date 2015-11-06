# Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Tests for finish_volume_migration."""


from cinder import context
from cinder import db
from cinder import objects
from cinder import test
from cinder.tests import utils as testutils


class FinishVolumeMigrationTestCase(test.TestCase):
    """Test cases for finish_volume_migration."""

    def test_finish_volume_migration(self):
        ctxt = context.RequestContext(user_id='user_id',
                                      project_id='project_id',
                                      is_admin=True)
        src_volume = testutils.create_volume(ctxt, host='src',
                                             migration_status='migrating',
                                             status='available')
        dest_volume = testutils.create_volume(ctxt, host='dest',
                                              migration_status='target:fake',
                                              status='available')
        db.finish_volume_migration(ctxt, src_volume['id'], dest_volume['id'])

        # Check that we have copied destination volume DB data into source DB
        # entry so we can keep the id
        src_volume = objects.Volume.get_by_id(ctxt, src_volume['id'])
        self.assertEqual('dest', src_volume.host)
        self.assertEqual('available', src_volume.status)
        self.assertIsNone(src_volume.migration_status)

        # Check that we have copied source volume DB data into destination DB
        # entry and we are setting it to deleting
        dest_volume = objects.Volume.get_by_id(ctxt, dest_volume['id'])
        self.assertEqual('src', dest_volume.host)
        self.assertEqual('deleting', dest_volume.status)
        self.assertEqual('deleting', dest_volume.migration_status)
