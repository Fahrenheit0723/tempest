# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
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

from tempest.api.compute.security_groups import base
from tempest.lib import decorators


class SecurityGroupRulesTestJSON(base.BaseSecurityGroupsTest):
    """Test security group rules API

    Test security group rules API with compute microversion less than 2.36.
    """

    @classmethod
    def setup_clients(cls):
        super(SecurityGroupRulesTestJSON, cls).setup_clients()
        cls.client = cls.security_group_rules_client

    @classmethod
    def resource_setup(cls):
        super(SecurityGroupRulesTestJSON, cls).resource_setup()
        cls.ip_protocol = 'tcp'
        cls.from_port = 22
        cls.to_port = 22

    def setUp(self):
        super(SecurityGroupRulesTestJSON, self).setUp()

        from_port = self.from_port
        to_port = self.to_port
        group = {}
        ip_range = {}
        self.expected = {
            'parent_group_id': None,
            'ip_protocol': self.ip_protocol,
            'from_port': from_port,
            'to_port': to_port,
            'ip_range': ip_range,
            'group': group
        }

    def _check_expected_response(self, actual_rule):
        for key in self.expected:
            self.assertEqual(self.expected[key], actual_rule[key],
                             "Miss-matched key is %s" % key)


    @decorators.idempotent_id('850795d7-d4d3-4e55-b527-a774c0123d3a')
    def test_security_group_rules_create(self):
        """Test creating security group rules"""
        # Creating a Security Group to add rules to it
        security_group = self.create_security_group()
        securitygroup_id = security_group['id']
        # Adding rules to the created Security Group
        rule = self.client.create_security_group_rule(
            parent_group_id=securitygroup_id,
            ip_protocol=self.ip_protocol,
            from_port=self.from_port,
            to_port=self.to_port)['security_group_rule']
        self.expected['parent_group_id'] = securitygroup_id
        self.expected['ip_range'] = {'cidr': '0.0.0.0/0'}
        self._check_expected_response(rule)

    @decorators.idempotent_id('7a01873e-3c38-4f30-80be-31a043cfe2fd')
    def test_security_group_rules_create_with_optional_cidr(self):
        """Test creating security group rules with optional field cidr"""
        # Creating a Security Group to add rules to it
        security_group = self.create_security_group()
        parent_group_id = security_group['id']

        # Adding rules to the created Security Group with optional cidr
        cidr = '10.2.3.124/24'
        rule = self.client.create_security_group_rule(
            parent_group_id=parent_group_id,
            ip_protocol=self.ip_protocol,
            from_port=self.from_port,
            to_port=self.to_port,
            cidr=cidr)['security_group_rule']
        self.expected['parent_group_id'] = parent_group_id
        self.expected['ip_range'] = {'cidr': cidr}
        self._check_expected_response(rule)

    @decorators.idempotent_id('7f5d2899-7705-4d4b-8458-4505188ffab6')
    def test_security_group_rules_create_with_optional_group_id(self):
        """Test creating security group rules with optional field group id"""
        # Creating a Security Group to add rules to it
        security_group = self.create_security_group()
        parent_group_id = security_group['id']

        # Creating a Security Group so as to assign group_id to the rule
        security_group = self.create_security_group()
        group_id = security_group['id']
        group_name = security_group['name']

        # Adding rules to the created Security Group with optional group_id
        rule = self.client.create_security_group_rule(
            parent_group_id=parent_group_id,
            ip_protocol=self.ip_protocol,
            from_port=self.from_port,
            to_port=self.to_port,
            group_id=group_id)['security_group_rule']
        self.expected['parent_group_id'] = parent_group_id
        self.expected['group'] = {'tenant_id': self.client.tenant_id,
                                  'name': group_name}
        self._check_expected_response(rule)


    @decorators.idempotent_id('a6154130-5a55-4850-8be4-5e9e796dbf17')
    def test_security_group_rules_list(self):
        """Test listing security group rules"""
        # Creating a Security Group to add rules to it
        security_group = self.create_security_group()
        securitygroup_id = security_group['id']

        # Add a first rule to the created Security Group
        rule = self.client.create_security_group_rule(
            parent_group_id=securitygroup_id,
            ip_protocol=self.ip_protocol,
            from_port=self.from_port,
            to_port=self.to_port)['security_group_rule']
        rule1_id = rule['id']

        # Add a second rule to the created Security Group
        ip_protocol2 = 'icmp'
        from_port2 = -1
        to_port2 = -1
        rule = self.client.create_security_group_rule(
            parent_group_id=securitygroup_id,
            ip_protocol=ip_protocol2,
            from_port=from_port2,
            to_port=to_port2)['security_group_rule']
        rule2_id = rule['id']
        # Delete the Security Group rule2 at the end of this method
        self.addCleanup(
            self.security_group_rules_client.delete_security_group_rule,
            rule2_id)

        # Get rules of the created Security Group
        rules = self.security_groups_client.show_security_group(
            securitygroup_id)['security_group']['rules']
        self.assertNotEmpty([i for i in rules if i['id'] == rule1_id])
        self.assertNotEmpty([i for i in rules if i['id'] == rule2_id])

    @decorators.idempotent_id('fc5c5acf-2091-43a6-a6ae-e42760e9ffaf')
    def test_security_group_rules_delete_when_peer_group_deleted(self):
        """Test security group rule gets deleted when peer group is deleted"""
        # Creating a Security Group to add rules to it
        security_group = self.create_security_group()
        sg1_id = security_group['id']
        # Creating other Security Group to access to group1
        security_group = self.create_security_group()
        sg2_id = security_group['id']
        # Adding rules to the Group1
        self.client.create_security_group_rule(
            parent_group_id=sg1_id,
            ip_protocol=self.ip_protocol,
            from_port=self.from_port,
            to_port=self.to_port,
            group_id=sg2_id)

        # Delete group2
        self.security_groups_client.delete_security_group(sg2_id)
        # Get rules of the Group1
        rules = (self.security_groups_client.show_security_group(sg1_id)
                 ['security_group']['rules'])
        # The group1 has no rules because group2 has deleted
        self.assertEmpty(rules)
