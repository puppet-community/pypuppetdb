from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from datetime import timedelta

from typing import List

from pypuppetdb.QueryBuilder import (EqualsOperator)
from pypuppetdb.utils import json_to_datetime

log = logging.getLogger(__name__)


class Event(object):
    """This object represents an Event (action taken during a Puppet run, from the Report).

    :ivar node: A :obj:`string` of this event's node certname.
    :ivar status: A :obj:`string` of this event's status.
    :ivar failed: The :obj:`bool` equivalent of `status`.
    :ivar timestamp: A :obj:`datetime.datetime` of when this event happened.
    :ivar node: The hostname of the machine this event occurred on.
    :ivar hash\_: The hash of this event.
    :ivar item: :obj:`dict` with information about the item/resource this\
        event was triggered for.
    """

    def __init__(self, node: str, status: str, timestamp: str, hash_: str, title: str,
                 property_: str, message: str, new_value: str, old_value: str, type_: str,
                 class_: str, execution_path: str, source_file: str, line_number: int):
        """Creates an Event object.

        :param node: The hostname of the node this event fired on.
        :param status: The status for the event.
        :param timestamp: A timestamp of when this event occurred.
               Formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
        :param hash_: The hash of the report that contains this event.
        :param title: The resource title this event was fired for.
        :param property_: The property of the resource this event was fired for.
        :param message: A message associated with this event.
        :param new_value: The new value/state of the resource.
        :param old_value: The old value/state of the resource.
        :param type_: The type of the resource this event fired for.
        :param class_: The class responsible for running this event.
        :param execution_path: The path used to reach this particular resource.
        :param source_file: The puppet source code file containing the class.
        :param line_number: The line number in the source file containing the
               definition responsible for triggering this event.
        """
        self.node = node
        self.status = status
        if self.status == 'failure':
            self.failed = True
        else:
            self.failed = False
        self.timestamp = json_to_datetime(timestamp)
        self.hash_ = hash_
        self.item = {'title': title, 'type': type_, 'property': property_,
                     'message': message, 'old': old_value,
                     'new': new_value, 'class': class_,
                     'execution_path': execution_path, 'source_file': source_file,
                     'line_number': line_number}
        self.__string = '{0}[{1}]/{2}'.format(self.item['type'],
                                              self.item['title'],
                                              self.hash_)

    def __repr__(self):
        return str('Event: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}').format(self.__string)

    @staticmethod
    def create_from_dict(event: dict) -> 'Event':
        """Create an Event object from a JSON object (dict) representing an Event
        returned by PuppetDB API events endpoint:
        https://puppet.com/docs/puppetdb/5.2/api/query/v4/events.html#response-format .

        :param event: JSON object (dict) representing an Event
        """
        return Event(
            node=event['certname'],
            status=event['status'],
            timestamp=event['timestamp'],
            hash_=event['report'],
            title=event['resource_title'],
            property_=event['property'],
            message=event['message'],
            new_value=event['new_value'],
            old_value=event['old_value'],
            type_=event['resource_type'],
            class_=event['containing_class'],
            execution_path=event['containment_path'],
            source_file=event['file'],
            line_number=event['line'],
        )


class Report(object):
    """This object represents a Report (of a Puppet run).

    :ivar node: The hostname this report originated from.
    :ivar hash\_: Unique identifier of this report.
    :ivar start: :obj:`datetime.datetime` when the Puppet agent run started.
    :ivar end: :obj:`datetime.datetime` when the Puppet agent run ended.
    :ivar received: :obj:`datetime.datetime` when the report finished\
        uploading.
    :ivar version: :obj:`string` catalog configuration version.
    :ivar format\_: :obj:`int` catalog format version.
    :ivar agent_version: :obj:`string` Puppet Agent version.
    :ivar run_time: :obj:`datetime.timedelta` of **end** - **start**.
    :ivar transaction: UUID identifying this transaction.
    :ivar environment: The environment assigned to the node that submitted\
        this report.
    :ivar status: The status associated to this report's node.
    :ivar metrics: :obj:`list` containing :obj:`dict` of all metrics\
        associated with this report.
    :ivar logs: :obj:`list` containing :obj:`dict` of all logs\
        associated with this report.
    :ivar code_id: :obj:`string` used to tie a catalog to the Puppet Code\
        which generated the catalog.
    :ivar catalog_uuid: :obj:`string` used to tie this report to the catalog\
        used on this Puppet run.
    :ivar cached_catalog_status: :obj:`string` identifying if this Puppet run\
        used a cached catalog, if so weather it was a result of an error or\
        otherwise.
    :ivar producer: :obj:`string` representing the certname of the Puppet\
        Master that sent the report to PuppetDB
    """

    # no type hint for "api" to prevent circular import
    def __init__(self, api, node: str, hash_: str, start: str, end: str, received: str,
                 version: str, format_: int, agent_version: str, transaction: str,
                 environment: str = None, status: str = None, noop: bool = False,
                 noop_pending: bool = False, metrics: List[dict] = [{}], logs: List[dict] = [{}],
                 code_id: str = None, catalog_uuid: str = None, cached_catalog_status: str = None,
                 producer: str = None):
        """Creates a Report object.

        :param api: API object (for subqueries)
        :param node: The hostname of the node this report originated on.
        :param hash\_: A string uniquely identifying this report.
        :param start: The start time of the agent run. Formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
        :param end: The time the agent finished its run. Formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
        :param received: The time PuppetDB received the report.
               Formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
        :param version: The catalog / configuration version.
        :param format\_: The catalog format version.
        :param agent_version: The Puppet agent version.
        :param transaction: The UUID of this transaction.
        :param environment: (Optional) The environment assigned to the node that\
            submitted this report.
        :param status: (Optional) The status associated to this report's node.
        :param noop: (Default `False`) A flag indicating weather the report was\
            produced by a noop run.
        :param noop_pending: (Default `False`) A flag indicating weather the \
            report had pending changes produced by a noop run.
        :param metrics: (Optional) All metrics associated with this report.
        :param logs: (Optional) All logs associated with this report.
        :param code_id: (Optional) Ties the catalog to the Puppet Code that\
            generated the catalog.
        :param catalog_uuid: (Optional) Ties the report to the catalog used\
            from that Puppet run.
        :param cached_catalog_status: (Optional) Identifies if the Puppet run\
            used a cached catalog and weather or not it was used due to an\
            error. Can be one of 'explicitly_requested', 'on_failure',\
            'not_used' not 'null'.
        :param producer: (Optional) The certname of the Puppet Master that\
            sent the report to PuppetDB
        """
        self.node = node
        self.hash_ = hash_
        self.start = json_to_datetime(start)
        self.end = json_to_datetime(end)
        self.received = json_to_datetime(received)
        self.version = version
        self.format_ = format_
        self.agent_version = agent_version
        self.run_time = self.end - self.start
        self.transaction = transaction
        self.environment = environment
        self.status = 'noop' if noop and noop_pending else status
        self.metrics = metrics
        self.logs = logs
        self.code_id = code_id
        self.catalog_uuid = catalog_uuid
        self.cached_catalog_status = cached_catalog_status
        self.producer = producer
        self.__string = '{0}'.format(self.hash_)

        self.__api = api

    def __repr__(self):
        return str('Report: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}').format(self.__string)

    def events(self, **kwargs):
        """Get all :class:`pypuppetdb.types.Event` for this report. Additional arguments may also be
        specified that will be passed to the query function.
        """
        return self.__api.events(query=EqualsOperator("report", self.hash_),
                                 **kwargs)

    @staticmethod
    # no type hint for "api" to prevent circular import
    def create_from_dict(api, report: dict) -> 'Report':
        """Create a Report from a JSON object (dict) representing a Report
        returned by PuppetDB API reports endpoint:
        https://puppet.com/docs/puppetdb/5.2/api/query/v4/reports.html#response-format .

        :param api: API object (for subqueries)
        :param report: JSON object (dict) representing a Report
        """
        return Report(
            api=api,
            node=report['certname'],
            hash_=report['hash'],
            start=report['start_time'],
            end=report['end_time'],
            received=report['receive_time'],
            version=report['configuration_version'],
            format_=report['report_format'],
            agent_version=report['puppet_version'],
            transaction=report['transaction_uuid'],
            environment=report['environment'],
            status=report['status'],
            noop=report.get('noop', False),
            noop_pending=report.get('noop_pending', False),
            metrics=report['metrics']['data'],
            logs=report['logs']['data'],
            code_id=report.get('code_id', None),
            catalog_uuid=report.get('catalog_uuid', None),
            cached_catalog_status=report.get('cached_catalog_status', None),
            # producer=report.get('producer', None) # TODO: consider adding this missing param
        )


class Fact(object):
    """This object represents a fact. Unless otherwise specified all
    parameters are required.

    :param node: The hostname this fact was collected from.
    :type node: :obj:`string`
    :param name: The fact's name, such as 'osfamily'
    :type name: :obj:`string`
    :param value: The fact's value, such as 'Debian'
    :type value: :obj:`string` or :obj:`int` or :obj:`dict`
    :param environment: (Optional) The fact's environment, such as\
        'production'
    :type environment: :obj:`string`

    :ivar node: :obj:`string` holding the hostname.
    :ivar name: :obj:`string` holding the fact's name.
    :ivar value: :obj:`string` or :obj:`int` or :obj:`dict` holding the\
        fact's value.
    :ivar environment: :obj:`string` holding the fact's environment
    """

    @staticmethod
    def create_from_dict(fact):
        return Fact(
            node=fact['certname'],
            name=fact['name'],
            value=fact['value'],
            environment=fact['environment']
        )

    def __init__(self, node, name, value, environment=None):
        self.node = node
        self.name = name
        self.value = value
        self.environment = environment
        self.__string = '{0}/{1}'.format(self.name, self.node)

    def __repr__(self):
        return str('Fact: {0}'.format(self.__string))

    def __str__(self):
        return str('{0}').format(self.__string)


class Resource(object):
    """This object represents a resource. Unless otherwise specified all
    parameters are required.

    :param node: The hostname this resource is located on.
    :type node: :obj:`string`
    :param name: The name of the resource in the Puppet manifest.
    :type name: :obj:`string`
    :param type\_: Type of the Puppet resource.
    :type type\_: :obj:`string`
    :param tags: Tags associated with this resource.
    :type tags: :obj:`list`
    :param exported: If it's an exported resource.
    :type exported: :obj:`bool`
    :param sourcefile: The Puppet manifest this resource is declared in.
    :type sourcefile: :obj:`string`
    :param sourceline: The line this resource is declared at.
    :type sourceline: :obj:`int`
    :param parameters: (Optional) The parameters this resource has been\
        declared with.
    :type parameters: :obj:`dict`
    :param environment: (Optional) The environment of the node associated\
        with this resource.
    :type environment: :obj:`string`

    :ivar node: The hostname this resources is located on.
    :ivar name: The name of the resource in the Puppet manifest.
    :ivar type\_: The type of Puppet resource.
    :ivar exported: :obj:`bool` if the resource is exported.
    :ivar sourcefile: The Puppet manifest this resource is declared in.
    :ivar sourceline: The line this resource is declared at.
    :ivar parameters: :obj:`dict` with key:value pairs of parameters.
    :ivar relationships: :obj:`list` Contains all relationships to other\
        resources
    :ivar environment: :obj:`string` The environment of the node associated\
        with this resource.
    """

    def __init__(self, node, name, type_, tags, exported, sourcefile,
                 sourceline, environment=None, parameters={}):
        self.node = node
        self.name = name
        self.type_ = type_
        self.tags = tags
        self.exported = exported
        self.sourcefile = sourcefile
        self.sourceline = sourceline
        self.parameters = parameters
        self.relationships = []
        self.environment = environment
        self.__string = '{0}[{1}]'.format(self.type_, self.name)

    def __repr__(self):
        return str('<Resource: {0}>').format(self.__string)

    def __str__(self):
        return str('{0}').format(self.__string)

    @staticmethod
    def create_from_dict(resource):
        return Resource(
            node=resource['certname'],
            name=resource['title'],
            type_=resource['type'],
            tags=resource['tags'],
            exported=resource['exported'],
            sourcefile=resource['file'],
            sourceline=resource['line'],
            parameters=resource['parameters'],
            environment=resource['environment'],
        )


class Node(object):
    """This object represents a node. It additionally has some helper methods
    so that you can query for resources or facts directly from the node scope.
    Unless otherwise specified all parameters are required.

    :param api: API object.
    :type api: :class:`pypuppetdb.api.BaseAPI`
    :param name: Hostname of this node.
    :type name: :obj:`string`
    :param deactivated: (default `None`) Time this node was deactivated at.
    :type deactivated: :obj:`string` formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param report_timestamp: (default `None`) Time of the last report.
    :type report_timestamp: :obj:`string` formatted as\
            ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param catalog_timestamp: (default `None`) Time the last time a catalog\
            was compiled.
    :type catalog_timestamp: :obj:`string` formatted as\
            ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param facts_timestamp: (default `None`) Time the last time facts were\
            collected.
    :type facts_timestamp: :obj:`string` formatted as\
            ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param status_report: (default `None`) Status of latest report \
            from the node changed | unchanged | failed
    :type status: :obj:`string`
    :param noop: (Default `False`) A flag indicating whether the latest \
        report of the node was produced by a noop run.
    :type noop: :obj:`bool`
    :param noop_pending: (Default `False`) A flag indicating whether \
        the latest report of the node had pending changes \
        produced by a noop run.
    :type noop_pending: :obj:`bool`
    :param events: (default `None`) Counted events from latest Report
    :type events: :obj:`dict`
    :param unreported: (default `False`) if node is considered unreported
    :type unreported_time: :obj:`bool`
    :param unreported_time: (default `None`) Time since last report
    :type unreported_time: :obj:`string`
    :param report_environment: (default 'production') The environment of the\
            last received report for this node
    :type report_environment: :obj:`string`
    :param catalog_environment: (default 'production') The environment of the\
            last received catalog for this node
    :type catalog_environment: :obj:`string`
    :param facts_environment: (default 'production') The environment of the\
            last received fact set for this node
    :type facts_environment: :obj:`string`
    :param latest_report_hash: The hash of the latest report from this node,\
            is only available in PuppetDB 3.2 and later
    :type latest_report_hash: :obj:`string`
    :param cached_catalog_status: Cached catalog status of the last puppet run\
            on this node, possible values are 'explicitly_requested',\
            'on_failure', 'not_used' or None.
    :type cached_catalog_status: :obj:`string`

    :ivar name: Hostname of this node.
    :ivar deactivated: :obj:`datetime.datetime` when this host was\
            deactivated or `False`.
    :ivar report_timestamp: :obj:`datetime.datetime` when the last run\
            occured or `None`.
    :ivar catalog_timestamp: :obj:`datetime.datetime` last time a catalog was\
            compiled or `None`.
    :ivar facts_timestamp: :obj:`datetime.datetime` last time when facts were\
            collected or `None`.
    :ivar report_environment: :obj:`string` the environment of the last\
            received report for this node.
    :ivar catalog_environment: :obj:`string` the environment of the last\
            received catalog for this node.
    :ivar facts_environment: :obj:`string` the environment of the last\
            received fact set for this node.
    :ivar latest_report_hash: :obj:`string` the hash value of the latest\
            report the current node reported. Available in PuppetDB 3.2\
            and later.
    :ivar cached_catalog_status: :obj:`string` the status of the cached\
            catalog from the last puppet run.
    """

    def __init__(self, api, name, deactivated=None, expired=None,
                 report_timestamp=None, catalog_timestamp=None,
                 facts_timestamp=None, status_report=None,
                 noop=False, noop_pending=False, events=None,
                 unreported=False, unreported_time=None,
                 report_environment='production',
                 catalog_environment='production',
                 facts_environment='production',
                 latest_report_hash=None, cached_catalog_status=None):
        self.name = name
        self.events = events
        self.unreported_time = unreported_time
        self.report_timestamp = report_timestamp
        self.catalog_timestamp = catalog_timestamp
        self.facts_timestamp = facts_timestamp
        self.report_environment = report_environment
        self.catalog_environment = catalog_environment
        self.facts_environment = facts_environment
        self.latest_report_hash = latest_report_hash
        self.cached_catalog_status = cached_catalog_status

        if unreported:
            self.status = 'unreported'
        elif noop and noop_pending:
            self.status = 'noop'
        else:
            self.status = status_report

        if deactivated is not None:
            self.deactivated = json_to_datetime(deactivated)
        else:
            self.deactivated = False
        if expired is not None:
            self.expired = json_to_datetime(expired)
        else:
            self.expired = False
        if report_timestamp is not None:
            self.report_timestamp = json_to_datetime(report_timestamp)
        else:
            self.report_timestamp = report_timestamp
        if facts_timestamp is not None:
            self.facts_timestamp = json_to_datetime(facts_timestamp)
        else:
            self.facts_timestamp = facts_timestamp
        if catalog_timestamp is not None:
            self.catalog_timestamp = json_to_datetime(catalog_timestamp)
        else:
            self.catalog_timestamp = catalog_timestamp

        self.__api = api
        self.__string = self.name

    def __repr__(self):
        return str('<Node: {0}>').format(self.__string)

    def __str__(self):
        return str('{0}').format(self.__string)

    def facts(self, query=None, **kwargs):
        """Get all facts of this node. Additional arguments may also be
        specified that will be passed to the query function.
        """
        q = EqualsOperator("certname", self.name)
        if query:
            q = AndOperator()
            q.add(EqualsOperator("certname", self.name))
            q.add(query)

        return self.__api.facts(query=q, **kwargs)

    def fact(self, name):
        """Get a single fact from this node."""
        facts = self.facts(name=name)
        return next(fact for fact in facts)

    def resources(self, type_=None, title=None, **kwargs):
        """Get all resources of this node or all resources of the specified
        type. Additional arguments may also be specified that will be passed
        to the query function.
        """
        if type_ is None:
            resources = self.__api.resources(
                query=EqualsOperator("certname", self.name),
                **kwargs)
        elif type_ is not None and title is None:
            resources = self.__api.resources(
                type_=type_,
                query=EqualsOperator("certname", self.name),
                **kwargs)
        else:
            resources = self.__api.resources(
                type_=type_,
                title=title,
                query=EqualsOperator("certname", self.name),
                **kwargs)
        return resources

    def resource(self, type_, title, **kwargs):
        """Get a resource matching the supplied type and title. Additional
        arguments may also be specified that will be passed to the query
        function.
        """
        resources = self.__api.resources(
            type_=type_,
            title=title,
            query=EqualsOperator("certname", self.name),
            **kwargs)
        return next(resource for resource in resources)

    def reports(self, **kwargs):
        """Get all reports for this node. Additional arguments may also be
        specified that will be passed to the query function.
        """
        return self.__api.reports(
            query=EqualsOperator("certname", self.name),
            **kwargs)

    @staticmethod
    def create_from_dict(query_api, node, with_status, with_event_numbers, latest_events, now,
                         unreported):

        node['status_report'] = None
        node['events'] = None

        if with_status:
            if with_event_numbers:
                status = [s for s in latest_events
                          if s['subject']['title'] == node['certname']]

                try:
                    node['status_report'] = node['latest_report_status']

                    if status:
                        node['events'] = status[0]
                except KeyError:
                    if status:
                        node['events'] = status = status[0]
                        if status['successes'] > 0:
                            node['status_report'] = 'changed'
                        if status['noops'] > 0:
                            node['status_report'] = 'noop'
                        if status['failures'] > 0:
                            node['status_report'] = 'failed'
                    else:
                        node['status_report'] = 'unchanged'
            else:
                node['status_report'] = node['latest_report_status']
                node['events'] = {
                    'successes': 0,
                    'failures': 0,
                    'noops': 0,
                }
                if node['status_report'] == 'changed':
                    node['events']['successes'] = 'some'
                elif node['status_report'] == 'noop':
                    node['events']['noops'] = 'some'
                elif node['status_report'] == 'failed':
                    node['events']['failures'] = 'some'

            # node report age
            if node['report_timestamp'] is not None:
                try:
                    last_report = json_to_datetime(
                        node['report_timestamp'])
                    last_report = last_report.replace(tzinfo=None)
                    unreported_border = now - timedelta(hours=unreported)
                    if last_report < unreported_border:
                        delta = (now - last_report)
                        node['unreported'] = True
                        node['unreported_time'] = '{0}d {1}h {2}m'.format(
                            delta.days,
                            int(delta.seconds / 3600),
                            int((delta.seconds % 3600) / 60)
                        )
                except AttributeError:
                    node['unreported'] = True

            if not node['report_timestamp']:
                node['unreported'] = True

        return Node(query_api,
                    name=node['certname'],
                    deactivated=node['deactivated'],
                    expired=node['expired'],
                    report_timestamp=node['report_timestamp'],
                    catalog_timestamp=node['catalog_timestamp'],
                    facts_timestamp=node['facts_timestamp'],
                    status_report=node['status_report'],
                    noop=node.get('latest_report_noop'),
                    noop_pending=node.get('latest_report_noop_pending'),
                    events=node['events'],
                    unreported=node.get('unreported'),
                    unreported_time=node.get('unreported_time'),
                    report_environment=node['report_environment'],
                    catalog_environment=node['catalog_environment'],
                    facts_environment=node['facts_environment'],
                    latest_report_hash=node.get('latest_report_hash'),
                    cached_catalog_status=node.get('cached_catalog_status')
                    )


class Catalog(object):
    """
    This object represents a compiled catalog from puppet. It contains\
    Resource and Edge object that represent the dependency graph. Unless\
    otherwise specified all parameters are required.

    :param node: Name of the host
    :type node: :obj:`string`
    :param edges: Edges returned from Catalog data
    :type edges: :obj:`list` containing :obj:`dict` of\
        :class:`pypuppetdb.types.Edge`
    :param resources: :class:`pypuppetdb.types.Resource` managed as of this\
        Catalog.
    :type resources: :obj:`dict` of :class:`pypuppetdb.types.Resource`
    :param version: Catalog version from Puppet (unique for each node)
    :type version: :obj:`string`
    :param transaction_uuid: A string used to match the catalog with the\
        corresponding report that was issued during the same puppet run
    :type transaction_uuid: :obj:`string`
    :param environment: The environment associated with the catalog's\
        certname.
    :type environment: :obj:`string`
    :param code_id: The string used to tie this catalog to the Puppet code\
        which generated the catalog.
    :type code_id: :obj:`string`
    :param catalog_uuid: Universally unique identifier of this catalog.
    :type catalog_uuid: :obj:`string`
    :param producer: The certname of the Puppet Master that sent the catalog\
        to PuppetDB
    :type producer: :obj:`string`

    :ivar node: :obj:`string` Name of the host
    :ivar version: :obj:`string` Catalog version from Puppet
        (unique for each node)
    :ivar transaction_uuid: :obj:`string` used to match the catalog with
        corresponding report
    :ivar edges: :obj:`list` of :obj:`Edge` The source Resource object\
        of the relationship
    :ivar environment: :obj:`string` Environment associated with the
        catalog's certname
    :ivar code_id: :obj:`string` ties the catalog to the Puppet code that\
        generated the catalog
    :ivar catalog_uuid: :obj:`string` uniquely identifying this catalog.
    :ivar producer: :obj:`string` of the Puppet Master that sent the catalog\
        to PuppetDB
    """

    def __init__(self, node, edges, resources, version, transaction_uuid,
                 environment=None, code_id=None, catalog_uuid=None,
                 producer=None):

        self.node = node
        self.version = version
        self.transaction_uuid = transaction_uuid
        self.environment = environment
        self.code_id = code_id
        self.catalog_uuid = catalog_uuid
        self.producer = producer

        self.resources = dict()
        for resource in resources:
            if 'file' not in resource:
                resource['file'] = None
            if 'line' not in resource:
                resource['line'] = None
            identifier = resource['type'] + '[' + resource['title'] + ']'
            res = Resource(node=node, name=resource['title'],
                           type_=resource['type'], tags=resource['tags'],
                           exported=resource['exported'],
                           sourcefile=resource['file'],
                           sourceline=resource['line'],
                           parameters=resource['parameters'],
                           environment=self.environment)
            self.resources[identifier] = res

        self.edges = []
        for edge in edges:
            identifier_source = edge['source_type'] + '[' + edge['source_title'] + ']'
            identifier_target = edge['target_type'] + '[' + edge['target_title'] + ']'
            e = Edge(source=self.resources[identifier_source],
                     target=self.resources[identifier_target],
                     relationship=edge['relationship'],
                     node=self.node)
            self.edges.append(e)
            self.resources[identifier_source].relationships.append(e)
            self.resources[identifier_target].relationships.append(e)

        self.__string = '{0}/{1}'.format(self.node, self.transaction_uuid)

    def __repr__(self):
        return str('<Catalog: {0}>').format(self.__string)

    def __str__(self):
        return str('{0}').format(self.__string)

    def get_resources(self):
        return self.resources.values()

    def get_resource(self, resource_type, resource_title):
        identifier = resource_type + \
                     '[' + resource_title + ']'
        return self.resources[identifier]

    def get_edges(self):
        return iter(self.edges)

    @staticmethod
    def create_from_dict(catalog):
        return Catalog(node=catalog['certname'],
                       edges=catalog['edges']['data'],
                       resources=catalog['resources']['data'],
                       version=catalog['version'],
                       transaction_uuid=catalog['transaction_uuid'],
                       environment=catalog['environment'],
                       code_id=catalog.get('code_id'),
                       catalog_uuid=catalog.get('catalog_uuid'))


class Edge(object):
    """
    This object represents the connection between two Resource objects.
    Unless otherwise specified all parameters are required.

    :param source: The source Resource object of the relationship
    :type source: :class:`pypuppetdb.Resource`
    :param target: The target Resource object of the relationship
    :type target: :class:`pypuppetdb.Resource`
    :param relationship: Name of the Puppet Resource Relationship
    :type relationship: :obj:`string`
    :param node: The certname of the node that owns this Relationship
    :type node: :obj:`string`

    :ivar source: :obj:`Resource` The source Resource object
    :ivar target: :obj:`Resource` The target Resource object
    :ivar relationship: :obj:`string` Name of the Puppet Resource relationship
    :ivar node: :obj:`string` The name of the node that owns this relationship
    """

    def __init__(self, source, target, relationship, node=None):
        self.source = source
        self.target = target
        self.relationship = relationship
        self.node = node
        self.__string = '{0} - {1} - {2}'.format(self.source,
                                                 self.relationship,
                                                 self.target)

    def __repr__(self):
        return str('<Edge: {0}>').format(self.__string)

    def __str__(self):
        return str('{0}').format(self.__string)

    @staticmethod
    def create_from_dict(edge):
        identifier_source = edge['source_type'] + '[' + edge['source_title'] + ']'
        identifier_target = edge['target_type'] + '[' + edge['target_title'] + ']'
        return Edge(source=identifier_source,
                    target=identifier_target,
                    relationship=edge['relationship'],
                    node=edge['certname'])


class Inventory(object):
    """This object represents a Node Inventory entry returned from
    the Inventory endpoint.

    :param node: The certname of the node associated with the inventory.
    :type node: :obj:`string`
    :param time: The time at which PuppetDB received the facts in the
        inventory.
    :type time: :obj:`string` formatted as ``%Y-%m-%dT%H:%M:%S.%fZ``
    :param environment: The environment associated with the inventory's
        certname.
    :type environment: :obj:`string`
    :param facts: The dictionary of key-value pairs for the nodes
        assosciated facts.
    :type facts: :obj:`dict`
    :param trusted: The trusted data from the node.
    :type trusted: :obj:`dict`

    :ivar node: The certname of the node associated with the inventory.
    :ivar time: The time at which PuppetDB received the facts in the
        inventory.
    :ivar environment: The environment associated with the inventory's
        certname.
    :ivar facts: The dictionary of key-value pairs for the nodes
        associated facts.
    :ivar trusted: The trusted data from the node.
    """

    def __init__(self, node, time, environment, facts, trusted):
        self.node = node
        self.time = json_to_datetime(time)
        self.environment = environment
        self.facts = facts
        self.trusted = trusted
        self.__string = self.node

    def __repr__(self):
        return str('<Inventory: {0}>').format(self.__string)

    def __str__(self):
        return str("{0}").format(self.__string)

    @staticmethod
    def create_from_dict(inv):
        return Inventory(
            node=inv['certname'],
            time=inv['timestamp'],
            environment=inv['environment'],
            facts=inv['facts'],
            trusted=inv['trusted']
        )
