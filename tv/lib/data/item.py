# Miro - an RSS based video player application
# Copyright (C) 2012
# Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""miro.data.item -- Defines ItemInfo and describes how to create them

ItemInfo is the read-only interface to database items.  To create one you need
to run a SELECT on the database and pass in the data from one row.

column_info() and join_sql() describe what columns need to be selected and how
to join the tables together in order to create an ItemInfo.
"""

import collections
import datetime
import os

from miro import app
from miro import displaytext
from miro import filetypes
from miro import fileutil
from miro import prefs
from miro import schema
from miro import util
from miro.plat import resources
from miro.plat.utils import PlatformFilenameType

class SelectColumn(object):
    """Describes a single column that we select for ItemInfo.

    :attribute table: name of the table that contains the column
    :attribute column: column nabe
    :attribute attr_name: attribute name in ItemInfo
    """

    # _schema_map maps (table, column) tuples to their SchemaItem objects
    _schema_map = {}
    for object_schema in schema.object_schemas:
        for column_name, schema_item in object_schema.fields:
            _schema_map[object_schema.table_name, column_name] = schema_item

    def __init__(self, table, column, attr_name=None):
        if attr_name is None:
            attr_name = column
        self.table = table
        self.column = column
        self.attr_name = attr_name

    def sqlite_type(self):
        """Get the sqlite type specification for this column."""
        schema_item = self._schema_map[self.table, self.column]
        return app.db.get_sqlite_type(schema_item)

# Construct the values for column_info() now, since they don't change.
_column_info = [
    SelectColumn('item', 'id'),
    SelectColumn('item', 'new'),
    SelectColumn('item', 'title'),
    SelectColumn('item', 'feed_id'),
    SelectColumn('item', 'parent_id'),
    SelectColumn('item', 'parent_title'),
    SelectColumn('item', 'downloader_id'),
    SelectColumn('item', 'is_file_item'),
    SelectColumn('item', 'pending_manual_download'),
    SelectColumn('item', 'pending_reason'),
    SelectColumn('item', 'expired'),
    SelectColumn('item', 'keep'),
    SelectColumn('item', 'creation_time', 'date_added'),
    SelectColumn('item', 'downloaded_time'),
    SelectColumn('item', 'watched_time'),
    SelectColumn('item', 'last_watched'),
    SelectColumn('item', 'subtitle_encoding'),
    SelectColumn('item', 'is_container_item'),
    SelectColumn('item', 'release_date'),
    SelectColumn('item', 'duration', 'duration_ms'),
    SelectColumn('item', 'screenshot'),
    SelectColumn('item', 'resume_time'),
    SelectColumn('item', 'license'),
    SelectColumn('item', 'rss_id'),
    SelectColumn('item', 'entry_description'),
    SelectColumn('item', 'enclosure_type', 'mime_type'),
    SelectColumn('item', 'enclosure_format'),
    SelectColumn('item', 'enclosure_size'),
    SelectColumn('item', 'link', 'permalink'),
    SelectColumn('item', 'payment_link'),
    SelectColumn('item', 'comments_link'),
    SelectColumn('item', 'url'),
    SelectColumn('item', 'was_downloaded'),
    SelectColumn('item', 'filename', 'raw_filename'),
    SelectColumn('item', 'play_count'),
    SelectColumn('item', 'skip_count'),
    SelectColumn('item', 'cover_art'),
    SelectColumn('item', 'description'),
    SelectColumn('item', 'album'),
    SelectColumn('item', 'album_artist'),
    SelectColumn('item', 'artist'),
    SelectColumn('item', 'track'),
    SelectColumn('item', 'album_tracks'),
    SelectColumn('item', 'year'),
    SelectColumn('item', 'genre'),
    SelectColumn('item', 'rating'),
    SelectColumn('item', 'file_type'),
    SelectColumn('item', 'has_drm'),
    SelectColumn('item', 'show'),
    SelectColumn('item', 'episode_id'),
    SelectColumn('item', 'episode_number'),
    SelectColumn('item', 'season_number'),
    SelectColumn('item', 'kind'),
    SelectColumn('item', 'net_lookup_enabled'),
    SelectColumn('item', 'eligible_for_autodownload'),
    SelectColumn('feed', 'orig_url', 'feed_url'),
    SelectColumn('feed', 'expire', 'feed_expire'),
    SelectColumn('feed', 'expireTime', 'feed_expire_time'),
    SelectColumn('feed', 'autoDownloadable', 'feed_auto_downloadable'),
    SelectColumn('feed', 'getEverything', 'feed_get_everything'),
    SelectColumn('icon_cache', 'filename', 'raw_icon_cache_filename'),
    SelectColumn('remote_downloader', 'content_type',
                  'downloader_content_type'),
    SelectColumn('remote_downloader', 'state', 'downloader_state'),
    SelectColumn('remote_downloader', 'reason_failed'),
    SelectColumn('remote_downloader', 'short_reason_failed'),
    SelectColumn('remote_downloader', 'type', 'downloader_type'),
    SelectColumn('remote_downloader', 'retry_time'),
    SelectColumn('remote_downloader', 'eta'),
    SelectColumn('remote_downloader', 'rate'),
    SelectColumn('remote_downloader', 'upload_rate'),
    SelectColumn('remote_downloader', 'current_size', 'downloaded_size'),
    SelectColumn('remote_downloader', 'total_size', 'downloader_size'),
    SelectColumn('remote_downloader', 'upload_size'),
    SelectColumn('remote_downloader', 'activity', 'startup_activity'),
    SelectColumn('remote_downloader', 'seeders'),
    SelectColumn('remote_downloader', 'leechers'),
    SelectColumn('remote_downloader', 'connections'),
]

def column_info():
    """Get the columns used to create the ItemInfo objects

    :returns: list of SelectColumn objects
    """
    return _column_info

def join_sql():
    """Returns SQL specifying the tables needing to be joined to the item
    table in order to create an ItemInfo.
    """
    return """\
LEFT JOIN feed ON feed.id=item.feed_id
LEFT JOIN remote_downloader ON remote_downloader.id=item.downloader_id
LEFT JOIN icon_cache ON icon_cache.id=item.icon_cache_id"""

# ItemRow is the base class for item.
ItemRow = collections.namedtuple("ItemRow",
                                 [c.attr_name for c in column_info()])

def _unicode_to_filename(unicode_value):
    # Convert a unicode value from the database to FilenameType
    # FIXME: This code is not very good and should be replaces as part of
    # #13182
    if unicode_value is not None and PlatformFilenameType != unicode:
        return unicode_value.encode('utf-8')
    else:
        return unicode_value

class ItemInfo(ItemRow):
    """ItemInfo represents a row in one of the item lists.

    This work similarly to the miro.item.Item class, except it's read-only.
    """
    html_stripper = util.HTMLStripper()

    source_type = 'database'
    remote = False
    device = None

    def __init__(self, *row_data):
        """Create an ItemInfo object.

        :param *row_data: data from sqlite.  There should be a value for each
        SelectColumn that column_info() returns.
        """
        ItemRow.__init__(self, *row_data)

    # NOTE: The previous ItemInfo API was all attributes, so we use properties
    # to try to match that.

    @property
    def filename(self):
        return _unicode_to_filename(self.raw_filename)

    @property
    def downloaded(self):
        return self.has_filename

    @property
    def has_filename(self):
        return self.raw_filename is not None

    @property
    def icon_cache_filename(self):
        return _unicode_to_filename(self.raw_icon_cache_filename)

    @property
    def cover_art_filename(self):
        return _unicode_to_filename(self.cover_art)

    @property
    def is_playable(self):
        return self.has_filename and self.file_type != u'other'

    @property
    def is_torrent(self):
        return self.downloader_type == u'BitTorrent'

    @property
    def is_torrent_folder(self):
        return self.is_torrent and self.is_container_item

    def looks_like_torrent(self):
        return self.is_torrent or filetypes.is_torrent_filename(self.url)

    @property
    def description_stripped(self):
        if not hasattr(self, '_description_stripped'):
            self._description_stripped = ItemInfo.html_stripper.strip(
                self.description)
        return self._description_stripped

    @property
    def thumbnail(self):
        if self.cover_art and fileutil.exists(self.cover_art_filename):
            return self.cover_art_filename
        if (self.raw_icon_cache_filename is not None and
            fileutil.exists(self.icon_cache_filename)):
            return self.icon_cache_filename
        if self.screenshot and fileutil.exists(self.screenshot):
            return self.screenshot
        if self.is_container_item:
            return resources.path("images/thumb-default-folder.png")
        else:
            # TODO: check for feed thumbnail here
            if self.file_type == u'audio':
                return resources.path("images/thumb-default-audio.png")
            else:
                return resources.path("images/thumb-default-video.png")

    @property
    def is_external(self):
        """Was this item downloaded by Miro, but not part of a feed?
        """
        if self.is_file_item:
            return self.has_parent
        else:
            return self.feed_url == 'dtv:manualFeed'

    @property
    def has_shareable_url(self):
        """Does this item have a URL that the user can share with
        others?

        This returns True when the item has a non-file URL.
        """
        return self.url != u'' and not self.url.startswith(u"file:")

    @property
    def size(self):
        """Get the size for an item.

        We try these methods in order to get the size:

        1. Physical size of a downloaded file
        2. HTTP content-length
        3. RSS enclosure tag value
        """
        if self.has_filename:
            try:
                return os.path.getsize(self.filename)
            except OSError:
                return None
        elif self.is_download:
            return self.downloader_size
        else:
            return self.enclosure_size

    @property
    def file_format(self):
        """Returns string with the format of the video.
        """
        if self.looks_like_torrent():
            return u'.torrent'

        if self.enclosure_format is not None:
            return self.enclosure_format

        return filetypes.calc_file_format(self.filename,
                                          self.downloader_content_type)

    @property
    def video_watched(self):
        return self.watched_time is not None

    @property
    def expiration_date(self):
        """When will this item expire?

        :returns: a datetime.datetime object or None if it doesn't expire.
        """
        if self.watched_time is None or not self.has_filename or self.keep:
            return None

        if self.feed_expire == u'never':
            return None
        elif self.feed_expire == u"feed":
            expire_time = feed_expire_time
        elif self.feed_expire == u"system":
            days = app.config.get(prefs.EXPIRE_AFTER_X_DAYS)
            if days <= 0:
                return None
            expire_time = datetime.timedelta(days=days)
        else:
            raise AssertionError("Unknown expire value: %s" % self.feed_expire)
        return self.watched_time + expire_time

    @property
    def expiration_date_text(self):
        return displaytext.expiration_date(self.expiration_date)

    @property
    def can_be_saved(self):
        return self.has_filename and not self.keep

    @property
    def is_download(self):
        return self.downloader_state in ('downloading', 'paused')

    @property
    def is_paused(self):
        return self.downloader_state == 'paused'

    @property
    def is_seeding(self):
        return self.downloader_state == 'uploading'

    @property
    def download_progress(self):
        """Calculate how for a download has progressed.

        :returns: [0.0, 1.0] depending on how much has been downloaded, or
        None if we don't have the info to make this calculation
        """
        if self.downloaded_size in (0, None):
            # Download hasn't started yet.  Give the downloader a little more
            # time before deciding that the eta is unknown.
            return 0.0
        if self.downloaded_size is None or self.downloader_size is None:
            # unknown total size, return None
            return None
        return float(self.downloaded_size) / self.downloader_size

    @property
    def download_rate_text(self):
        return displaytext.download_rate(self.rate)

    @property
    def upload_rate_text(self):
        return displaytext.download_rate(self.upload_rate)

    @property
    def upload_ratio(self):
        return float(self.upload_size) / self.downloaded_size

    @property
    def upload_ratio_text(self):
        return "%0.2f" % self.upload_ratio

    @property
    def eta_text(self):
        return displaytext.time_string_0_blank(self.eta)

    @property
    def downloaded_size_text(self):
        return displaytext.size_string(self.downloaded_size)

    @property
    def upload_size_text(self):
        return displaytext.size_string(self.upload_size)

    @property
    def is_failed_download(self):
        return self.downloader_state == 'failed'

    @property
    def pending_auto_dl(self):
        return (self.feed_auto_downloadable and
                not self.was_downloaded and
                self.feed_auto_downloadable and
                (self.feed_get_everything or self.eligible_for_autodownload))

    @property
    def title_sort_key(self):
        return util.name_sort_key(self.title)

    @property
    def artist_sort_key(self):
        return util.name_sort_key(self.artist)

    @property
    def album_sort_key(self):
        return util.name_sort_key(self.album)

    @property
    def has_parent(self):
        return self.parent_id is not None

    @property
    def parent_title_for_sort(self):
        """value to use for sorting by parent title.

        This will sort items by their parent title (torrent folder name or
        feed name, but if 2 torrents have the same name, or a torrent and a
        feed have the same name, then they will be separated)
        """
        return (self.parent_title, self.feed_id, self.parent_id)

    @property
    def album_artist_sort_key(self):
        if self.album_artist:
            return util.name_sort_key(self.album_artist)
        else:
            return self.artist_sort_key

    @property
    def description_oneline(self):
        return self.description_stripped[0].replace('\n', '$')

    @property
    def auto_rating(self):
        """Guess at a rating based on the number of times the files has been
        played vs. skipped and the item's age.
        """
        # TODO: we may want to take into consideration average ratings for this
        # artist and this album, total play count and skip counts, and average
        # manual rating
        SKIP_FACTOR = 1.5 # rating goes to 1 when user skips 40% of the time
        UNSKIPPED_FACTOR = 2 # rating goes to 5 when user plays 3 times without
                             # skipping
        # TODO: should divide by log of item's age
        if self.play_count > 0:
            if self.skip_count > 0:
                return min(5, max(1, int(self.play_count -
                    SKIP_FACTOR * self.skip_count)))
            else:
                return min(5, int(UNSKIPPED_FACTOR * self.play_count))
        elif self.skip_count > 0:
            return 1
        else:
            return None

    @property
    def duration(self):
        if self.duration_ms is None:
            return None
        else:
            return self.duration_ms // 1000

def fetch_item_infos(connection, item_ids):
    """Fetch a list of ItemInfos """
    columns = ','.join('%s.%s' % (c.table, c.column) for c in column_info())
    item_ids = ','.join(str(item_id) for item_id in item_ids)
    sql = ("SELECT %s FROM item %s WHERE item.id IN (%s)" %
           (columns, join_sql(), item_ids))
    return [ItemInfo(*row) for row in connection.execute(sql)]
