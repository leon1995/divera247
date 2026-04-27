"""Pydantic models for Divera 24/7 news API.

These models map to the schemas defined in ``api_v2_news.yaml``.
"""

import datetime
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

from divera247.models.alarm import JsonPayload


class NewsResult(BaseModel):
    """News result schema (news-result)."""

    class NewsSurveyCustomAnswer(BaseModel):
        """Custom free-text answer in a survey option."""

        id: int | None = Field(default=None, description='ID')
        ts: datetime.datetime | None = Field(default=None, description='UNIX-Timestamp')
        note: str | None = Field(default=None, description='Notiz')

    class NewsSurveyAnswer(BaseModel):
        """One selectable answer option within a survey."""

        id: int | None = Field(default=None, description='ID')
        title: str | None = Field(default=None, description='Antwort')
        note: str | None = Field(default=None, description='Notiz')
        answeredcount: int | None = Field(default=None, description='Anzahl Antworten')
        answeredlist: Sequence[int] | None = Field(default=None, description='Antwortende Benutzer')
        custom_answers: Sequence['NewsResult.NewsSurveyCustomAnswer'] | None = Field(
            default=None,
            description='Freitext-Antworten',
        )

    class NewsSurvey(BaseModel):
        """Survey definition attached to a news item."""

        id: int | None = Field(default=None, description='ID')
        title: str | None = Field(default=None, description='Frage')
        show_result_count: int | None = Field(default=None, description='Ergebnisanzeige Anzahl')
        show_result_names: int | None = Field(default=None, description='Ergebnisanzeige Namen')
        access_count: bool | None = Field(default=None, description='Anzahl sichtbar')
        access_names: bool | None = Field(default=None, description='Namen sichtbar')
        multiple_answers: bool | None = Field(default=None, description='Mehrfachauswahl möglich')
        custom_answers: bool | None = Field(default=None, description='Freitext möglich')
        response_until: bool | None = Field(default=None, description='Rückmeldung zeitlich begrenzt')
        ts_response: datetime.datetime | None = Field(default=None, description='Rückmeldung bis')
        answers: Mapping[str, 'NewsResult.NewsSurveyAnswer'] | None = Field(
            default=None,
            description='Antwortoptionen',
        )
        answer_sorting: Sequence[str | int] | None = Field(
            default=None,
            alias='answerSorting',
            description='Antwort-Reihenfolge',
        )

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    foreign_id: str | None = Field(default=None, description='Fremdschlüssel')
    author_id: int | None = Field(default=None, description='ID des Nutzers')
    date: datetime.datetime | None = Field(
        default=None,
        description='Mitteilungszeit als UNIX-Timestamp',
    )
    title: str | None = Field(default=None, description='Titel')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Ort')
    cluster: Sequence[int] | None = Field(default=None, description='IDs der Standorte')
    group: Sequence[int] | None = Field(default=None, description='IDs der Gruppen')
    user_cluster_relation: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer',
    )
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    notification_type: int | None = Field(
        default=None,
        description='Empfänger-Auswahl (1-4)',
    )
    send_push: bool | None = Field(default=None, description='Push senden')
    send_sms: bool | None = Field(default=None, description='SMS senden')
    send_call: bool | None = Field(default=None, description='Sprachanruf senden')
    send_mail: bool | None = Field(default=None, description='E-Mail senden')
    send_pager: bool | None = Field(default=None, description='Pager senden')
    survey: bool | None = Field(default=None, description='Umfrage aktiv')
    surveys: Sequence[NewsSurvey] | None = Field(default=None, description='Umfragen')
    new: bool | None = Field(default=None, description='Neu/Ungelesen')
    editable: bool | None = Field(default=None, description='Bearbeitbar')
    answerable: bool | None = Field(default=None, description='Beantwortbar')
    hidden: bool | None = Field(default=None, description='Entwurf')
    deleted: bool | None = Field(default=None, description='Im Archiv')
    ucr_addressed: Sequence[int] | None = Field(default=None, description='Adressierte Benutzer')
    ucr_answered: Sequence[int] | Mapping[str, JsonPayload] | None = Field(
        default=None,
        description='Rückmeldende Benutzer',
    )
    ucr_self_addressed: bool | None = Field(default=None, description='Selbst adressiert')
    count_recipients: int | None = Field(default=None, description='Anzahl Empfänger')
    count_read: int | None = Field(default=None, description='Anzahl Gelesen')
    ts_publish: datetime.datetime | None = Field(default=None, description='Veröffentlichungszeitpunkt')
    archive: bool | None = Field(default=None, description='Archiviert')
    ts_archive: datetime.datetime | None = Field(default=None, description='Archivierungszeitpunkt')
    ts_create: datetime.datetime | None = Field(default=None, description='UNIX-Timestamp Erstelldatum')
    ts_update: datetime.datetime | None = Field(
        default=None,
        description='UNIX-Timestamp zuletzt bearbeitet',
    )


class NewsData(BaseModel):
    """Data payload for GET /api/v2/news."""

    items: Mapping[str, NewsResult] = Field(
        default_factory=dict,
        description='Mitteilungen nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Reihenfolge der Mitteilungen',
    )


class NewsResponse(BaseModel):
    """Response schema for GET /api/v2/news."""

    success: bool = Field(description='Whether the request succeeded')
    data: NewsData | None = Field(default=None, description='News payload')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class NewsSingleResponse(BaseModel):
    """Response schema for GET/POST/PUT /api/v2/news/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: NewsResult | None = Field(default=None, description='News data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class ReachData(BaseModel):
    """Reach data for GET /api/v2/news/reach/{id}."""

    transports: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Abgeschlossene Versand-Prozesse',
    )
    received: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Benachrichtigung erhalten',
    )
    viewed: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Meldung gelesen',
    )
    confirmed: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Aktive Rückmeldung',
    )


class ReachResponse(BaseModel):
    """Response schema for GET /api/v2/news/reach/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: ReachData | None = Field(default=None, description='Reach data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class NewsInputNews(BaseModel):
    """News object for create/update (news-input.News)."""

    foreign_id: str | None = Field(default=None, description='Fremdschlüssel')
    title: str = Field(description='Titel')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Ort')
    survey: bool | None = Field(default=None, description='Umfrage hinzufügen')
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    notification_type: int = Field(
        description='Empfänger-Auswahl (1-4)',
    )
    send_push: bool | None = Field(default=None, description='Push senden')
    send_sms: bool | None = Field(default=None, description='SMS senden')
    send_call: bool | None = Field(default=None, description='Sprachanruf senden')
    send_mail: bool | None = Field(default=None, description='E-Mail senden')
    send_pager: bool | None = Field(default=None, description='Pager senden')
    ts_publish: float | None = Field(
        default=None,
        description='Zeitgesteuerte Veröffentlichung',
    )
    archive: bool | None = Field(default=None, description='Zeitgesteuert archivieren')
    ts_archive: float | None = Field(
        default=None,
        description='Zeitgesteuert archivieren',
    )
    group: Sequence[int] | None = Field(default=None, description='IDs der Gruppen')
    user_cluster_relation: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer',
    )
    cluster: Mapping[str, Mapping[str, int]] | None = Field(
        default=None,
        description='Cluster config (PRO)',
    )


class NewsInput(BaseModel):
    """Request body for creating/updating news (news-input)."""

    News: NewsInputNews = Field(description='News data')
    instructions: Mapping[str, Mapping[str, str]] | None = Field(
        default=None,
        description='Mapping instructions',
    )
    NewsSurvey: Mapping[str, object] | None = Field(
        default=None,
        description='Survey options',
    )
    NewsSurveyAnswer: Mapping[str, object] | None = Field(
        default=None,
        description='Survey answer options',
    )


class NewsConfirmPayload(BaseModel):
    """Request body for POST /api/v2/news/confirm/{id}."""

    NewsSurvey: Mapping[str, object] | None = Field(
        default=None,
        description='Survey (id, note)',
    )
    NewsSurveyAnswer: Mapping[str, object] | None = Field(
        default=None,
        description='Answer (id, checked, custom_answer)',
    )
