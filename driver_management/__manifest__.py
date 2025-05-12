{
    'name': 'driver_management',
    'version': '1.0',
    'summary': 'This is my first custom Odoo module',
    'description': 'Longer description if needed',
    'author': 'Your Name',
    'website': 'http://yourwebsite.com',
    'category': 'Uncategorized',
    'depends': ['base'],
    'data': [
        'security/driver_security.xml',
        'security/ir.model.access.csv',
        'views/driver_properties_views.xml',
        'views/res_partner_views.xml',
        'views/driver_menus.xml',

    ],
    'installable': True,
    'application': True,
}
