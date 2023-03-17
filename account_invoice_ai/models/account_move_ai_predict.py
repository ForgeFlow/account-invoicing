# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
from collections import defaultdict

from pypdf import PdfReader

from odoo import _, models
from odoo.tools import float_compare
from odoo.tools.misc import format_amount
_logger = logging(__name__)


from odoo import models


class AccountMoveAiPredict(models.AbstractModel):
    """
    get the data from invoice attached and introduce to the tf model
    to predict and fill invoice fields
    """

    _name = "account.move.ai.predict"
    _description = "Account Move AI predict"

    def classify(self, word, classes):
        # Prediction or To Get the Posibility or Probability from the Model
        x_bow = bow(sentence, words, show_details=True))
        results = model.predict(x_bow)[0]
        # Exclude those results which are Below Threshold
        ERROR_THRESHOLD = 0.1
        results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
        # Sorting is Done because higher Confidence Answer comes first.
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append((classes[r[0]], r[1])) #Tuppl -> Intent and Probability
        return return_list


    def _ai_invoice_predict(self, attachment):
        encoded_data = attachment.datas
        base64.b64decode(encoded_data)
        attachment.store_fname
        real_path = attachment._full_path(attachment.store_fname)
        txt = ""
        reader = PdfReader(real_path)
        page = reader.pages[0]
        txt = page.extract_text()
        raise Warning(txt)
        _logger("Loading Pickle.....")        
        # TODO: put in a system parameter
        data = pickle.load(open( "training_data", "rb" ) )
        words = data['words']
        classes = data['classes']
        train_x = data['train_x']
        train_y = data['train_y']
        model.load('./model.tflearn')
        for word in txt:
            field_name = self.classify(word, classes)
            if field_name:
                _logger.info("completing %s with value" % field_name, word)


    def _update_invoice_from_attachment(self, attachment, invoice):
        invoice_data = self._ai_invoice_predict(attachment)

    def _get_invoice_company(self, invoice_data):
        if invoice_data["company"]:
            if invoice_data["company"].get("vat"):
                company = self.env["res.company"].search(
                    [("vat", "like", invoice_data["company"].get("vat"))]
                )
                if company:
                    return company
        return False

    def _get_invoice(self, invoice_data):
        """
        We want to maintain a hook because it might be interesting for
        contracts, an existent invoice in draft, with but not the number.
        """
        company = self._get_invoice_company(invoice_data) or self.env.company
        context = {}
        if invoice_data["context"]:
            context.update(invoice_data["context"])
        invoice = (
            self.env["account.move"]
            .with_company(company.id)
            .with_context(**context)
            .create({})
        )
        invoice.flush()
        return invoice
