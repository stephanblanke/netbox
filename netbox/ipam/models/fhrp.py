from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from extras.utils import extras_features
from netbox.models import ChangeLoggedModel, PrimaryModel
from ipam.choices import *
from ipam.constants import *

__all__ = (
    'FHRPGroup',
    'FHRPGroupAssignment',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class FHRPGroup(PrimaryModel):
    """
    A grouping of next hope resolution protocol (FHRP) peers. (For instance, VRRP or HSRP.)
    """
    group_id = models.PositiveSmallIntegerField(
        verbose_name='Group ID'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='fhrpgroup',
        blank=True,
        null=True
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='fhrpgroup',
        blank=True,
        null=True
    )
    vlan_group = models.ForeignKey(
        to='ipam.VLANGroup',
        on_delete=models.PROTECT,
        related_name='fhrpgroup',
        blank=True,
        null=True
    )
    vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.PROTECT,
        related_name='fhrpgroup',
        blank=True,
        null=True,
        verbose_name='VLAN'
    )
    protocol = models.CharField(
        max_length=50,
        choices=FHRPGroupProtocolChoices
    )
    auth_type = models.CharField(
        max_length=50,
        choices=FHRPGroupAuthTypeChoices,
        blank=True,
        verbose_name='Authentication type'
    )
    auth_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Authentication key'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='fhrpgroup'
    )

    clone_fields = ('site', 'tenant', 'site', 'vlan_group', 'vlan',
                    'protocol', 'auth_type', 'auth_key')

    class Meta:
        ordering = ['protocol', 'group_id', 'pk']
        verbose_name = 'FHRP group'

    def __str__(self):
        name = f'{self.get_protocol_display()}: {self.group_id}'

        # Append the first assigned IP addresses (if any) to serve as an additional identifier
        if self.pk:
            ip_address = self.ip_addresses.first()
            if ip_address:
                return f"{name} ({ip_address})"

        return name

    def get_absolute_url(self):
        return reverse('ipam:fhrpgroup', args=[self.pk])

    def clean(self):
        super().clean()

        if self.site and self.vlan_group:

            if self.vlan_group.scope != self.site:
                raise ValidationError({
                    'vlan_group': f"If a site is assigned, the VLAN group must be assigned to this site."
                })

        if self.vlan_group and self.vlan:

            if self.vlan.group != self.vlan_group:
                raise ValidationError({
                    'vlan': f"If a VLAN group is assigned, the VLAN must be assigned to this VLAN group."
                })


@extras_features('webhooks')
class FHRPGroupAssignment(ChangeLoggedModel):
    interface_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    interface_id = models.PositiveIntegerField()
    interface = GenericForeignKey(
        ct_field='interface_type',
        fk_field='interface_id'
    )
    group = models.ForeignKey(
        to='ipam.FHRPGroup',
        on_delete=models.CASCADE
    )
    priority = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(FHRPGROUPASSIGNMENT_PRIORITY_MIN),
            MaxValueValidator(FHRPGROUPASSIGNMENT_PRIORITY_MAX)
        )
    )

    clone_fields = ('interface_type', 'interface_id')

    class Meta:
        ordering = ('-priority', 'pk')
        unique_together = ('interface_type', 'interface_id', 'group')
        verbose_name = 'FHRP group assignment'

    def __str__(self):
        return f'{self.interface}: {self.group} ({self.priority})'

    def get_absolute_url(self):
        # Used primarily for redirection after creating a new assignment
        if self.interface:
            return self.interface.get_absolute_url()
        return None
