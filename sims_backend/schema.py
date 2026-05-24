"""
GraphQL schema for SIMS Backend project.
Complete GraphQL schema with Strawberry.
"""

import strawberry
import logging

logger = logging.getLogger(__name__)
logger.info("Initializing GraphQL schema...")

# Import all Strawberry-based app schemas
logger.debug("Loading Core schemas...")
from core.queries.core_queries import CoreQuery
from core.mutations.core_mutations import CoreMutation

logger.debug("Loading Academics schemas...")
from academics.queries.academics_queries import AcademicsQuery
from academics.mutations.academics_mutations import AcademicsMutation

logger.debug("Loading HR schemas...")
from hr.queries.hr_queries import HrQuery
from hr.mutations.hr_mutations import HrMutation

logger.debug("Loading Communication schemas...")
from communication.queries.communication_queries import CommunicationQuery
from communication.mutations.communication_mutations import CommunicationMutation

logger.debug("Loading Reports schemas...")
from reports.queries.reports_queries import ReportsQuery
from reports.mutations.reports_mutations import ReportsMutation

logger.debug("All schemas imported successfully.")


@strawberry.type
class Query(
    CoreQuery,
    AcademicsQuery,
    HrQuery,
    CommunicationQuery,
    ReportsQuery,
):
    """Root GraphQL query with Strawberry"""
    pass


@strawberry.type
class Mutation(
    CoreMutation,
    AcademicsMutation,
    HrMutation,
    CommunicationMutation,
    ReportsMutation,
):
    """Root GraphQL mutation with Strawberry"""
    pass


# Create the Strawberry schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
logger.info("GraphQL schema initialized successfully.")
