"""V2 API endpoint clients."""

from divera247.endpoints.alarm import AlarmEndpoint
from divera247.endpoints.attachment import AttachmentEndpoint
from divera247.endpoints.auth import AuthEndpoint
from divera247.endpoints.dashboard import DashboardEndpoint
from divera247.endpoints.event import EventEndpoint
from divera247.endpoints.file import FileEndpoint
from divera247.endpoints.message import MessageEndpoint
from divera247.endpoints.message_channel import MessageChannelEndpoint
from divera247.endpoints.news import NewsEndpoint
from divera247.endpoints.operations import OperationsEndpoint
from divera247.endpoints.password import PasswordEndpoint
from divera247.endpoints.pull import PullEndpoint
from divera247.endpoints.reporttype import ReporttypeEndpoint
from divera247.endpoints.shift_plans import ShiftPlansEndpoint
from divera247.endpoints.statusgeber import StatusgeberEndpoint
from divera247.endpoints.using_vehicle import UsingVehicleEndpoint
from divera247.endpoints.using_vehicle_crew import UsingVehicleCrewEndpoint
from divera247.endpoints.using_vehicle_property import UsingVehiclePropertyEndpoint

__all__ = (
    'AlarmEndpoint',
    'AttachmentEndpoint',
    'AuthEndpoint',
    'DashboardEndpoint',
    'EventEndpoint',
    'FileEndpoint',
    'MessageChannelEndpoint',
    'MessageEndpoint',
    'NewsEndpoint',
    'OperationsEndpoint',
    'PasswordEndpoint',
    'PullEndpoint',
    'ReporttypeEndpoint',
    'ShiftPlansEndpoint',
    'StatusgeberEndpoint',
    'UsingVehicleCrewEndpoint',
    'UsingVehicleEndpoint',
    'UsingVehiclePropertyEndpoint',
)
