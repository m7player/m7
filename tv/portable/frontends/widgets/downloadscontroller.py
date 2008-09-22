# Miro - an RSS based video player application
# Copyright (C) 2005-2008 Participatory Culture Foundation
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

"""Controller for Downloads tab."""

from miro.gtcache import gettext as _

from miro.frontends.widgets import itemlistcontroller
from miro.frontends.widgets.itemlistwidgets import ItemView, HideableSection, ItemContainerWidget, DownloadStaticToolbar, DownloadDataToolbar, ItemListTitlebar
from miro.frontends.widgets import itemcontextmenu
from miro.frontends.widgets import imagepool
from miro.frontends.widgets import itemlist

from miro import messages
from miro import downloader
from miro.plat import resources

from miro.plat.utils import get_available_bytes_for_movies

class DownloadsController(itemlistcontroller.ItemListController):
    def __init__(self):
        itemlistcontroller.ItemListController.__init__(self, 'downloads', None)

    def build_widget(self):
        self._make_item_views()

        widget = ItemContainerWidget()
        widget.sort_bar.connect('sort-changed', self.on_sort_changed)

        widget.titlebar_vbox.pack_start(self.make_titlebar())

        self.static_toolbar = DownloadStaticToolbar()
        self.static_toolbar.connect("pause-all", self._on_pause_all)
        self.static_toolbar.connect("resume-all", self._on_resume_all)
        self.static_toolbar.connect("cancel-all", self._on_cancel_all)

        self.data_toolbar = DownloadDataToolbar()
        self._update_free_space()

        widget.titlebar_vbox.pack_start(self.static_toolbar)
        widget.titlebar_vbox.pack_start(self.data_toolbar)

        widget.content_vbox.pack_start(self.indydownloads_section)
        widget.content_vbox.pack_start(self.downloads_section)
        widget.content_vbox.pack_start(self.seeding_section)

        return widget

    def make_titlebar(self):
        image_path = resources.path("wimages/icon-downloading_large.png")
        icon = imagepool.get(image_path)
        titlebar = ItemListTitlebar(_("Downloads"), icon)
        titlebar.connect('search-changed', self._on_search_changed)
        return titlebar

    def make_context_menu_handler(self):
        return itemcontextmenu.ItemContextMenuHandler()

    def _make_item_views(self):
        self.indydownloads_view = ItemView(itemlist.IndividualDownloadItemList())
        self.indydownloads_section = HideableSection(_("Single and external downloads"), self.indydownloads_view)

        self.downloads_view = ItemView(itemlist.ChannelDownloadItemList())
        self.downloads_section = HideableSection(_("Channel downloads"), self.downloads_view)

        self.seeding_view = ItemView(itemlist.SeedingItemList())
        self.seeding_section = HideableSection(_("Seeding"), self.seeding_view)

    def all_item_views(self):
        return [self.indydownloads_view, self.downloads_view, self.seeding_view]

    def default_item_view(self):
        return self.downloads_view

    def _on_search_changed(self, widget, search_text):
        self.set_search(search_text)

    def _update_free_space(self):
        self.static_toolbar.update_free_space(get_available_bytes_for_movies())

    def _on_pause_all(self, widget):
        messages.PauseAllDownloads().send_to_backend()

    def _on_resume_all(self, widget):
        messages.ResumeAllDownloads().send_to_backend()

    def _on_cancel_all(self, widget):
        messages.CancelAllDownloads().send_to_backend()

    def _expand_lists_initially(self):
        self.indydownloads_section.show()
        self.downloads_section.show()
        self.seeding_section.show()

        self.indydownloads_section.expand()
        self.downloads_section.expand()
        self.seeding_section.expand()

    def on_initial_list(self):
        self._expand_lists_initially()

    def on_items_changed(self):
        self.data_toolbar.update_rates(downloader.totalDownRate, downloader.totalUpRate)
