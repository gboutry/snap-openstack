# SPDX-FileCopyrightText: 2024 - Canonical Ltd
# SPDX-License-Identifier: Apache-2.0

"""Type definitions for cluster API responses."""

from typing import TypedDict


class Node(TypedDict):
    """Represents a node in the cluster."""

    name: str
    role: list[str]
    machineid: int
    systemid: str


class JujuUser(TypedDict):
    """Represents a Juju user."""

    username: str
    token: str


class TerraformLock(TypedDict):
    """Represents a Terraform lock (based on Terraform's lock file format)."""

    ID: str
    Operation: str
    Info: str
    Who: str
    Version: str
    Created: str
    Path: str


class Manifest(TypedDict):
    """Represents a manifest entry."""

    manifestid: str
    data: str
    applied_date: str | None


class CertPair(TypedDict):
    """Represents a certificate pair."""

    certificate: str
    private_key: str


class MemberStatus(TypedDict):
    """Represents the status of a cluster member."""

    status: str
    address: str
