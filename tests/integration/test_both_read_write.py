"""Both tools enabled, read-write, static credentials.

`blocked_commands` is the default list minus `cluster-info`, so the
successful `cluster-info` call proves the override reaches the server.
Writes use uuid-suffixed names and are cleaned up through the MCP tools
themselves, which doubles as a delete-write test.
"""

from uuid import uuid4

from tests.integration.mcp_container import (
    OPENSHIFT_PATH,
    OPENSTACK_PATH,
    McpIntegrationTest,
    default_blocked_commands_without,
)


class BothReadWriteTests(McpIntegrationTest):
    openstack_enabled = True
    openshift_enabled = True
    openstack_allow_write = True
    openshift_allow_write = True
    openshift_blocked_commands = default_blocked_commands_without("cluster-info")
    static_creds = True

    async def test_volume_create_with_and_without_prefix(self):
        name = f"itest-{uuid4().hex[:8]}"
        with_prefix = await self.call_tool(
            OPENSTACK_PATH, f"openstack volume create --size 1 {name}-1"
        )
        without_prefix = await self.call_tool(
            OPENSTACK_PATH, f"volume create --size 1 {name}-2"
        )
        self.assertIn(f"{name}-1", with_prefix)
        self.assertIn(f"{name}-2", without_prefix)
        # Cleanup through the MCP tool itself, doubling as a delete test
        await self.call_tool(OPENSTACK_PATH, f"volume delete {name}-1")
        await self.call_tool(OPENSTACK_PATH, f"volume delete {name}-2")

    async def test_namespace_create_and_delete(self):
        name = f"itest-{uuid4().hex[:8]}"
        output = await self.call_tool(OPENSHIFT_PATH, f"create namespace {name}")
        self.assertIn(name, output)
        output = await self.call_tool(OPENSHIFT_PATH, f"delete namespace {name}")
        self.assertIn(name, output)

    async def test_cluster_info_is_allowed_by_the_override(self):
        output = await self.call_tool(OPENSHIFT_PATH, "cluster-info")
        self.assertIn("Kubernetes control plane", output)

    async def test_still_blocked_commands_are_rejected(self):
        await self.assert_tool_error(OPENSHIFT_PATH, "config view")

    async def test_forbidden_arguments_are_still_rejected(self):
        await self.assert_tool_error(
            OPENSTACK_PATH, "project list --os-token some-token"
        )
        await self.assert_tool_error(
            OPENSHIFT_PATH, "get pod -n openstack --token some-token"
        )

    async def test_pipes_still_fail(self):
        await self.assert_tool_error(OPENSTACK_PATH, "project list | grep admin")
        await self.assert_tool_error(OPENSHIFT_PATH, "get pod -n openstack | grep nova")
