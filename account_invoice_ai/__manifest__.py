# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice AI predict",
    "summary": """
        AI to train and predict invoices""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "external_dependencies": {"python": ["pypdf", "numpy", "tensorflow"]},
    "data": [
        "views/account_move.xml",
    ],
}
