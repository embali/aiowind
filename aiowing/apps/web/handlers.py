import aiohttp_jinja2
import peewee
import psycopg2
from aiohttp import web

from aiowing import settings
from aiowing.base import handler
from aiowing.apps.web.models import Record


class Records(handler.Handler):
    @aiohttp_jinja2.template('web/records.html')
    async def get(self):
        page = int(self.request.match_info.get('page', 1))

        try:
            records = await settings.manager.execute(
                Record
                .select()
                .where(Record.active == True)
                .order_by(Record.name.asc())
                .offset((page - 1) * settings.RECORDS_PER_PAGE)
                .limit(settings.RECORDS_PER_PAGE + 1))
        except (psycopg2.OperationalError, peewee.IntegrityError,
                peewee.ProgrammingError):
            records = []

        count = len(records)

        if count == 0 and page != 1:
            return web.HTTPFound(self.request.app.router['web_records'].url())

        next_page = page + 1 if count > settings.RECORDS_PER_PAGE else None
        prev_page = page - 1 if page != 1 else None

        return dict(request=self.request,
                    records=records[:settings.RECORDS_PER_PAGE],
                    prev_page=prev_page,
                    page=page,
                    next_page=next_page)
