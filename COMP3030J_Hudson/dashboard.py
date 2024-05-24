# myproject/dashboard.py

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name

class CustomIndexDashboard(Dashboard):
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # Add a link list module
        self.children.append(modules.LinkList(
            'Quick links',
            column=1,
            children=[
                {'title': 'Return to site', 'url': '/', 'external': False},
                {'title': 'Change password', 'url': '%s/password_change/' % site_name},
                {'title': 'Log out', 'url': '%s/logout/' % site_name},
            ]
        ))

        # Add an app list module
        self.children.append(modules.AppList(
            'Applications',
            column=1,
            exclude=('django.contrib.*',),
        ))

        # Add a model list module
        self.children.append(modules.ModelList(
            'Administration',
            column=1,
            models=('django.contrib.*',),
        ))

        # Append a recent actions module
        self.children.append(modules.RecentActions(
            'Recent Actions',
            limit=5,
            column=2,
        ))
